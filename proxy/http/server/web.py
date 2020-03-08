# -*- coding: utf-8 -*-
"""
    proxy.py
    ~~~~~~~~
    ⚡⚡⚡ Fast, Lightweight, Pluggable, TLS interception capable proxy server focused on
    Network monitoring, controls & Application development, testing, debugging.

    :copyright: (c) 2013-present by Abhinav Singh and contributors.
    :license: BSD, see LICENSE for more details.
"""
import gzip
import re
import time
import errno
import logging
import os
import mimetypes
import socket
from typing import List, Tuple, Optional, Dict, Union, Any, Pattern

from ...core.connection import TcpServerConnection
from .plugin import HttpWebServerBasePlugin
from .protocols import httpProtocolTypes
from ..exception import HttpProtocolException, ProxyConnectionFailed
from ..websocket import WebsocketFrame, websocketOpcodes
from ..codes import httpStatusCodes
from ..parser import HttpParser, httpParserStates, httpParserTypes
from ..handler import HttpProtocolHandlerPlugin

from ...common.utils import bytes_, text_, build_http_response, build_websocket_handshake_response
from ...common.constants import PROXY_AGENT_HEADER_VALUE
from ...common.types import HasFileno

logger = logging.getLogger(__name__)


class HttpWebServerPlugin(HttpProtocolHandlerPlugin):
    """HttpProtocolHandler plugin which handles incoming requests to local web server."""

    DEFAULT_404_RESPONSE = memoryview(build_http_response(
        httpStatusCodes.NOT_FOUND,
        reason=b'NOT FOUND',
        headers={b'Server': PROXY_AGENT_HEADER_VALUE,
                 b'Connection': b'close'}
    ))

    DEFAULT_501_RESPONSE = memoryview(build_http_response(
        httpStatusCodes.NOT_IMPLEMENTED,
        reason=b'NOT IMPLEMENTED',
        headers={b'Server': PROXY_AGENT_HEADER_VALUE,
                 b'Connection': b'close'}
    ))

    def __init__(
            self,
            *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.start_time: float = time.time()
        self.pipeline_request: Optional[HttpParser] = None
        self.switched_protocol: Optional[int] = None
        self.routes: Dict[int, Dict[Pattern[str], HttpWebServerBasePlugin]] = {
            httpProtocolTypes.HTTP: {},
            httpProtocolTypes.HTTPS: {},
            httpProtocolTypes.WEBSOCKET: {},
        }
        self.route: Optional[HttpWebServerBasePlugin] = None
        # TODO: Does it make sense to have more than one upstream destination for a single request? Guess not,
        #  as routes should be unique among web plugins
        self.server: Optional[TcpServerConnection] = None

        if b'HttpWebServerBasePlugin' in self.flags.plugins:
            for klass in self.flags.plugins[b'HttpWebServerBasePlugin']:
                instance = klass(
                    self.uid,
                    self.flags,
                    self.client,
                    self.event_queue,
                    self)
                for (protocol, route) in instance.routes():
                    self.routes[protocol][re.compile(route)] = instance

    @staticmethod
    def read_and_build_static_file_response(path: str) -> memoryview:
        with open(path, 'rb') as f:
            content = f.read()
        content_type = mimetypes.guess_type(path)[0]
        if content_type is None:
            content_type = 'text/plain'
        return memoryview(build_http_response(
            httpStatusCodes.OK,
            reason=b'OK',
            headers={
                b'Content-Type': bytes_(content_type),
                b'Cache-Control': b'max-age=86400',
                b'Content-Encoding': b'gzip',
                b'Connection': b'close',
            },
            body=gzip.compress(content)))

    def serve_file_or_404(self, path: str) -> bool:
        """Read and serves a file from disk.

        Queues 404 Not Found for IOError.
        Shouldn't this be server error?
        """
        try:
            self.client.queue(
                self.read_and_build_static_file_response(path))
        except IOError:
            self.client.queue(self.DEFAULT_404_RESPONSE)
        return True

    def try_upgrade(self) -> bool:
        if self.request.has_header(b'connection') and \
                self.request.header(b'connection').lower() == b'upgrade':
            if self.request.has_header(b'upgrade') and \
                    self.request.header(b'upgrade').lower() == b'websocket':
                self.client.queue(
                    memoryview(build_websocket_handshake_response(
                        WebsocketFrame.key_to_accept(
                            self.request.header(b'Sec-WebSocket-Key')))))
                self.switched_protocol = httpProtocolTypes.WEBSOCKET
            else:
                self.client.queue(self.DEFAULT_501_RESPONSE)
                return True
        return False

    def on_request_complete(self) -> Union[socket.socket, bool]:
        if self.request.has_upstream_server():
            return False

        assert self.request.path

        # If a websocket route exists for the path, try upgrade
        for route in self.routes[httpProtocolTypes.WEBSOCKET]:
            match = route.match(text_(self.request.path))
            if match:
                self.route = self.routes[httpProtocolTypes.WEBSOCKET][route]

                # Connection upgrade
                teardown = self.try_upgrade()
                if teardown:
                    return True

                # For upgraded connections, nothing more to do
                if self.switched_protocol:
                    # Invoke plugin.on_websocket_open
                    self.route.on_websocket_open()
                    return False

                break

        # Routing for Http(s) requests
        protocol = httpProtocolTypes.HTTPS \
            if self.flags.encryption_enabled() else \
            httpProtocolTypes.HTTP
        for route in self.routes[protocol]:
            match = route.match(text_(self.request.path))
            if match:
                self.route = self.routes[protocol][route]
                self.route.handle_request(self.request)
                return False

        # No-route found, try static serving if enabled
        if self.flags.enable_static_server:
            path = text_(self.request.path).split('?')[0]
            if os.path.isfile(self.flags.static_server_dir + path):
                return self.serve_file_or_404(
                    self.flags.static_server_dir + path)

        # Catch all unhandled web server requests, return 404
        self.client.queue(self.DEFAULT_404_RESPONSE)
        return True

    # TODO: Check how much is common between self and HttpProxyPlugin and consider extracting into
    #  HttpProtocolHandlerPlugin
    def write_to_descriptors(self, w: List[Union[int, HasFileno]]) -> bool:
        if self.server and not self.server.closed and \
                self.server.has_buffer() and \
                self.server.connection in w:
            logger.debug('Server is write ready, flushing buffer')
            try:
                self.server.flush()
            except OSError:
                logger.error('OSError when flushing buffer to server')
                return True
            except BrokenPipeError:
                logger.error(
                    'BrokenPipeError when flushing buffer for server')
                return True
        return False

    # TODO: Check how much is common between self and HttpProxyPlugin and consider extracting into
    #  HttpProtocolHandlerPlugin
    def read_from_descriptors(self, r: List[Union[int, HasFileno]]) -> bool:
        if self.server and not self.server.closed and self.server.connection in r:
            logger.debug('Server is ready for reads, reading...')
            try:
                raw = self.server.recv(self.flags.server_recvbuf_size)
            except TimeoutError as e:
                if e.errno == errno.ETIMEDOUT:
                    logger.warning(
                        '%s:%d timed out on recv' %
                        self.server.addr)
                    return True
                else:
                    raise e
            # TODO: not supporting SSL yet on reverse proxy case
            # except ssl.SSLWantReadError:    # Try again later
            #     # logger.warning('SSLWantReadError encountered while reading from server, will retry ...')
            #     return False
            except OSError as e:
                if e.errno == errno.EHOSTUNREACH:
                    logger.warning(
                        '%s:%d unreachable on recv' %
                        self.server.addr)
                    return True
                elif e.errno == errno.ECONNRESET:
                    logger.warning('Connection reset by upstream: %r' % e)
                else:
                    logger.exception(
                        'Exception while receiving from %s connection %r with reason %r' %
                        (self.server.tag, self.server.connection, e))
                return True

            if raw is None:
                logger.debug('Server closed connection, tearing down...')
                return True

            # TODO: is we want to do some processing on the response from upstream we should do it here
            #  maybe we should alter interface HttpWebServerBasePlugin to allow for that and add something
            #  like handle_upstream_chunk() for forward proxy use case
            # for plugin in self.plugins.values():
            #    raw = plugin.handle_upstream_chunk(raw)

            # parse incoming response packet
            # only for non-https requests and when
            # tls interception is enabled
            # if self.request.method != httpMethods.CONNECT:
            #     # See https://github.com/abhinavsingh/proxy.py/issues/127 for why
            #     # currently response parsing is disabled when TLS interception is enabled.
            #     #
            #     # or self.config.tls_interception_enabled():
            #     if self.response.state == httpParserStates.COMPLETE:
            #         self.handle_pipeline_response(raw)
            #     else:
            #         # TODO(abhinavsingh): Remove .tobytes after parser is
            #         # memoryview compliant
            #         self.response.parse(raw.tobytes())
            #         self.emit_response_events()
            # else:
            #     self.response.total_size += len(raw)
            # queue raw data for client
            self.client.queue(raw)
        return False

    def on_client_data(self, raw: memoryview) -> Optional[memoryview]:
        if self.switched_protocol == httpProtocolTypes.WEBSOCKET:
            # TODO(abhinavsingh): Remove .tobytes after websocket frame parser
            # is memoryview compliant
            remaining = raw.tobytes()
            frame = WebsocketFrame()
            while remaining != b'':
                # TODO: Teardown if invalid protocol exception
                remaining = frame.parse(remaining)
                if frame.opcode == websocketOpcodes.CONNECTION_CLOSE:
                    logger.warning(
                        'Client sent connection close packet')
                    raise HttpProtocolException()
                else:
                    assert self.route
                    self.route.on_websocket_message(frame)
                frame.reset()
            return None
        # If 1st valid request was completed and it's a HTTP/1.1 keep-alive
        # And only if we have a route, parse pipeline requests
        elif self.request.state == httpParserStates.COMPLETE and \
                self.request.is_http_1_1_keep_alive() and \
                self.route is not None:
            if self.pipeline_request is None:
                self.pipeline_request = HttpParser(
                    httpParserTypes.REQUEST_PARSER)
            # TODO(abhinavsingh): Remove .tobytes after parser is memoryview
            # compliant
            self.pipeline_request.parse(raw.tobytes())
            if self.pipeline_request.state == httpParserStates.COMPLETE:
                self.route.handle_request(self.pipeline_request)
                if not self.pipeline_request.is_http_1_1_keep_alive():
                    logger.error(
                        'Pipelined request is not keep-alive, will teardown request...')
                    raise HttpProtocolException()
                self.pipeline_request = None
        return raw

    def on_response_chunk(self, chunk: List[memoryview]) -> List[memoryview]:
        return chunk

    def on_client_connection_close(self) -> None:
        if self.request.has_upstream_server():
            return
        if self.switched_protocol:
            # Invoke plugin.on_websocket_close
            assert self.route
            self.route.on_websocket_close()
        self.access_log()

    def access_log(self) -> None:
        logger.info(
            '%s:%s - %s %s - %.2f ms' %
            (self.client.addr[0],
             self.client.addr[1],
             text_(self.request.method),
             text_(self.request.path),
             (time.time() - self.start_time) * 1000))

    #def add_descriptors(self, descriptors: Tuple[socket.socket, socket.socket]) -> None:
    #    if descriptors[0] is not None:
    #        self.read_desc.append(descriptors[0])
    #    if descriptors[1] is not None:
    #        self.write_desc.append(descriptors[1])

    def get_descriptors(self) -> Tuple[List[socket.socket], List[socket.socket]]:
        r: List[socket.socket] = []
        w: List[socket.socket] = []
        if self.server and not self.server.closed and self.server.connection:
            r.append(self.server.connection)
        if self.server and not self.server.closed and \
            self.server.has_buffer() and self.server.connection:
            w.append(self.server.connection)
        return r, w

    # Check if we are able to extract this to common ancestor
    def connect_upstream(self, host: str, port: int) -> TcpServerConnection:
        if host and port:
            self.server = TcpServerConnection(text_(host), port)
            try:
                logger.debug(
                    'Connecting to upstream %s:%s' %
                    (text_(host), port))
                self.server.connect()
                self.server.connection.setblocking(False)
                logger.debug(
                    'Connected to upstream %s:%s' %
                    (text_(host), port))
            except Exception as e:  # TimeoutError, socket.gaierror
                self.server.closed = True
                raise ProxyConnectionFailed(text_(host), port, repr(e)) from e
        else:
            logger.exception('Both host and port must exist')
            raise HttpProtocolException()
        return self.server
