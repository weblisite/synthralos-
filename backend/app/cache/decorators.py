"""
Cache Decorators

Decorators for caching function results.
"""

import functools
from collections.abc import Callable

from app.cache.service import default_cache_service


def cache_result(
    ttl_seconds: int | None = None,
    key_prefix: str | None = None,
    key_func: Callable[[tuple, dict], str] | None = None,
):
    """
    Decorator to cache function results.

    Args:
        ttl_seconds: Time-to-live in seconds (None for no expiration)
        key_prefix: Prefix for cache key (defaults to function name)
        key_func: Custom function to generate cache key from args/kwargs

    Example:
        @cache_result(ttl_seconds=300)
        def expensive_query(user_id: int):
            return db.query(User).filter(User.id == user_id).first()
    """

    def decorator(func: Callable) -> Callable:
        prefix = key_prefix or f"{func.__module__}.{func.__name__}"

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cache = default_cache_service

            # Generate cache key
            if key_func:
                cache_key = key_func(args, kwargs)
            else:
                cache_key = cache._generate_key(prefix, *args, **kwargs)

            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Compute result
            result = func(*args, **kwargs)

            # Cache result
            cache.set(cache_key, result, ttl_seconds)

            return result

        return wrapper

    return decorator


def invalidate_cache(key_prefix: str | None = None):
    """
    Decorator to invalidate cache after function execution.

    Args:
        key_prefix: Prefix for cache keys to invalidate

    Example:
        @invalidate_cache(key_prefix="user")
        def update_user(user_id: int):
            # This will invalidate all cache keys starting with "user"
            pass
    """

    def decorator(func: Callable) -> Callable:
        prefix = key_prefix or f"{func.__module__}.{func.__name__}"

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Execute function
            result = func(*args, **kwargs)

            # Invalidate cache
            cache = default_cache_service
            cache.clear(prefix)

            return result

        return wrapper

    return decorator
