"""
Execution Prioritization

Provides priority-based execution ordering:
- Priority queue for executions
- Priority-based execution order
- Priority inheritance
- Priority-based resource allocation
"""

import uuid
from enum import IntEnum

from sqlmodel import Session, select

from app.models import WorkflowExecution


class ExecutionPriority(IntEnum):
    """Execution priority levels."""

    LOW = 1
    NORMAL = 5
    HIGH = 10
    CRITICAL = 20


class PrioritizationManager:
    """
    Manages execution prioritization.
    """

    def __init__(self):
        """Initialize prioritization manager."""
        pass

    def get_execution_priority(
        self,
        session: Session,
        execution_id: uuid.UUID,
    ) -> int:
        """
        Get priority for an execution.

        Args:
            session: Database session
            execution_id: Execution ID

        Returns:
            Priority value (higher = more important)
        """
        execution = session.get(WorkflowExecution, execution_id)
        if not execution:
            return ExecutionPriority.NORMAL

        # Get priority from execution_state or trigger_data
        state = execution.execution_state or {}
        trigger_data = execution.trigger_data or {}

        # Check explicit priority
        priority = (
            state.get("priority")
            or trigger_data.get("priority")
            or ExecutionPriority.NORMAL
        )

        # Convert string to enum if needed
        if isinstance(priority, str):
            try:
                priority = ExecutionPriority[priority.upper()].value
            except KeyError:
                priority = ExecutionPriority.NORMAL

        return int(priority)

    def get_prioritized_executions(
        self,
        session: Session,
        status: str = "running",
        limit: int = 100,
    ) -> list[WorkflowExecution]:
        """
        Get executions ordered by priority.

        Args:
            session: Database session
            status: Execution status filter
            limit: Maximum number of executions to return

        Returns:
            List of executions ordered by priority (highest first)
        """
        query = select(WorkflowExecution).where(WorkflowExecution.status == status)

        executions = list(session.exec(query).all())

        # Sort by priority (highest first)
        executions.sort(
            key=lambda e: self.get_execution_priority(session, e.id), reverse=True
        )

        return executions[:limit]

    def set_execution_priority(
        self,
        session: Session,
        execution_id: uuid.UUID,
        priority: int | ExecutionPriority,
    ) -> None:
        """
        Set priority for an execution.

        Args:
            session: Database session
            execution_id: Execution ID
            priority: Priority value
        """
        execution = session.get(WorkflowExecution, execution_id)
        if not execution:
            return

        # Convert enum to int if needed
        if isinstance(priority, ExecutionPriority):
            priority = priority.value

        # Update execution_state
        state = execution.execution_state or {}
        state["priority"] = priority
        execution.execution_state = state

        session.add(execution)
        session.commit()


# Default prioritization manager instance
default_prioritization_manager = PrioritizationManager()
