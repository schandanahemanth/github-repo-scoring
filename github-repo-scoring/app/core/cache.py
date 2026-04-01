from __future__ import annotations

from dataclasses import dataclass
from time import time
from typing import Callable, Generic, TypeVar

K = TypeVar("K")
V = TypeVar("V")


@dataclass
class CacheEntry(Generic[V]):
    value: V
    expires_at: float


class InMemoryTTLCache(Generic[K, V]):
    """Store values in memory until their configured expiration time."""

    def __init__(self, time_provider: Callable[[], float] | None = None) -> None:
        """Initialize the cache with an optional time provider for tests."""
        self._store: dict[K, CacheEntry[V]] = {}
        self._time_provider = time_provider or time

    def get(self, key: K) -> V | None:
        """Return a cached value when present and not expired."""
        entry = self._store.get(key)
        if entry is None:
            return None
        if entry.expires_at <= self._time_provider():
            self._store.pop(key, None)
            return None
        return entry.value

    def set(self, key: K, value: V, ttl_seconds: int) -> None:
        """Cache a value for the provided TTL in seconds."""
        self._store[key] = CacheEntry(
            value=value,
            expires_at=self._time_provider() + ttl_seconds,
        )
