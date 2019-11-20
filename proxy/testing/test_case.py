# -*- coding: utf-8 -*-
"""
    proxy.py
    ~~~~~~~~
    ⚡⚡⚡ Fast, Lightweight, Programmable Proxy Server in a single Python file.

    :copyright: (c) 2013-present by Abhinav Singh and contributors.
    :license: BSD, see LICENSE for more details.
"""
import contextlib
import time
import unittest
from typing import Optional, List, Generator, Any

from ..proxy import Proxy
from ..common.utils import get_available_port, new_socket_connection


class TestCase(unittest.TestCase):
    """Base TestCase class that automatically setup and teardown proxy.py."""

    DEFAULT_PROXY_PY_STARTUP_FLAGS = [
        '--num-workers', '1',
        '--threadless',
    ]

    PROXY_PORT: int = 8899
    PROXY: Optional[Proxy] = None
    INPUT_ARGS: Optional[List[str]] = None
    ENABLE_VCR: bool = False

    @classmethod
    def setUpClass(cls) -> None:
        cls.PROXY_PORT = get_available_port()
        cls.INPUT_ARGS = getattr(cls, 'PROXY_PY_STARTUP_FLAGS') \
            if hasattr(cls, 'PROXY_PY_STARTUP_FLAGS') \
            else cls.DEFAULT_PROXY_PY_STARTUP_FLAGS
        cls.INPUT_ARGS.append('--port')
        cls.INPUT_ARGS.append(str(cls.PROXY_PORT))
        cls.PROXY = Proxy(input_args=cls.INPUT_ARGS)
        cls.PROXY.__enter__()
        cls.wait_for_server(cls.PROXY_PORT)

    @staticmethod
    def wait_for_server(proxy_port: int) -> None:
        """Wait for proxy.py server to come up."""
        while True:
            try:
                conn = new_socket_connection(
                    ('localhost', proxy_port))
                conn.close()
                break
            except ConnectionRefusedError:
                time.sleep(0.1)

    @classmethod
    def tearDownClass(cls) -> None:
        assert cls.PROXY
        cls.PROXY.__exit__(None, None, None)
        cls.PROXY_PORT = 8899
        cls.PROXY = None
        cls.INPUT_ARGS = None
        cls.ENABLE_VCR = False

    @contextlib.contextmanager
    def vcr(self) -> Generator[None, None, None]:
        self.ENABLE_VCR = True
        try:
            yield
        finally:
            self.ENABLE_VCR = False

    def run(self, result: Optional[unittest.TestResult] = None) -> Any:
        super().run(result)
