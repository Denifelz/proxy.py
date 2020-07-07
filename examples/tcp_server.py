# -*- coding: utf-8 -*-
"""
    proxy.py
    ~~~~~~~~
    ⚡⚡⚡ Fast, Lightweight, Pluggable, TLS interception capable proxy server focused on
    Network monitoring, controls & Application development, testing, debugging.

    :copyright: (c) 2013-present by Abhinav Singh and contributors.
    :license: BSD, see LICENSE for more details.
"""
import time
import socket
import selectors

from typing import Dict, List, Union

from proxy.core.acceptor import AcceptorPool, ThreadlessWork
from proxy.common.flags import Flags
from proxy.common.types import HasFileno


class EchoClient(ThreadlessWork):

    def initialize(self) -> None:
        self.client.connection.setblocking(False)

    def is_inactive(self) -> bool:
        return False

    def get_events(self) -> Dict[socket.socket, int]:
        events: Dict[socket.socket, int] = {
            self.client.connection: selectors.EVENT_READ
        }
        if self.client.has_buffer():
            events[self.client.connection] |= selectors.EVENT_WRITE
        return events

    def handle_events(
            self,
            readables: List[Union[int, HasFileno]],
            writables: List[Union[int, HasFileno]]) -> bool:
        """Return True to shutdown work."""
        if self.client.connection in readables:
            data = self.client.recv()
            if data is None:
                # Signal shutdown of connection
                return True
            # Send back data to client
            self.client.queue(data)

        if self.client.connection in writables:
            self.client.flush()

        return False

    def run(self) -> None:
        print('run')


def main() -> None:
    pool = AcceptorPool(
        flags=Flags(num_workers=1, threadless=True),
        work_klass=EchoClient)
    try:
        pool.setup()
        while True:
            time.sleep(1)
    finally:
        pool.shutdown()


if __name__ == '__main__':
    main()
