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
import logging

from proxy.common.utils import socket_connection
from proxy.common.constants import DEFAULT_BUFFER_SIZE

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    with socket_connection(('::', 12345)) as client:
        while True:
            client.send(b'hello')
            data = client.recv(DEFAULT_BUFFER_SIZE)
            if data is None:
                break
            logger.info(data)
