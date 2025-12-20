"""
Cache Service

In-memory and Redis-based caching service for performance optimization.
"""

import hashlib
import json
import logging
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)


class CacheService:
    """
    Cache service for storing and retrieving cached data.

    Supports:
    - In-memory caching (default)
    - Redis caching (when available)
    - TTL (time-to-live) support
    - Cache invalidation
    """

    def __init__(self):
        """Initialize cache service."""
        self._memory_cache: dict[str, tuple[Any, float]] = {}
        self._redis_available = False
        self._redis_client = None
        self._check_redis_availability()

    def _check_redis_availability(self) -> None:
        """Check if Redis is available."""
        try:
            import redis

            from app.core.config import settings

            if settings.REDIS_URL:
                try:
                    self._redis_client = redis.from_url(settings.REDIS_URL)
                    # Test connection
                    self._redis_client.ping()
                    self._redis_available = True
                    logger.info("Redis cache enabled")
                except Exception as e:
                    logger.warning(
                        f"Redis connection failed: {e}. Using in-memory cache."
                    )
                    self._redis_available = False
                    self._redis_client = None
            else:
                self._redis_available = False
                logger.info("Using in-memory cache (Redis URL not configured)")
        except ImportError:
            logger.warning("Redis not installed. Install with: pip install redis")
            self._redis_available = False
            self._redis_client = None

    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """
        Generate cache key from prefix and arguments.

        Args:
            prefix: Cache key prefix
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Cache key string
        """
        # Create a hash of arguments
        key_data = {
            "prefix": prefix,
            "args": args,
            "kwargs": kwargs,
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        key_hash = hashlib.md5(key_str.encode()).hexdigest()
        return f"{prefix}:{key_hash}"

    def get(self, key: str) -> Any | None:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        # Check memory cache first
        if key in self._memory_cache:
            value, expiry = self._memory_cache[key]
            import time

            if expiry is None or time.time() < expiry:
                return value
            else:
                # Expired, remove from cache
                del self._memory_cache[key]

        # Check Redis if available
        if self._redis_available and self._redis_client:
            try:
                value = self._redis_client.get(key)
                if value:
                    return json.loads(value)
            except Exception as e:
                logger.warning(f"Redis get failed: {e}")

        return None

    def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: int | None = None,
    ) -> None:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time-to-live in seconds (None for no expiration)
        """
        import time

        # Set in memory cache
        expiry = None
        if ttl_seconds:
            expiry = time.time() + ttl_seconds
        self._memory_cache[key] = (value, expiry)

        # Set in Redis if available
        if self._redis_available and self._redis_client:
            try:
                value_json = json.dumps(value, default=str)
                if ttl_seconds:
                    self._redis_client.setex(key, ttl_seconds, value_json)
                else:
                    self._redis_client.set(key, value_json)
            except Exception as e:
                logger.warning(f"Redis set failed: {e}")

    def delete(self, key: str) -> None:
        """
        Delete value from cache.

        Args:
            key: Cache key
        """
        # Delete from memory cache
        if key in self._memory_cache:
            del self._memory_cache[key]

        # Delete from Redis if available
        if self._redis_available and self._redis_client:
            try:
                self._redis_client.delete(key)
            except Exception as e:
                logger.warning(f"Redis delete failed: {e}")

    def clear(self, prefix: str | None = None) -> None:
        """
        Clear cache entries.

        Args:
            prefix: Optional prefix to clear only matching keys
        """
        if prefix:
            # Clear keys with prefix
            keys_to_delete = [
                key for key in self._memory_cache.keys() if key.startswith(prefix)
            ]
            for key in keys_to_delete:
                del self._memory_cache[key]

            # Clear from Redis if available
            if self._redis_available and self._redis_client:
                try:
                    pattern = f"{prefix}*"
                    keys = self._redis_client.keys(pattern)
                    if keys:
                        self._redis_client.delete(*keys)
                except Exception as e:
                    logger.warning(f"Redis clear failed: {e}")
        else:
            # Clear all cache
            self._memory_cache.clear()

            if self._redis_available and self._redis_client:
                try:
                    self._redis_client.flushdb()
                except Exception as e:
                    logger.warning(f"Redis flush failed: {e}")

    def get_or_set(
        self,
        key: str,
        callable: Callable[[], Any],
        ttl_seconds: int | None = None,
    ) -> Any:
        """
        Get value from cache, or compute and cache if not found.

        Args:
            key: Cache key
            callable: Function to call if value not in cache
            ttl_seconds: Time-to-live in seconds

        Returns:
            Cached or computed value
        """
        value = self.get(key)
        if value is not None:
            return value

        # Compute value
        value = callable()

        # Cache it
        self.set(key, value, ttl_seconds)

        return value


# Default cache service instance
default_cache_service = CacheService()
