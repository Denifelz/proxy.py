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

       eventing
       iterable
       Submodules
"""
from .queue import EventQueue
from .names import EventNames, eventNames
from .dispatcher import EventDispatcher
from .subscriber import EventSubscriber
from .manager import EventManager

__all__ = [
    'eventNames',
    'EventNames',
    'EventQueue',
    'EventDispatcher',
    'EventSubscriber',
    'EventManager',
]
