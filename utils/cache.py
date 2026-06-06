"""
LLM Response Cache — Thread-safe LRU cache with TTL support.

Caches LLM responses keyed by a SHA-256 hash of (model, system_prompt, prompt, temperature, json_mode).
Avoids re-calling the LLM when the same prompt is sent again within the TTL window.
"""

import hashlib
import json
import time
import threading
import logging
from typing import Optional, Any
from collections import OrderedDict

logger = logging.getLogger(__name__)


class ResponseCache:
    """
    LRU cache for LLM responses.

    - max_size: maximum number of cached responses (oldest evicted first).
    - ttl_seconds: time-to-live for each entry; 0 means no expiry.
    """

    def __init__(self, max_size: int = 100, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: OrderedDict[str, dict] = OrderedDict()
        self._lock = threading.Lock()
        self._hits = 0
        self._misses = 0

    # ── public API ──────────────────────────────────────────────

    @staticmethod
    def make_key(
        model: str,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7,
        json_mode: bool = False,
    ) -> str:
        """Deterministic cache key from request parameters."""
        raw = json.dumps(
            {
                "model": model,
                "prompt": prompt,
                "system_prompt": system_prompt,
                "temperature": temperature,
                "json_mode": json_mode,
            },
            sort_keys=True,
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def get(self, key: str) -> Optional[str]:
        """Return cached response or None if miss / expired."""
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                self._misses += 1
                return None

            # Check TTL
            if self.ttl_seconds and (time.time() - entry["ts"]) > self.ttl_seconds:
                del self._cache[key]
                self._misses += 1
                logger.debug(f"Cache entry expired: {key[:12]}…")
                return None

            # Move to end (most recently used)
            self._cache.move_to_end(key)
            self._hits += 1
            logger.debug(f"Cache hit: {key[:12]}…")
            return entry["response"]

    def set(self, key: str, response: str) -> None:
        """Store a response in the cache."""
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
                self._cache[key] = {"response": response, "ts": time.time()}
            else:
                self._cache[key] = {"response": response, "ts": time.time()}
                if len(self._cache) > self.max_size:
                    evicted_key, _ = self._cache.popitem(last=False)
                    logger.debug(f"Cache evicted: {evicted_key[:12]}…")

    def clear(self) -> None:
        """Clear all cached entries."""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0

    @property
    def stats(self) -> dict:
        """Return cache hit/miss statistics."""
        total = self._hits + self._misses
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(self._hits / total, 2) if total else 0.0,
        }

    def __len__(self) -> int:
        return len(self._cache)

    def __repr__(self) -> str:
        return f"ResponseCache(size={len(self)}, max={self.max_size}, ttl={self.ttl_seconds}s)"
