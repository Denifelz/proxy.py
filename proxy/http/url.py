# -*- coding: utf-8 -*-
"""
    proxy.py
    ~~~~~~~~
    ⚡⚡⚡ Fast, Lightweight, Pluggable, TLS interception capable proxy server focused on
    Network monitoring, controls & Application development, testing, debugging.

    :copyright: (c) 2013-present by Abhinav Singh and contributors.
    :license: BSD, see LICENSE for more details.
"""
from typing import Optional, Tuple

from ..common.constants import COLON, SLASH


class Url:
    """urllib.urlparse doesn't work for proxy.py, so we wrote a simple Url.

    Currently, Url only implements what is necessary for HttpParser to work.
    """

    def __init__(
            self,
            scheme: Optional[bytes] = None,
            host: Optional[bytes] = None,
            port: Optional[int] = None,
            remainder: Optional[bytes] = None,
    ) -> None:
        self.scheme: Optional[bytes] = scheme
        self.hostname: Optional[bytes] = host
        self.port: Optional[int] = port
        self.remainder: Optional[bytes] = remainder

    @classmethod
    def from_bytes(cls, raw: bytes) -> 'Url':
        """A Url within proxy.py core can have several styles,
        because proxy.py supports both proxy and web server use cases.

        Example:
        For a Web server, url is like "/" or "/get" or "/get?key=value"
        For a HTTPS connect tunnel, url is like "httpbin.org:443"
        For a HTTP proxy request, url is like "http://httpbin.org/get"

        Further:
        1) Url may contain unicode characters
        2) Url may contain IPv4 and IPv6 format addresses instead of domain names

        We use heuristics based approach for our Url parser.
        """
        sraw = raw.decode('utf-8')
        if sraw[0] == SLASH.decode('utf-8'):
            return cls(remainder=raw)
        if sraw.startswith('https://') or sraw.startswith('http://'):
            is_https = sraw.startswith('https://')
            rest = raw[len(b'https://'):] if is_https else raw[len(b'http://'):]
            parts = rest.split(SLASH)
            host, port = Url.parse_host_and_port(parts[0])
            return cls(
                scheme=b'https' if is_https else b'http',
                host=host,
                port=port,
                remainder=None if len(parts) == 1 else (
                    SLASH + SLASH.join(parts[1:])
                ),
            )
        host, port = Url.parse_host_and_port(raw)
        return cls(host=host, port=port)

    @staticmethod
    def parse_host_and_port(raw: bytes) -> Tuple[bytes, Optional[int]]:
        parts = raw.split(COLON)
        if len(parts) == 1:
            return parts[0], None
        if len(parts) == 2:
            host, port = COLON.join(parts[:-1]), int(parts[-1])
        if len(parts) > 2:
            try:
                port = int(parts[-1])
                host = COLON.join(parts[:-1])
            except ValueError:
                # If unable to convert last part into port,
                # this is the IPv6 scenario.  Treat entire
                # data as host
                host, port = raw, None
        # patch up invalid ipv6 scenario
        rhost = host.decode('utf-8')
        if COLON.decode('utf-8') in rhost and rhost[0] != '[' and rhost[-1] != ']':
            host = b'[' + host + b']'
        return host, port
