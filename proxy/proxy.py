# -*- coding: utf-8 -*-
"""
    proxy.py
    ~~~~~~~~
    ⚡⚡⚡ Fast, Lightweight, Pluggable, TLS interception capable proxy server focused on
    Network monitoring, controls & Application development, testing, debugging.

    :copyright: (c) 2013-present by Abhinav Singh and contributors.
    :license: BSD, see LICENSE for more details.
"""
import os
import sys
import time
import logging

from types import TracebackType
from typing import List, Optional, Any, Type

from proxy.core.acceptor.work import Work

from .common.utils import bytes_
from .core.acceptor import AcceptorPool
from .http.handler import HttpProtocolHandler
from .core.event import EventManager
from .common.flag import FlagParser, flags
from .common.constants import DEFAULT_LOG_FILE, DEFAULT_LOG_FORMAT, DEFAULT_LOG_LEVEL
from .common.constants import DEFAULT_OPEN_FILE_LIMIT, DEFAULT_PLUGINS, DEFAULT_VERSION
from .common.constants import DEFAULT_ENABLE_DASHBOARD


logger = logging.getLogger(__name__)


flags.add_argument(
    '--version',
    '-v',
    action='store_true',
    default=DEFAULT_VERSION,
    help='Prints proxy.py version.',
)

flags.add_argument(
    '--log-level',
    type=str,
    default=DEFAULT_LOG_LEVEL,
    help='Valid options: DEBUG, INFO (default), WARNING, ERROR, CRITICAL. '
    'Both upper and lowercase values are allowed. '
    'You may also simply use the leading character e.g. --log-level d',
)

flags.add_argument(
    '--log-file',
    type=str,
    default=DEFAULT_LOG_FILE,
    help='Default: sys.stdout. Log file destination.',
)

flags.add_argument(
    '--log-format',
    type=str,
    default=DEFAULT_LOG_FORMAT,
    help='Log format for Python logger.',
)

flags.add_argument(
    '--open-file-limit',
    type=int,
    default=DEFAULT_OPEN_FILE_LIMIT,
    help='Default: 1024. Maximum number of files (TCP connections) '
    'that proxy.py can open concurrently.',
)

flags.add_argument(
    '--plugins',
    type=str,
    default=DEFAULT_PLUGINS,
    help='Comma separated plugins',
)

# TODO: Ideally all `--enable-*` flags must be at the top-level.
# --enable-dashboard is specially needed here because
# ProxyDashboard class is not imported by anyone.
#
# If we move this flag definition within dashboard.py,
# users will also have to explicitly enable dashboard plugin
# to also use flags provided by it.
flags.add_argument(
    '--enable-dashboard',
    action='store_true',
    default=DEFAULT_ENABLE_DASHBOARD,
    help='Default: False.  Enables proxy.py dashboard.',
)


class Proxy:
    """Context manager to control core AcceptorPool server lifecycle.

    By default, AcceptorPool is started with HttpProtocolHandler worker class
    i.e. we are only expecting HTTP traffic to flow between clients and server.

    Optionally, also initialize a global event queue.
    It is a multiprocess safe queue which can be used to
    build pubsub patterns for message sharing or signaling
    within the running proxy environment.
    """

    def __init__(self, input_args: Optional[List[str]], **opts: Any) -> None:
        self.flags = FlagParser.initialize(input_args, **opts)
        self.pool: Optional[AcceptorPool] = None
        # TODO(abhinavsingh): Allow users to override the worker class itself
        # e.g. A clear text protocol. Or imagine a TelnetProtocolHandler instead
        # of default HttpProtocolHandler.
        self.work_klass: Type[Work] = HttpProtocolHandler
        self.event_manager: Optional[EventManager] = None

    def write_pid_file(self) -> None:
        if self.flags.pid_file is not None:
            # TODO(abhinavsingh): Multiple instances of proxy.py running on
            # same host machine will currently result in overwriting the PID file
            with open(self.flags.pid_file, 'wb') as pid_file:
                pid_file.write(bytes_(os.getpid()))

    def delete_pid_file(self) -> None:
        if self.flags.pid_file and os.path.exists(self.flags.pid_file):
            os.remove(self.flags.pid_file)

    def __enter__(self) -> 'Proxy':
        if self.flags.enable_events:
            logger.info('Core Event enabled')
            self.event_manager = EventManager()
            self.event_manager.start_event_dispatcher()
        self.pool = AcceptorPool(
            flags=self.flags,
            work_klass=self.work_klass,
            event_queue=self.event_manager.event_queue if self.event_manager is not None else None,
        )
        self.pool.setup()
        self.write_pid_file()
        return self

    def __exit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc_val: Optional[BaseException],
            exc_tb: Optional[TracebackType],
    ) -> None:
        assert self.pool
        self.pool.shutdown()
        if self.flags.enable_events:
            assert self.event_manager is not None
            self.event_manager.stop_event_dispatcher()
        self.delete_pid_file()


def main(
        input_args: Optional[List[str]] = None,
        **opts: Any,
) -> None:
    try:
        with Proxy(input_args=input_args, **opts) as proxy:
            assert proxy.pool is not None
            if proxy.flags.unix_socket_path:
                logger.info(
                    'Listening on %s' %
                    (proxy.flags.unix_socket_path),
                )
            else:
                logger.info(
                    'Listening on %s:%s' %
                    (proxy.pool.flags.hostname, proxy.pool.flags.port),
                )
            # TODO: Introduce cron feature
            # https://github.com/abhinavsingh/proxy.py/issues/392
            #
            # TODO: Introduce ability to publish
            # adhoc events which can modify behaviour of server
            # at runtime.  Example, updating flags, plugin
            # configuration etc.
            #
            # TODO: Python shell within running proxy.py environment?
            #
            # TODO: Pid watcher which watches for processes started
            # by proxy.py core.  May be alert or restart those processes
            # on failure.
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        pass


def entry_point() -> None:
    main(input_args=sys.argv[1:])
