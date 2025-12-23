"""
Execution Caching

Provides caching for workflow execution:
- Workflow state caching
- Node result caching
- Execution data caching
- Cache invalidation
- Cache warming
"""

import uuid
from datetime import datetime, timedelta
from typing import Any

from sqlmodel import Session

from app.workflows.engine import WorkflowEngine
from app.workflows.state import ExecutionState


class CacheEntry:
    """Cache entry for execution state."""

    def __init__(
        self,
        data: dict[str, Any],
        expires_at: datetime,
    ):
        """
        Initialize cache entry.

        Args:
            data: Cached data
            expires_at: Expiration time
        """
        self.data = data
        self.expires_at = expires_at

    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        return datetime.utcnow() > self.expires_at


class ExecutionCache:
    """
    Cache for workflow execution state.
    """

    def __init__(
        self,
        default_ttl_seconds: int = 300,  # 5 minutes
    ):
        """
        Initialize execution cache.

        Args:
            default_ttl_seconds: Default TTL in seconds
        """
        self.default_ttl_seconds = default_ttl_seconds
        self._cache: dict[str, CacheEntry] = {}  # execution_id -> CacheEntry

    def get(
        self,
        execution_id: uuid.UUID,
    ) -> dict[str, Any] | None:
        """
        Get cached execution state.

        Args:
            execution_id: Execution ID

        Returns:
            Cached state if found and not expired, None otherwise
        """
        cache_key = str(execution_id)
        entry = self._cache.get(cache_key)

        if not entry:
            return None

        if entry.is_expired():
            del self._cache[cache_key]
            return None

        return entry.data

    def set(
        self,
        execution_id: uuid.UUID,
        data: dict[str, Any],
        ttl_seconds: int | None = None,
    ) -> None:
        """
        Cache execution state.

        Args:
            execution_id: Execution ID
            data: State data to cache
            ttl_seconds: Optional TTL in seconds
        """
        cache_key = str(execution_id)
        ttl = ttl_seconds or self.default_ttl_seconds
        expires_at = datetime.utcnow() + timedelta(seconds=ttl)

        self._cache[cache_key] = CacheEntry(data, expires_at)

    def invalidate(
        self,
        execution_id: uuid.UUID,
    ) -> None:
        """
        Invalidate cache for an execution.

        Args:
            execution_id: Execution ID
        """
        cache_key = str(execution_id)
        self._cache.pop(cache_key, None)

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()

    def cleanup_expired(self) -> int:
        """
        Remove expired cache entries.

        Returns:
            Number of entries removed
        """
        expired_keys = [key for key, entry in self._cache.items() if entry.is_expired()]

        for key in expired_keys:
            del self._cache[key]

        return len(expired_keys)


class CachedWorkflowEngine:
    """
    Workflow engine with caching support.
    """

    def __init__(
        self,
        workflow_engine: WorkflowEngine | None = None,
        cache: ExecutionCache | None = None,
    ):
        """
        Initialize cached workflow engine.

        Args:
            workflow_engine: WorkflowEngine instance
            cache: ExecutionCache instance
        """
        self.workflow_engine = workflow_engine or WorkflowEngine()
        self.cache = cache or ExecutionCache()

    def get_execution_state_cached(
        self,
        session: Session,
        execution_id: uuid.UUID,
    ) -> ExecutionState:
        """
        Get execution state with caching.

        Args:
            session: Database session
            execution_id: Execution ID

        Returns:
            ExecutionState instance
        """
        # Try cache first
        cached_data = self.cache.get(execution_id)

        if cached_data:
            from app.workflows.state import ExecutionState

            return ExecutionState.from_dict(cached_data)

        # Cache miss - get from database
        state = self.workflow_engine.get_execution_state(session, execution_id)

        # Cache the state
        self.cache.set(execution_id, state.to_dict())

        return state

    def save_execution_state_cached(
        self,
        session: Session,
        execution_id: uuid.UUID,
        state: ExecutionState,
    ) -> None:
        """
        Save execution state with cache invalidation.

        Args:
            session: Database session
            execution_id: Execution ID
            state: ExecutionState instance
        """
        # Save to database
        self.workflow_engine.save_execution_state(session, execution_id, state)

        # Update cache
        self.cache.set(execution_id, state.to_dict())


# Default cache instance
default_execution_cache = ExecutionCache()
