"""
Cache Module

Provides caching layer for database queries and computed results.
"""

from app.cache.decorators import cache_result, invalidate_cache
from app.cache.service import CacheService, default_cache_service

__all__ = [
    "CacheService",
    "default_cache_service",
    "cache_result",
    "invalidate_cache",
]
