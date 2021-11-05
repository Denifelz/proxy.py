# -*- coding: utf-8 -*-
"""
    proxy.py
    ~~~~~~~~
    ⚡⚡⚡ Fast, Lightweight, Pluggable, TLS interception capable proxy server focused on
    Network monitoring, controls & Application development, testing, debugging.

    :copyright: (c) 2013-present by Abhinav Singh and contributors.
    :license: BSD, see LICENSE for more details.
"""
import argparse
import logging
import multiprocessing
import socket

from multiprocessing import connection
from types import TracebackType
from multiprocessing.reduction import send_handle
from typing import List, Optional, Type

from .acceptor import Acceptor
from .work import Work

from ..event import EventQueue

from ...common.flag import flags
from ...common.constants import DEFAULT_BACKLOG, DEFAULT_IPV6_HOSTNAME, DEFAULT_NUM_WORKERS, DEFAULT_PORT

logger = logging.getLogger(__name__)

# Lock shared by worker processes
LOCK = multiprocessing.Lock()


flags.add_argument(
    '--backlog',
    type=int,
    default=DEFAULT_BACKLOG,
    help='Default: 100. Maximum number of pending connections to proxy server',
)

flags.add_argument(
    '--hostname',
    type=str,
    default=str(DEFAULT_IPV6_HOSTNAME),
    help='Default: ::1. Server IP address.',
)

flags.add_argument(
    '--port', type=int, default=DEFAULT_PORT,
    help='Default: 8899. Server port.',
)

flags.add_argument(
    '--num-workers',
    type=int,
    default=DEFAULT_NUM_WORKERS,
    help='Defaults to number of CPU cores.',
)


class AcceptorPool:
    """AcceptorPool pre-spawns worker processes to utilize all cores available on the system.
    A server socket is initialized and dispatched over a pipe to these workers.
    Each worker process then concurrently accepts new client connection over
    the initialized server socket.

    Example usage:

        pool = AcceptorPool(flags=..., work_klass=...)
        try:
            pool.setup()
            while True:
                time.sleep(1)
        finally:
            pool.shutdown()

    `work_klass` must implement `work.Work` class.
    """

    def __init__(
        self, flags: argparse.Namespace,
        work_klass: Type[Work], event_queue: Optional[EventQueue] = None,
    ) -> None:
        self.flags = flags
        self.socket: Optional[socket.socket] = None
        self.acceptors: List[Acceptor] = []
        self.work_queues: List[connection.Connection] = []
        self.work_klass = work_klass
        self.event_queue: Optional[EventQueue] = event_queue

    def __enter__(self) -> 'AcceptorPool':
        self.setup()
        return self

    def __exit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc_val: Optional[BaseException],
            exc_tb: Optional[TracebackType],
    ) -> None:
        self.shutdown()

    def listen(self) -> None:
        self.socket = socket.socket(self.flags.family, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((str(self.flags.hostname), self.flags.port))
        self.socket.listen(self.flags.backlog)
        self.socket.setblocking(False)
        # Override flags.port to match the actual port
        # we are listening upon.  This is necessary to preserve
        # the server port when `--port=0` is used.
        self.flags.port = self.socket.getsockname()[1]

    def start_workers(self) -> None:
        """Start worker processes."""
        for acceptor_id in range(self.flags.num_workers):
            work_queue = multiprocessing.Pipe()
            acceptor = Acceptor(
                idd=acceptor_id,
                work_queue=work_queue[1],
                flags=self.flags,
                work_klass=self.work_klass,
                lock=LOCK,
                event_queue=self.event_queue,
            )
            acceptor.start()
            logger.debug(
                'Started acceptor#%d process %d',
                acceptor_id,
                acceptor.pid,
            )
            self.acceptors.append(acceptor)
            self.work_queues.append(work_queue[0])
        logger.info('Started %d workers' % self.flags.num_workers)

    def shutdown(self) -> None:
        logger.info('Shutting down %d workers' % self.flags.num_workers)
        for acceptor in self.acceptors:
            acceptor.running.set()
        for acceptor in self.acceptors:
            acceptor.join()
        logger.debug('Acceptors shutdown')

    def setup(self) -> None:
        """Listen on port, setup workers and pass server socket to workers."""
        self.listen()
        self.start_workers()
        # Send server socket to all acceptor processes.
        assert self.socket is not None
        for index in range(self.flags.num_workers):
            send_handle(
                self.work_queues[index],
                self.socket.fileno(),
                self.acceptors[index].pid,
            )
            self.work_queues[index].close()
        self.socket.close()
