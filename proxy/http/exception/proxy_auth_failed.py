# -*- coding: utf-8 -*-
"""
    proxy.py
    ~~~~~~~~
    ⚡⚡⚡ Fast, Lightweight, Pluggable, TLS interception capable proxy server focused on
    Network monitoring, controls & Application development, testing, debugging.

    :copyright: (c) 2013-present by Abhinav Singh and contributors.
    :license: BSD, see LICENSE for more details.

    .. spelling::

       auth
       http
"""
from typing import TYPE_CHECKING, Any

from .base import HttpProtocolException

from ..codes import httpStatusCodes

from ...common.constants import PROXY_AGENT_HEADER_VALUE, PROXY_AGENT_HEADER_KEY
from ...common.utils import build_http_response

if TYPE_CHECKING:
    from ..parser import HttpParser


class ProxyAuthenticationFailed(HttpProtocolException):
    """Exception raised when HTTP Proxy auth is enabled and
    incoming request doesn't present necessary credentials."""

    RESPONSE_PKT = memoryview(
        build_http_response(
            httpStatusCodes.PROXY_AUTH_REQUIRED,
            reason=b'Proxy Authentication Required',
            headers={
                PROXY_AGENT_HEADER_KEY: PROXY_AGENT_HEADER_VALUE,
                b'Proxy-Authenticate': b'Basic',
            },
            body=b'Proxy Authentication Required',
            conn_close=True,
        ),
    )

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(self.__class__.__name__, **kwargs)

    def response(self, _request: 'HttpParser') -> memoryview:
        return self.RESPONSE_PKT
