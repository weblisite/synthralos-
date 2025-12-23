"""
Resource Limits Management

Manages resource limits for workflow executions:
- Memory limits per execution
- CPU limits per execution
- Timeout limits
- Concurrent execution limits per user
- Resource quota management
"""

import uuid
from datetime import datetime
from typing import Any

from sqlmodel import Session, func, select

from app.core.config import settings
from app.models import WorkflowExecution


class ResourceLimitError(Exception):
    """Base exception for resource limit errors."""

    pass


class ResourceLimitsManager:
    """
    Manages resource limits for workflow executions.
    """

    def __init__(self):
        """Initialize resource limits manager."""
        # Default limits (can be overridden by settings)
        self.default_memory_limit_mb = getattr(
            settings, "WORKFLOW_MEMORY_LIMIT_MB", 512
        )
        self.default_cpu_limit = getattr(settings, "WORKFLOW_CPU_LIMIT", 1.0)
        self.default_timeout_seconds = getattr(
            settings, "WORKFLOW_TIMEOUT_SECONDS", 3600
        )
        self.default_concurrent_executions_per_user = getattr(
            settings, "WORKFLOW_CONCURRENT_EXECUTIONS_PER_USER", 10
        )

    def check_user_concurrent_limit(
        self,
        session: Session,
        user_id: uuid.UUID,
    ) -> tuple[bool, int]:
        """
        Check if user has reached concurrent execution limit.

        Args:
            session: Database session
            user_id: User ID

        Returns:
            Tuple of (within_limit, current_count)
        """
        # Get workflow IDs owned by user
        from app.models import Workflow

        workflow_query = select(Workflow.id).where(Workflow.owner_id == user_id)
        workflow_ids = [w.id for w in session.exec(workflow_query).all()]

        if not workflow_ids:
            return (True, 0)

        # Count running executions for user's workflows
        query = (
            select(func.count(WorkflowExecution.id))
            .where(WorkflowExecution.workflow_id.in_(workflow_ids))
            .where(WorkflowExecution.status == "running")
        )

        current_count = session.exec(query).one()

        limit = self.default_concurrent_executions_per_user

        return (current_count < limit, current_count)

    def check_execution_resources(
        self,
        session: Session,
        execution_id: uuid.UUID,
    ) -> dict[str, Any]:
        """
        Check resource usage for an execution.

        Args:
            session: Database session
            execution_id: Execution ID

        Returns:
            Dictionary with resource usage information
        """
        execution = session.get(WorkflowExecution, execution_id)
        if not execution:
            return {}

        # Get resource limits from execution_state
        state = execution.execution_state or {}
        memory_limit = state.get("memory_limit_mb", self.default_memory_limit_mb)
        cpu_limit = state.get("cpu_limit", self.default_cpu_limit)
        timeout_seconds = state.get("timeout_seconds", self.default_timeout_seconds)

        # Calculate resource usage (simplified - would integrate with actual monitoring)
        duration_seconds = (
            (datetime.utcnow() - execution.started_at).total_seconds()
            if execution.started_at
            else 0
        )

        return {
            "execution_id": str(execution_id),
            "memory_limit_mb": memory_limit,
            "cpu_limit": cpu_limit,
            "timeout_seconds": timeout_seconds,
            "duration_seconds": duration_seconds,
            "within_limits": duration_seconds < timeout_seconds,
        }

    def set_execution_limits(
        self,
        session: Session,
        execution_id: uuid.UUID,
        memory_limit_mb: int | None = None,
        cpu_limit: float | None = None,
        timeout_seconds: int | None = None,
    ) -> None:
        """
        Set resource limits for an execution.

        Args:
            session: Database session
            execution_id: Execution ID
            memory_limit_mb: Memory limit in MB
            cpu_limit: CPU limit (cores)
            timeout_seconds: Timeout in seconds
        """
        execution = session.get(WorkflowExecution, execution_id)
        if not execution:
            return

        state = execution.execution_state or {}

        if memory_limit_mb is not None:
            state["memory_limit_mb"] = memory_limit_mb

        if cpu_limit is not None:
            state["cpu_limit"] = cpu_limit

        if timeout_seconds is not None:
            state["timeout_seconds"] = timeout_seconds

        execution.execution_state = state
        session.add(execution)
        session.commit()

    def enforce_user_limits(
        self,
        session: Session,
        user_id: uuid.UUID,
    ) -> None:
        """
        Enforce resource limits for a user.

        Args:
            session: Database session
            user_id: User ID

        Raises:
            ResourceLimitError: If limits are exceeded
        """
        within_limit, current_count = self.check_user_concurrent_limit(session, user_id)

        if not within_limit:
            limit = self.default_concurrent_executions_per_user
            raise ResourceLimitError(
                f"User has reached concurrent execution limit ({current_count}/{limit})"
            )


# Default resource limits manager instance
default_resource_limits_manager = ResourceLimitsManager()
