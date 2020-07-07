# -*- coding: utf-8 -*-
"""
    proxy.py
    ~~~~~~~~
    ⚡⚡⚡ Fast, Lightweight, Pluggable, TLS interception capable proxy server focused on
    Network monitoring, controls & Application development, testing, debugging.

    :copyright: (c) 2013-present by Abhinav Singh and contributors.
    :license: BSD, see LICENSE for more details.
"""

import logging

from typing import Optional

from ..http.exception import HttpRequestRejected
from ..http.parser import HttpParser
from ..http.codes import httpStatusCodes
from ..http.proxy import HttpProxyBasePlugin

import re

logger = logging.getLogger(__name__)

class FilterByURLRegexPlugin(HttpProxyBasePlugin):
    """
        Drop traffic by inspecting request URL, 
        checking against a list of regular expressions, 
        then returning a HTTP status code.
    """

    FILTER_LIST = [
        {
            b'regex': b'https{0,1}://tpc.googlesyndication.com:\d{1,5}/simgad/.*',
            b'status_code': 444,
            b'notes': b'Google image ads',
        },
    ]

    def before_upstream_connection(
            self, request: HttpParser) -> Optional[HttpParser]:
        return request

    def handle_client_request(
            self, request: HttpParser) -> Optional[HttpParser]:

        logger.info('----------')
        logger.info(request.host)
        logger.info(request.url)
        logger.info(request.headers)
        logger.info(request.header('host'))
        logger.info(request.path)
        logger.info(request.port)

        # request_host = None
        # if request.host:
        #     host = request.host
        # else:
        #     if request.headers

        # # build URL
        # url = b'http://%s:%d%s' % (
        #     request.host or request.headers['host'][1], 
        #     request.port,
        #     request.path,
        # )

        # logger.info(url)

        logger.info('----------')

        # # check URL against list
        # rule_number = 1
        # for blocked_entry in self.FILTER_LIST:

        #     # if regex matches on URL
        #     if re.search(blocked_entry[b'regex'], url):

        #         # log that the request has been filtered
        #         logger.info(b"Blocked: '%s' with status_code '%s' by rule number '%s'" % (
        #             url,
        #             blocked_entry[b'status_code'],
        #             rule_number,
        #             )
        #         )

        #         raise HttpRequestRejected(
        #             status_code = blocked_entry[b'status_code'],
        #             headers = {b'Connection': b'close'},
        #         )

        #         break

        #     rule_number += 1 

        return request

    def handle_upstream_chunk(self, chunk: memoryview) -> memoryview:
        return chunk

    def on_upstream_connection_close(self) -> None:
        pass
