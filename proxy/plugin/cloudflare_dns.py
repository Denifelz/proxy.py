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

try:
    import httpx
except ImportError:
    pass

from typing import Optional, Tuple

from ..common.flag import flags
from ..http.parser import HttpParser
from ..http.proxy import HttpProxyBasePlugin

logger = logging.getLogger(__name__)


flags.add_argument(
    '--cloudflare-dns-mode',
    type=str,
    default='security',
    help='Default: security.  Either "security" (for malware protection) ' +
    'or "family" (for malware and adult content protection)',
)


class CloudflareDnsResolverPlugin(HttpProxyBasePlugin):
    """This plugin uses Cloudflare DNS resolver to provide protection
    against malwares and adult content.  Implementation uses DoH specification.

    See https://developers.cloudflare.com/1.1.1.1/1.1.1.1-for-families
    See https://developers.cloudflare.com/1.1.1.1/encrypted-dns/dns-over-https/make-api-requests/dns-json

    NOTE: For this plugin to work, make sure to bypass proxy for 1.1.1.1

    NOTE: This plugin requires additional dependency because DoH mandates
    a HTTP2 complaint client.  Install `httpx` dependency as:

    pip install "httpx[http2]"
    """

    def resolve_dns(self, host: str, port: int) -> Tuple[Optional[str], Optional[Tuple[str, int]]]:
        try:
            context = httpx.create_ssl_context(http2=True)
            # TODO: Support resolution via Authority (SOA) to add support for
            # AAAA (IPv6) query
            r = httpx.get(
                'https://{0}.cloudflare-dns.com/dns-query?name={1}&type=A'.format(
                    self.flags.cloudflare_dns_mode, host,
                ),
                headers={'accept': 'application/dns-json'},
                verify=context,
                timeout=httpx.Timeout(timeout=5.0),
                proxies={
                    'all://': None,
                },
            )
            if r.status_code != 200:
                return None, None
            response = r.json()
            answers = response.get('Answer', [])
            if len(answers) == 0:
                return None, None
            # TODO: Utilize TTL to cache response locally
            # instead of making a DNS query repeatedly for the same host.
            return answers[0]['data'], None
        except Exception as e:
            logger.exception('Unable to resolve DNS-over-HTTPS', exc_info=e)
            return None, None

    def before_upstream_connection(
            self, request: HttpParser,
    ) -> Optional[HttpParser]:
        return request

    def handle_client_request(
            self, request: HttpParser,
    ) -> Optional[HttpParser]:
        return request

    def handle_upstream_chunk(self, chunk: memoryview) -> memoryview:
        return chunk

    def on_upstream_connection_close(self) -> None:
        pass
