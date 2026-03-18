"""Durable delivery-ID deduplication (replay) store for GitHub App webhooks.

Design notes
------------
The default implementation is in-process (dict-backed).  It is intentionally
isolated behind a ``ReplayStore`` protocol so that a Redis- or DB-backed
implementation can be swapped in without touching webhook ingress logic.

Restart-safety guarantee
------------------------
In-process storage does **not** survive process restarts.  For a single-process
deployment this is an acceptable trade-off: the window in which a replayed
delivery could sneak past the check is bounded by the time between a restart
and the next delivery of the same ID, which GitHub's retry policy makes
extremely unlikely in practice (delivery IDs are unique per attempt).

If strict restart-safety is required, replace ``InMemoryReplayStore`` with a
``RedisReplayStore`` or similar and inject it via the ``replay_store`` module
singleton assignment.
"""
from __future__ import annotations

import threading
import time
from typing import Protocol, runtime_checkable

from trustagents.observability import get_logger

logger = get_logger("github_app.replay_store")

# How long to keep delivery IDs before they are eligible for eviction (seconds).
# GitHub retries within a 72-hour window; 80 hours provides a comfortable buffer.
_TTL_SECONDS: int = 80 * 3600


@runtime_checkable
class ReplayStore(Protocol):
    """Minimal interface that any replay-protection backend must satisfy."""

    def is_seen(self, delivery_id: str) -> bool:
        """Return True if *delivery_id* has been processed before."""
        ...

    def mark_seen(self, delivery_id: str) -> None:
        """Record *delivery_id* as processed."""
        ...


class InMemoryReplayStore:
    """Thread-safe, TTL-evicting in-memory replay store.

    Eviction runs on every ``mark_seen`` call to avoid unbounded growth.
    The eviction pass is O(n) but is cheap for the typical delivery volume.
    """

    def __init__(self, ttl_seconds: int = _TTL_SECONDS) -> None:
        self._records: dict[str, float] = {}  # delivery_id -> expiry epoch
        self._lock = threading.Lock()
        self._ttl = ttl_seconds

    def is_seen(self, delivery_id: str) -> bool:
        with self._lock:
            expiry = self._records.get(delivery_id)
            if expiry is None:
                return False
            if time.monotonic() > expiry:
                # Expired — treat as unseen and evict proactively
                del self._records[delivery_id]
                return False
            return True

    def mark_seen(self, delivery_id: str) -> None:
        now = time.monotonic()
        with self._lock:
            self._records[delivery_id] = now + self._ttl
            self._evict(now)

    def _evict(self, now: float) -> None:
        """Remove entries whose TTL has elapsed. Must be called under _lock."""
        expired = [k for k, expiry in self._records.items() if now > expiry]
        for k in expired:
            del self._records[k]
            logger.debug("replay_store_evicted", extra={"delivery_id": k})

    def __len__(self) -> int:
        with self._lock:
            return len(self._records)


# Module-level singleton used by webhook ingress.
# To swap for a persistent backend:
#   from trustagents.github_app.replay_store import replay_store
#   replay_store = RedisReplayStore(...)
replay_store: ReplayStore = InMemoryReplayStore()
