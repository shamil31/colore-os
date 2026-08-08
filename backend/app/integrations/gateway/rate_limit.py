"""Per-bucket minimum interval between outbound calls.

The limits are the platforms' own published numbers, not guesses:

- Telegram: "In a single chat, avoid sending more than one message per second."
- Altegio:  "200 requests/min or 5 requests/sec per IP."

The bucket matters as much as the interval. Telegram's limit is per *chat*, so
one busy conversation must not throttle alerts about a different one, and one
connector must not be able to exhaust the salon's whole Altegio quota answering
a single message.

Deliberately in-process and in-memory: one backend container holds the whole
outbound path today. If a second replica ever runs, this becomes per-replica
and the limits need to move to Redis — see the note in `docs/research/`.
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable


class RateLimitExceeded(Exception):
    """The wait needed to stay inside the limit was longer than `max_wait`."""


class RateLimiter:
    """Enforces a minimum interval between calls sharing a bucket key.

    `clock` and `sleeper` are injectable so tests do not have to spend real
    seconds proving that a one-second limit is a one-second limit.
    """

    def __init__(
        self,
        *,
        max_wait: float = 3.0,
        clock: Callable[[], float] | None = None,
        sleeper: Callable[[float], None] | None = None,
    ) -> None:
        self.max_wait = max_wait
        self._clock = clock or time.monotonic
        self._sleeper = sleeper or time.sleep
        self._last: dict[str, float] = {}
        self._lock = threading.Lock()

    def acquire(self, key: str, min_interval: float) -> float:
        """Block until the bucket is free. Returns how long that took.

        Raises `RateLimitExceeded` rather than sleeping past `max_wait`: a
        caller waiting indefinitely inside a webhook handler is worse than a
        recorded failure it can retry.
        """
        if min_interval <= 0:
            return 0.0

        with self._lock:
            now = self._clock()
            previous = self._last.get(key)

            if previous is None:
                self._last[key] = now
                return 0.0

            wait = (previous + min_interval) - now
            if wait <= 0:
                self._last[key] = now
                return 0.0

            if wait > self.max_wait:
                raise RateLimitExceeded(
                    f"{key} needs {wait:.2f}s to stay within "
                    f"{min_interval:.2f}s spacing, limit is {self.max_wait:.2f}s"
                )

            # Reserve the slot before releasing the lock so concurrent callers
            # queue behind this one instead of all computing the same wait.
            self._last[key] = previous + min_interval

        self._sleeper(wait)
        return wait

    def reset(self) -> None:
        with self._lock:
            self._last.clear()
