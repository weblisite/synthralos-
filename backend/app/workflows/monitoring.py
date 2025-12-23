"""
Workflow Monitoring and Observability

Provides monitoring and observability for workflow execution:
- Metrics collection
- Performance monitoring
- Error tracking
- Resource usage monitoring
"""

import uuid
from datetime import datetime
from typing import Any

from sqlmodel import Session, func, select

from app.models import ExecutionLog, WorkflowExecution
from app.observability.langfuse import default_langfuse_client
from app.observability.posthog import default_posthog_client


class WorkflowMonitor:
    """
    Monitors workflow execution and collects metrics.
    """

    def __init__(self):
        """Initialize workflow monitor."""
        pass

    def record_execution_start(
        self,
        execution_id: uuid.UUID,
        workflow_id: uuid.UUID,
        user_id: uuid.UUID | None = None,
    ) -> None:
        """
        Record execution start event.

        Args:
            execution_id: Execution ID
            workflow_id: Workflow ID
            user_id: Optional user ID
        """
        # Langfuse trace
        if default_langfuse_client:
            try:
                trace = default_langfuse_client.trace(
                    name="workflow_execution",
                    id=str(execution_id),
                    metadata={
                        "workflow_id": str(workflow_id),
                        "execution_id": str(execution_id),
                    },
                )
                trace.update(
                    metadata={
                        "user_id": str(user_id) if user_id else None,
                    }
                )
            except Exception:
                pass

        # PostHog event
        if default_posthog_client:
            try:
                default_posthog_client.capture(
                    distinct_id=str(user_id) if user_id else "anonymous",
                    event="workflow_execution_started",
                    properties={
                        "execution_id": str(execution_id),
                        "workflow_id": str(workflow_id),
                    },
                )
            except Exception:
                pass

    def record_execution_complete(
        self,
        execution_id: uuid.UUID,
        workflow_id: uuid.UUID,
        status: str,
        duration_seconds: float,
        user_id: uuid.UUID | None = None,
    ) -> None:
        """
        Record execution completion event.

        Args:
            execution_id: Execution ID
            workflow_id: Workflow ID
            status: Execution status
            duration_seconds: Execution duration
            user_id: Optional user ID
        """
        # Langfuse trace
        if default_langfuse_client:
            try:
                trace = default_langfuse_client.trace(
                    id=str(execution_id),
                )
                trace.update(
                    output={
                        "status": status,
                        "duration_seconds": duration_seconds,
                    },
                    metadata={
                        "completed_at": datetime.utcnow().isoformat(),
                    },
                )
            except Exception:
                pass

        # PostHog event
        if default_posthog_client:
            try:
                default_posthog_client.capture(
                    distinct_id=str(user_id) if user_id else "anonymous",
                    event="workflow_execution_completed",
                    properties={
                        "execution_id": str(execution_id),
                        "workflow_id": str(workflow_id),
                        "status": status,
                        "duration_seconds": duration_seconds,
                    },
                )
            except Exception:
                pass

    def record_node_execution(
        self,
        execution_id: uuid.UUID,
        node_id: str,
        node_type: str,
        status: str,
        duration_ms: int,
    ) -> None:
        """
        Record node execution event.

        Args:
            execution_id: Execution ID
            node_id: Node ID
            node_type: Node type
            status: Execution status
            duration_ms: Execution duration in milliseconds
        """
        # Langfuse span
        if default_langfuse_client:
            try:
                trace = default_langfuse_client.trace(id=str(execution_id))
                span = trace.span(
                    name=f"node_{node_id}",
                    metadata={
                        "node_id": node_id,
                        "node_type": node_type,
                        "status": status,
                        "duration_ms": duration_ms,
                    },
                )
                span.end(output={"status": status})
            except Exception:
                pass

    def record_error(
        self,
        execution_id: uuid.UUID,
        workflow_id: uuid.UUID,
        error_type: str,
        error_message: str,
        node_id: str | None = None,
        user_id: uuid.UUID | None = None,
    ) -> None:
        """
        Record error event.

        Args:
            execution_id: Execution ID
            workflow_id: Workflow ID
            error_type: Error type
            error_message: Error message
            node_id: Optional node ID
            user_id: Optional user ID
        """
        # Langfuse trace
        if default_langfuse_client:
            try:
                trace = default_langfuse_client.trace(id=str(execution_id))
                trace.update(
                    output={
                        "error": True,
                        "error_type": error_type,
                        "error_message": error_message,
                    },
                    level="ERROR",
                )
            except Exception:
                pass

        # PostHog event
        if default_posthog_client:
            try:
                default_posthog_client.capture(
                    distinct_id=str(user_id) if user_id else "anonymous",
                    event="workflow_execution_error",
                    properties={
                        "execution_id": str(execution_id),
                        "workflow_id": str(workflow_id),
                        "error_type": error_type,
                        "error_message": error_message,
                        "node_id": node_id,
                    },
                )
            except Exception:
                pass

    def get_execution_metrics(
        self,
        session: Session,
        workflow_id: uuid.UUID | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> dict[str, Any]:
        """
        Get execution metrics.

        Args:
            session: Database session
            workflow_id: Optional workflow ID filter
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            Metrics dictionary
        """
        query = select(WorkflowExecution)

        if workflow_id:
            query = query.where(WorkflowExecution.workflow_id == workflow_id)

        if start_date:
            query = query.where(WorkflowExecution.started_at >= start_date)

        if end_date:
            query = query.where(WorkflowExecution.started_at <= end_date)

        executions = list(session.exec(query).all())

        total = len(executions)
        completed = sum(1 for e in executions if e.status == "completed")
        failed = sum(1 for e in executions if e.status == "failed")
        running = sum(1 for e in executions if e.status == "running")

        # Calculate durations
        completed_executions = [
            e for e in executions if e.status == "completed" and e.completed_at
        ]
        durations = [
            (e.completed_at - e.started_at).total_seconds()
            for e in completed_executions
        ]

        avg_duration = sum(durations) / len(durations) if durations else 0
        min_duration = min(durations) if durations else 0
        max_duration = max(durations) if durations else 0

        # Get error logs
        error_logs_query = select(func.count(ExecutionLog.id)).where(
            ExecutionLog.level == "error"
        )
        if workflow_id:
            from app.models import Workflow

            workflow_ids = [
                w.id
                for w in session.exec(
                    select(Workflow.id).where(Workflow.id == workflow_id)
                ).all()
            ]
            if workflow_ids:
                execution_ids = [
                    e.id
                    for e in session.exec(
                        select(WorkflowExecution.id).where(
                            WorkflowExecution.workflow_id.in_(workflow_ids)
                        )
                    ).all()
                ]
                if execution_ids:
                    error_logs_query = error_logs_query.where(
                        ExecutionLog.execution_id.in_(execution_ids)
                    )

        error_count = session.exec(error_logs_query).one() or 0

        return {
            "total_executions": total,
            "completed": completed,
            "failed": failed,
            "running": running,
            "success_rate": completed / total if total > 0 else 0,
            "failure_rate": failed / total if total > 0 else 0,
            "avg_duration_seconds": avg_duration,
            "min_duration_seconds": min_duration,
            "max_duration_seconds": max_duration,
            "error_count": error_count,
        }


# Default monitor instance
default_workflow_monitor = WorkflowMonitor()
