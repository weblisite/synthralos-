"""
Timeout Management for Workflow Execution

Handles node and workflow-level timeouts:
- Per-node timeout detection
- Workflow-level timeout detection
- Timeout error handling
- Timeout retry logic
"""

import uuid
from datetime import datetime, timedelta

from sqlmodel import Session

from app.workflows.engine import WorkflowEngine


class TimeoutError(Exception):
    """Base exception for timeout errors."""

    pass


class TimeoutManager:
    """
    Manages timeouts for workflow executions and nodes.
    """

    def __init__(self, workflow_engine: WorkflowEngine | None = None):
        """
        Initialize timeout manager.

        Args:
            workflow_engine: WorkflowEngine instance
        """
        self.workflow_engine = workflow_engine or WorkflowEngine()

    def set_node_timeout(
        self,
        session: Session,
        execution_id: uuid.UUID,
        node_id: str,
        timeout_seconds: int,
    ) -> None:
        """
        Set timeout for a specific node.

        Args:
            session: Database session
            execution_id: Execution ID
            node_id: Node ID
            timeout_seconds: Timeout in seconds
        """
        state = self.workflow_engine.get_execution_state(session, execution_id)
        deadline = datetime.utcnow() + timedelta(seconds=timeout_seconds)
        state.node_timeouts[node_id] = deadline
        self.workflow_engine.save_execution_state(session, execution_id, state)

    def set_workflow_timeout(
        self,
        session: Session,
        execution_id: uuid.UUID,
        timeout_seconds: int,
    ) -> None:
        """
        Set timeout for entire workflow execution.

        Args:
            session: Database session
            execution_id: Execution ID
            timeout_seconds: Timeout in seconds
        """
        state = self.workflow_engine.get_execution_state(session, execution_id)
        deadline = datetime.utcnow() + timedelta(seconds=timeout_seconds)
        state.workflow_timeout = deadline
        self.workflow_engine.save_execution_state(session, execution_id, state)

    def check_node_timeout(
        self,
        session: Session,
        execution_id: uuid.UUID,
        node_id: str,
    ) -> bool:
        """
        Check if a node has timed out.

        Args:
            session: Database session
            execution_id: Execution ID
            node_id: Node ID

        Returns:
            True if node has timed out, False otherwise
        """
        state = self.workflow_engine.get_execution_state(session, execution_id)
        deadline = state.node_timeouts.get(node_id)

        if deadline and datetime.utcnow() > deadline:
            return True

        return False

    def check_workflow_timeout(
        self,
        session: Session,
        execution_id: uuid.UUID,
    ) -> bool:
        """
        Check if workflow execution has timed out.

        Args:
            session: Database session
            execution_id: Execution ID

        Returns:
            True if workflow has timed out, False otherwise
        """
        state = self.workflow_engine.get_execution_state(session, execution_id)

        if state.workflow_timeout and datetime.utcnow() > state.workflow_timeout:
            return True

        return False

    def handle_node_timeout(
        self,
        session: Session,
        execution_id: uuid.UUID,
        node_id: str,
        retry: bool = False,
    ) -> None:
        """
        Handle node timeout.

        Args:
            session: Database session
            execution_id: Execution ID
            node_id: Node ID
            retry: Whether to retry the node
        """
        state = self.workflow_engine.get_execution_state(session, execution_id)
        deadline = state.node_timeouts.get(node_id)

        if deadline:
            timeout_duration = (deadline - state.started_at).total_seconds()

            if retry:
                # Schedule retry
                self.workflow_engine.fail_execution(
                    session,
                    execution_id,
                    f"Node {node_id} timed out after {timeout_duration} seconds",
                    schedule_retry=True,
                )
            else:
                # Fail execution
                self.workflow_engine.fail_execution(
                    session,
                    execution_id,
                    f"Node {node_id} timed out after {timeout_duration} seconds",
                    schedule_retry=False,
                )

    def handle_workflow_timeout(
        self,
        session: Session,
        execution_id: uuid.UUID,
    ) -> None:
        """
        Handle workflow timeout.

        Args:
            session: Database session
            execution_id: Execution ID
        """
        state = self.workflow_engine.get_execution_state(session, execution_id)

        if state.workflow_timeout:
            timeout_duration = (
                state.workflow_timeout - state.started_at
            ).total_seconds()

            self.workflow_engine.fail_execution(
                session,
                execution_id,
                f"Workflow execution timed out after {timeout_duration} seconds",
                schedule_retry=False,
            )

    def get_remaining_time(
        self,
        session: Session,
        execution_id: uuid.UUID,
        node_id: str | None = None,
    ) -> float | None:
        """
        Get remaining time before timeout.

        Args:
            session: Database session
            execution_id: Execution ID
            node_id: Optional node ID (for node timeout)

        Returns:
            Remaining seconds, or None if no timeout set
        """
        state = self.workflow_engine.get_execution_state(session, execution_id)

        if node_id:
            deadline = state.node_timeouts.get(node_id)
            if deadline:
                remaining = (deadline - datetime.utcnow()).total_seconds()
                return max(0, remaining)
        else:
            if state.workflow_timeout:
                remaining = (state.workflow_timeout - datetime.utcnow()).total_seconds()
                return max(0, remaining)

        return None


# Default timeout manager instance
default_timeout_manager = TimeoutManager()
