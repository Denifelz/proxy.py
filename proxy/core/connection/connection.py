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
from abc import ABC, abstractmethod
from typing import List, Union, Optional

from .types import tcpConnectionTypes
from ...common.types import TcpOrTlsSocket
from ...common.leakage import Leakage
from ...common.constants import DEFAULT_BUFFER_SIZE, DEFAULT_MAX_SEND_SIZE


logger = logging.getLogger(__name__)

EMPTY_MV = memoryview(b'')

class TcpConnectionUninitializedException(Exception):
    pass


class TcpConnection(ABC):
    """TCP server/client connection abstraction.

    Main motivation of this class is to provide a buffer management
    when reading and writing into the socket.

    Implement the connection property abstract method to return
    a socket connection object.
    """

    def __init__(
        self,
        tag: int,
        flush_bps: int = 512,
        recv_bps: int = 512,
    ) -> None:
        self.tag: str = 'server' if tag == tcpConnectionTypes.SERVER else 'client'
        self.buffer: List[memoryview] = []
        self.closed: bool = False
        self._reusable: bool = False
        self._num_buffer = 0
        self._flush_leakage = Leakage(rate=flush_bps) if flush_bps > 0 else None
        self._recv_leakage = Leakage(rate=recv_bps) if recv_bps > 0 else None

    @property
    @abstractmethod
    def connection(self) -> TcpOrTlsSocket:
        """Must return the socket connection to use in this class."""
        raise TcpConnectionUninitializedException()     # pragma: no cover

    def send(self, data: Union[memoryview, bytes]) -> int:
        """Users must handle BrokenPipeError exceptions"""
        return self.connection.send(data)

    def recv(
            self, buffer_size: int = DEFAULT_BUFFER_SIZE,
    ) -> Optional[memoryview]:
        """Users must handle socket.error exceptions"""
        if self._recv_leakage is not None:
            allowed_bytes = self._recv_leakage.consume(buffer_size)
            if allowed_bytes == 0:
                return EMPTY_MV
            buffer_size = min(buffer_size, allowed_bytes)
        data: bytes = self.connection.recv(buffer_size)
        size = len(data)
        unused = buffer_size - size
        if self._recv_leakage is not None and unused > 0:
            self._recv_leakage.release(unused)
        if size == 0:
            return None
        logger.debug('received %d bytes from %s' % (size, self.tag))
        logger.info(data)
        return memoryview(data)

    def close(self) -> bool:
        if not self.closed and self.connection:
            self.connection.close()
            self.closed = True
        return self.closed

    def has_buffer(self) -> bool:
        return self._num_buffer != 0

    def queue(self, mv: memoryview) -> None:
        if len(mv) == 0:
            return
        self.buffer.append(mv)
        self._num_buffer += 1

    def flush(self, max_send_size: Optional[int] = None) -> int:
        """Users must handle BrokenPipeError exceptions"""
        if not self.has_buffer():
            return 0
        mv = self.buffer[0]
        # TODO: Assemble multiple packets if total
        # size remains below max send size.
        max_send_size = max_send_size or DEFAULT_MAX_SEND_SIZE
        allowed_bytes = (
            self._flush_leakage.consume(min(len(mv), max_send_size))
            if self._flush_leakage is not None
            else max_send_size
        )
        sent: int = 0
        if allowed_bytes > 0:
            try:
                sent = self.send(mv[:allowed_bytes])
            except BlockingIOError:
                logger.warning(
                    'BlockingIOError when trying send to {0}'.format(self.tag),
                )
                del mv
                return 0
            finally:
                unused = allowed_bytes - sent
                if self._flush_leakage is not None and unused > 0:
                    self._flush_leakage.release(unused)
        if sent == len(mv):
            self.buffer.pop(0)
            self._num_buffer -= 1
        else:
            self.buffer[0] = mv[sent:]
        logger.debug('flushed %d bytes to %s' % (sent, self.tag))
        logger.info(mv[:sent].tobytes())
        del mv
        return sent

    def is_reusable(self) -> bool:
        return self._reusable

    def mark_inuse(self) -> None:
        self._reusable = False

    def reset(self) -> None:
        assert not self.closed
        self._reusable = True
        self.buffer = []
        self._num_buffer = 0
