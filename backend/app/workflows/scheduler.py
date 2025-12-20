"""
Workflow CRON Scheduler

Handles scheduled workflow executions based on CRON expressions.
"""

import uuid
from datetime import datetime

from croniter import croniter
from sqlmodel import Session, select

from app.models import Workflow, WorkflowSchedule
from app.workflows.engine import WorkflowEngine


class SchedulerError(Exception):
    """Base exception for scheduler errors."""

    pass


class InvalidCronExpressionError(SchedulerError):
    """Invalid CRON expression."""

    pass


class WorkflowScheduler:
    """
    CRON-based workflow scheduler.

    Manages scheduled workflow executions:
    - Parsing CRON expressions
    - Calculating next run times
    - Triggering scheduled executions
    """

    def __init__(self, workflow_engine: WorkflowEngine | None = None):
        """
        Initialize scheduler.

        Args:
            workflow_engine: WorkflowEngine instance (creates new if None)
        """
        self.workflow_engine = workflow_engine or WorkflowEngine()

    def validate_cron_expression(self, cron_expr: str) -> bool:
        """
        Validate a CRON expression.

        Args:
            cron_expr: CRON expression to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            croniter(cron_expr)
            return True
        except Exception:
            return False

    def calculate_next_run(
        self,
        cron_expr: str,
        base_time: datetime | None = None,
    ) -> datetime:
        """
        Calculate next run time from CRON expression.

        Args:
            cron_expr: CRON expression
            base_time: Base time to calculate from (defaults to now)

        Returns:
            Next run datetime

        Raises:
            InvalidCronExpressionError: If CRON expression is invalid
        """
        if base_time is None:
            base_time = datetime.utcnow()

        try:
            cron = croniter(cron_expr, base_time)
            next_run = cron.get_next(datetime)
            return next_run
        except Exception as e:
            raise InvalidCronExpressionError(
                f"Invalid CRON expression '{cron_expr}': {e}"
            )

    def create_schedule(
        self,
        session: Session,
        workflow_id: uuid.UUID,
        cron_expression: str,
        is_active: bool = True,
    ) -> WorkflowSchedule:
        """
        Create a workflow schedule.

        Args:
            session: Database session
            workflow_id: Workflow ID
            cron_expression: CRON expression
            is_active: Whether schedule is active

        Returns:
            WorkflowSchedule instance

        Raises:
            InvalidCronExpressionError: If CRON expression is invalid
        """
        # Validate CRON expression
        if not self.validate_cron_expression(cron_expression):
            raise InvalidCronExpressionError(
                f"Invalid CRON expression: {cron_expression}"
            )

        # Calculate next run
        next_run_at = self.calculate_next_run(cron_expression)

        # Create schedule
        schedule = WorkflowSchedule(
            workflow_id=workflow_id,
            cron_expression=cron_expression,
            is_active=is_active,
            next_run_at=next_run_at,
        )

        session.add(schedule)
        session.commit()
        session.refresh(schedule)

        return schedule

    def update_schedule_next_run(
        self,
        session: Session,
        schedule_id: uuid.UUID,
    ) -> None:
        """
        Update schedule's next run time after execution.

        Args:
            session: Database session
            schedule_id: Schedule ID
        """
        schedule = session.get(WorkflowSchedule, schedule_id)
        if not schedule:
            return

        if schedule.is_active:
            next_run_at = self.calculate_next_run(schedule.cron_expression)
            schedule.next_run_at = next_run_at
            schedule.last_run_at = datetime.utcnow()
            session.add(schedule)
            session.commit()

    def get_due_schedules(
        self,
        session: Session,
        limit: int = 100,
    ) -> list[WorkflowSchedule]:
        """
        Get schedules that are due for execution.

        Args:
            session: Database session
            limit: Maximum number of schedules to return

        Returns:
            List of due schedules
        """
        now = datetime.utcnow()

        query = (
            select(WorkflowSchedule)
            .where(
                WorkflowSchedule.is_active == True,
                WorkflowSchedule.next_run_at <= now,
            )
            .limit(limit)
        )

        schedules = session.exec(query).all()
        return list(schedules)

    def trigger_scheduled_execution(
        self,
        session: Session,
        schedule_id: uuid.UUID,
    ) -> uuid.UUID:
        """
        Trigger a scheduled workflow execution.

        Args:
            session: Database session
            schedule_id: Schedule ID

        Returns:
            Execution ID

        Raises:
            SchedulerError: If schedule not found or workflow not found
        """
        schedule = session.get(WorkflowSchedule, schedule_id)
        if not schedule:
            raise SchedulerError(f"Schedule {schedule_id} not found")

        if not schedule.is_active:
            raise SchedulerError(f"Schedule {schedule_id} is not active")

        # Verify workflow exists and is active
        workflow = session.get(Workflow, schedule.workflow_id)
        if not workflow:
            raise SchedulerError(f"Workflow {schedule.workflow_id} not found")

        if not workflow.is_active:
            raise SchedulerError(f"Workflow {schedule.workflow_id} is not active")

        # Create execution
        execution = self.workflow_engine.create_execution(
            session,
            schedule.workflow_id,
            trigger_data={
                "trigger_type": "schedule",
                "schedule_id": str(schedule_id),
                "cron_expression": schedule.cron_expression,
            },
        )

        # Update schedule
        self.update_schedule_next_run(session, schedule_id)

        return execution.id

    def process_due_schedules(
        self,
        session: Session,
        limit: int = 100,
    ) -> list[uuid.UUID]:
        """
        Process all due schedules and trigger executions.

        Args:
            session: Database session
            limit: Maximum number of schedules to process

        Returns:
            List of execution IDs created
        """
        due_schedules = self.get_due_schedules(session, limit)
        execution_ids = []

        for schedule in due_schedules:
            try:
                execution_id = self.trigger_scheduled_execution(session, schedule.id)
                execution_ids.append(execution_id)
            except Exception as e:
                # Log error but continue processing other schedules
                # TODO: Add proper logging
                print(f"Error triggering schedule {schedule.id}: {e}")
                continue

        return execution_ids


# Default scheduler instance
default_scheduler = WorkflowScheduler()
