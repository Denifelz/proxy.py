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
            'regex': b'tpc.googlesyndication.com/simgad/.*',
            'status_code': 444,
            'notes': 'Google image ads',
        },
        {
            'regex': b'tpc.googlesyndication.com/sadbundle/.*',
            'status_code': 444,
            'notes': 'Google animated ad bundles',
        },
        {
            'regex': b'pagead\d+.googlesyndication.com/.*',
            'status_code': 444,
            'notes': 'Google tracking',
        },
        {
            'regex': b'(www){0,1}.google-analytics.com/r/collect\?.*',
            'status_code': 444,
            'notes': 'Google tracking',
        },
        {
            'regex': b'(www){0,1}.facebook.com/tr/.*',
            'status_code': 444,
            'notes': 'Facebook tracking',
        },
        {
            'regex': b'tpc.googlesyndication.com/daca_images/simgad/.*',
            'status_code': 444,
            'notes': 'Google image ads',
        },
        {
            'regex': b'.*.2mdn.net/videoplayback/.*.mp4',
            'status_code': 444,
            'notes': 'Twitch.tv video ads',
        },
        {
            'regex': b'(www.){0,1}google.com(.*)/pagead/.*',
            'status_code': 444,
            'notes': 'Google ads',
        }
    ]

    def before_upstream_connection(
            self, request: HttpParser) -> Optional[HttpParser]:
        return request

    def handle_client_request(
            self, request: HttpParser) -> Optional[HttpParser]:

        # determine host
        request_host = None
        if request.host:
            request_host = request.host
        else:
            if b'host' in request.headers:
                request_host = request.header(b'host')

        if not request_host:
            logger.error("Cannot determine host")
            return request

        # build URL
        url = b'%s%s' % (
            request_host, 
            request.path,
        )

        # check URL against list
        rule_number = 1
        for blocked_entry in self.FILTER_LIST:

            # if regex matches on URL
            if re.search(blocked_entry['regex'], url):

                # log that the request has been filtered
                logger.info("Blocked: '%s' with status_code '%i' by rule number '%i'" % (
                    url,
                    blocked_entry['status_code'],
                    rule_number,
                    )
                )

                raise HttpRequestRejected(
                    status_code = blocked_entry['status_code'],
                    headers = {b'Connection': b'close'},
                )

                break

            rule_number += 1 

        return request

    def handle_upstream_chunk(self, chunk: memoryview) -> memoryview:
        return chunk

    def on_upstream_connection_close(self) -> None:
        pass
