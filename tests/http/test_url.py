# -*- coding: utf-8 -*-
"""
    proxy.py
    ~~~~~~~~
    ⚡⚡⚡ Fast, Lightweight, Pluggable, TLS interception capable proxy server focused on
    Network monitoring, controls & Application development, testing, debugging.

    :copyright: (c) 2013-present by Abhinav Singh and contributors.
    :license: BSD, see LICENSE for more details.
"""
import unittest

from proxy.http.url import Url


class TestUrl(unittest.TestCase):

    def test_web_server_url(self) -> None:
        url = Url.from_bytes(b'/')
        self.assertEqual(url.scheme, None)
        self.assertEqual(url.hostname, None)
        self.assertEqual(url.port, None)
        self.assertEqual(url.remainder, b'/')

    def test_http_proxy_url(self) -> None:
        url = Url.from_bytes(b'http://httpbin.org/get')
        self.assertEqual(url.scheme, b'http')
        self.assertEqual(url.hostname, b'httpbin.org')
        self.assertEqual(url.port, None)
        self.assertEqual(url.remainder, b'/get')

    def test_https_connect_url(self) -> None:
        url = Url.from_bytes(b'httpbin.org:443')
        self.assertEqual(url.scheme, None)
        self.assertEqual(url.hostname, b'httpbin.org')
        self.assertEqual(url.port, 443)
        self.assertEqual(url.remainder, None)

    def test_https_connect_with_ipv6_url(self) -> None:
        url = Url.from_bytes(b'[::]:443')
        self.assertEqual(url.scheme, None)
        self.assertEqual(url.hostname, b'[::]')
        self.assertEqual(url.port, 443)
        self.assertEqual(url.remainder, None)

    def test_https_connect_with_ipv6_malformed_url(self) -> None:
        url = Url.from_bytes(b':::443')
        self.assertEqual(url.scheme, None)
        self.assertEqual(url.hostname, b'[::]')
        self.assertEqual(url.port, 443)
        self.assertEqual(url.remainder, None)

    def test_unicode_url(self) -> None:
        url = Url.from_bytes('å∫ç.com'.encode('utf-8'))
        self.assertEqual(url.scheme, None)
        self.assertEqual(url.hostname, 'å∫ç.com'.encode('utf-8'))
        self.assertEqual(url.port, None)
        self.assertEqual(url.remainder, None)

    def test_full_url(self) -> None:
        url = Url.from_bytes(b'https://example.com/path/dir/?a=b&c=d#p=q')
        self.assertEqual(url.scheme, b'https')
        self.assertEqual(url.hostname, b'example.com')
        self.assertEqual(url.port, None)
        self.assertEqual(url.remainder, b'/path/dir/?a=b&c=d#p=q')

    def test_no_trailing_slash_url(self) -> None:
        url = Url.from_bytes(b'http://localhost:12345')
        self.assertEqual(url.scheme, b'http')
        self.assertEqual(url.hostname, b'localhost')
        self.assertEqual(url.port, 12345)
        self.assertEqual(url.remainder, None)

    def test_trailing_slash_url(self) -> None:
        url = Url.from_bytes(b'http://localhost:12345/v1/users/')
        self.assertEqual(url.scheme, b'http')
        self.assertEqual(url.hostname, b'localhost')
        self.assertEqual(url.port, 12345)
        self.assertEqual(url.remainder, b'/v1/users/')
