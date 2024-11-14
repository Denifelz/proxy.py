# -*- coding: utf-8 -*-
"""
    proxy.py
    ~~~~~~~~
    ⚡⚡⚡ Fast, Lightweight, Pluggable, TLS interception capable proxy server focused on
    Network monitoring, controls & Application development, testing, debugging.

    :copyright: (c) 2013-present by Abhinav Singh and contributors.
    :license: BSD, see LICENSE for more details.
"""
import time


class Leakage:
    def __init__(self, rate: int):
        """Initialize the leaky bucket with a specified leak rate in bytes per second."""
        self.rate = (
            rate  # Maximum number of tokens the bucket can hold (bytes per second)
        )
        self.tokens = rate  # Initially start with a full bucket
        self.last_check = time.time()  # Record the current time

    def _refill(self):
        """Refill tokens based on the elapsed time since the last check."""
        now = time.time()
        elapsed = now - self.last_check
        # Add tokens proportional to elapsed time, up to the rate
        self.tokens += int(elapsed * self.rate)
        # Cap tokens at the maximum rate to enforce the rate limit
        self.tokens = min(self.tokens, self.rate)
        self.last_check = now  # Update the last check time

    def putback(self, tokens) -> None:
        self.tokens += tokens

    def consume(self, amount: int) -> int:
        """Attempt to consume the amount from the bucket.

        Returns the amount allowed to be sent, up to the available tokens (rate).
        """
        self._refill()  # Refill the tokens before consumption
        allowed = min(amount, self.tokens)  # Allow up to the available tokens
        self.tokens -= allowed  # Subtract the allowed amount from the available tokens
        return allowed  # Return the number of bytes allowed to be consumed
