# -*- coding: utf-8 -*-
#
# proxy.py
# ~~~~~~~~
# ⚡ Fast • 🪶 Lightweight • 0️⃣ Dependency • 🔌 Pluggable •
# 😈 TLS interception • 🔒 DNS-over-HTTPS • 🔥 Poor Man's VPN •
# ⏪ Reverse & ⏩ Forward • 👮🏿 "Proxy Server" framework •
# 🌐 "Web Server" framework • ➵ ➶ ➷ ➠ "PubSub" framework •
# 👷 "Work" acceptor & executor framework.
#
# :copyright: (c) 2013-present by Abhinav Singh and contributors.
# :license: BSD, see LICENSE for more details.
#
from typing import Type
from proxy.http.proxy import HttpProxyBasePlugin

from proxy.plugin import ModifyPostDataPlugin, ProposedRestApiPlugin, RedirectToCustomServerPlugin, \
    FilterByUpstreamHostPlugin, CacheResponsesPlugin, ManInTheMiddlePlugin, FilterByURLRegexPlugin


def get_plugin_by_test_name(test_name: str) -> Type[HttpProxyBasePlugin]:
    plugin: Type[HttpProxyBasePlugin] = ModifyPostDataPlugin
    if test_name == 'test_modify_post_data_plugin':
        plugin = ModifyPostDataPlugin
    elif test_name == 'test_proposed_rest_api_plugin':
        plugin = ProposedRestApiPlugin
    elif test_name == 'test_redirect_to_custom_server_plugin':
        plugin = RedirectToCustomServerPlugin
    elif test_name == 'test_filter_by_upstream_host_plugin':
        plugin = FilterByUpstreamHostPlugin
    elif test_name == 'test_cache_responses_plugin':
        plugin = CacheResponsesPlugin
    elif test_name == 'test_man_in_the_middle_plugin':
        plugin = ManInTheMiddlePlugin
    elif test_name == 'test_filter_by_url_regex_plugin':
        plugin = FilterByURLRegexPlugin
    return plugin
