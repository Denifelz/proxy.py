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
"""
    .. spelling::

       reusability
       Submodules
"""
from .connection import TcpConnection, TcpConnectionUninitializedException
from .client import TcpClientConnection
from .server import TcpServerConnection
from .pool import ConnectionPool
from .types import tcpConnectionTypes

__all__ = [
    'TcpConnection',
    'TcpConnectionUninitializedException',
    'TcpServerConnection',
    'TcpClientConnection',
    'tcpConnectionTypes',
    'ConnectionPool',
]
