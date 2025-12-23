"""
Workflow Email Notification Service

Sends email notifications for workflow execution events.
"""

import logging

from sqlmodel import Session, select

from app.core.config import settings
from app.models import User, Workflow, WorkflowExecution
from app.services.email_service import email_service
from app.services.email_template_service import EmailTemplateService

logger = logging.getLogger(__name__)


class WorkflowNotificationService:
    """Service for sending workflow execution email notifications"""

    def __init__(self, session: Session):
        self.session = session
        self.template_service = EmailTemplateService(session)

    def send_execution_started_notification(
        self,
        *,
        execution: WorkflowExecution,
        workflow: Workflow,
    ) -> None:
        """Send email notification when workflow execution starts"""
        try:
            # Get workflow owner
            owner = self.session.get(User, workflow.owner_id)
            if not owner:
                logger.warning(f"Workflow owner {workflow.owner_id} not found")
                return

            # Get template
            template = self.template_service.get_template_by_slug("workflow-started")
            if not template or not template.is_active:
                logger.debug(
                    "Workflow started template not found or inactive, skipping notification"
                )
                return

            # Build context
            execution_url = (
                f"{settings.FRONTEND_HOST}/workflows?execution_id={execution.id}"
            )
            context = {
                "user_name": owner.full_name or owner.email.split("@")[0],
                "workflow_name": workflow.name,
                "execution_id": str(execution.id),
                "execution_url": execution_url,
                "project_name": settings.PROJECT_NAME,
            }

            # Render and send email
            subject = self.template_service.render_template(
                template=template, field="subject", context=context
            )
            html_content = self.template_service.render_template(
                template=template, field="html_content", context=context
            )

            email_service.send_email(
                email_to=owner.email,
                subject=subject,
                html_content=html_content,
            )

            logger.info(
                f"Sent execution started notification to {owner.email} for execution {execution.id}"
            )
        except Exception as e:
            logger.error(
                f"Failed to send execution started notification: {e}", exc_info=True
            )

    def send_execution_completed_notification(
        self,
        *,
        execution: WorkflowExecution,
        workflow: Workflow,
    ) -> None:
        """Send email notification when workflow execution completes successfully"""
        try:
            # Get workflow owner
            owner = self.session.get(User, workflow.owner_id)
            if not owner:
                logger.warning(f"Workflow owner {workflow.owner_id} not found")
                return

            # Get template
            template = self.template_service.get_template_by_slug("workflow-completed")
            if not template or not template.is_active:
                logger.debug(
                    "Workflow completed template not found or inactive, skipping notification"
                )
                return

            # Calculate duration
            duration = "Unknown"
            if execution.started_at and execution.completed_at:
                delta = execution.completed_at - execution.started_at
                total_seconds = int(delta.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60
                if hours > 0:
                    duration = f"{hours}h {minutes}m {seconds}s"
                elif minutes > 0:
                    duration = f"{minutes}m {seconds}s"
                else:
                    duration = f"{seconds}s"

            # Build context
            execution_url = (
                f"{settings.FRONTEND_HOST}/workflows?execution_id={execution.id}"
            )
            context = {
                "user_name": owner.full_name or owner.email.split("@")[0],
                "workflow_name": workflow.name,
                "execution_id": str(execution.id),
                "duration": duration,
                "execution_url": execution_url,
                "project_name": settings.PROJECT_NAME,
            }

            # Render and send email
            subject = self.template_service.render_template(
                template=template, field="subject", context=context
            )
            html_content = self.template_service.render_template(
                template=template, field="html_content", context=context
            )

            email_service.send_email(
                email_to=owner.email,
                subject=subject,
                html_content=html_content,
            )

            logger.info(
                f"Sent execution completed notification to {owner.email} for execution {execution.id}"
            )

            # Also notify team members if workflow belongs to a team
            self._notify_team_members(
                execution=execution, workflow=workflow, event_type="completed"
            )
        except Exception as e:
            logger.error(
                f"Failed to send execution completed notification: {e}", exc_info=True
            )

    def send_execution_failed_notification(
        self,
        *,
        execution: WorkflowExecution,
        workflow: Workflow,
        error_message: str,
    ) -> None:
        """Send email notification when workflow execution fails"""
        try:
            # Get workflow owner
            owner = self.session.get(User, workflow.owner_id)
            if not owner:
                logger.warning(f"Workflow owner {workflow.owner_id} not found")
                return

            # Get template
            template = self.template_service.get_template_by_slug("workflow-failed")
            if not template or not template.is_active:
                logger.debug(
                    "Workflow failed template not found or inactive, skipping notification"
                )
                return

            # Build context
            execution_url = (
                f"{settings.FRONTEND_HOST}/workflows?execution_id={execution.id}"
            )
            context = {
                "user_name": owner.full_name or owner.email.split("@")[0],
                "workflow_name": workflow.name,
                "execution_id": str(execution.id),
                "error_message": error_message or "Unknown error",
                "execution_url": execution_url,
                "project_name": settings.PROJECT_NAME,
            }

            # Render and send email
            subject = self.template_service.render_template(
                template=template, field="subject", context=context
            )
            html_content = self.template_service.render_template(
                template=template, field="html_content", context=context
            )

            email_service.send_email(
                email_to=owner.email,
                subject=subject,
                html_content=html_content,
            )

            logger.info(
                f"Sent execution failed notification to {owner.email} for execution {execution.id}"
            )

            # Also notify team members if workflow belongs to a team
            self._notify_team_members(
                execution=execution,
                workflow=workflow,
                event_type="failed",
                error_message=error_message,
            )
        except Exception as e:
            logger.error(
                f"Failed to send execution failed notification: {e}", exc_info=True
            )

    def _notify_team_members(
        self,
        *,
        execution: WorkflowExecution,
        workflow: Workflow,
        event_type: str,
        error_message: str | None = None,
    ) -> None:
        """Notify team members about workflow execution events"""
        try:
            # Find teams that the workflow owner belongs to
            # For now, we'll notify all teams the owner is part of
            # In the future, workflows could be associated with specific teams
            try:
                from app.models import TeamMember

                owner_teams = self.session.exec(
                    select(TeamMember).where(TeamMember.user_id == workflow.owner_id)
                ).all()

                if not owner_teams:
                    return
            except ImportError:
                # TeamMember model might not be available in all environments
                logger.debug(
                    "TeamMember model not available, skipping team notifications"
                )
                return

            # Get template based on event type
            template_slug = f"workflow-{event_type}"
            template = self.template_service.get_template_by_slug(template_slug)
            if not template or not template.is_active:
                return

            # Notify team members (excluding owner, already notified)
            for team_member in owner_teams:
                member_user = self.session.get(User, team_member.user_id)
                if not member_user or member_user.id == workflow.owner_id:
                    continue

                # Build context
                execution_url = (
                    f"{settings.FRONTEND_HOST}/workflows?execution_id={execution.id}"
                )
                context = {
                    "user_name": member_user.full_name
                    or member_user.email.split("@")[0],
                    "workflow_name": workflow.name,
                    "execution_id": str(execution.id),
                    "execution_url": execution_url,
                    "project_name": settings.PROJECT_NAME,
                }

                if event_type == "failed" and error_message:
                    context["error_message"] = error_message
                elif event_type == "completed":
                    # Calculate duration
                    duration = "Unknown"
                    if execution.started_at and execution.completed_at:
                        delta = execution.completed_at - execution.started_at
                        total_seconds = int(delta.total_seconds())
                        hours = total_seconds // 3600
                        minutes = (total_seconds % 3600) // 60
                        seconds = total_seconds % 60
                        if hours > 0:
                            duration = f"{hours}h {minutes}m {seconds}s"
                        elif minutes > 0:
                            duration = f"{minutes}m {seconds}s"
                        else:
                            duration = f"{seconds}s"
                    context["duration"] = duration

                # Render and send email
                subject = self.template_service.render_template(
                    template=template, field="subject", context=context
                )
                html_content = self.template_service.render_template(
                    template=template, field="html_content", context=context
                )

                email_service.send_email(
                    email_to=member_user.email,
                    subject=subject,
                    html_content=html_content,
                )

                logger.info(
                    f"Sent {event_type} notification to team member {member_user.email} for execution {execution.id}"
                )
        except Exception as e:
            logger.error(f"Failed to notify team members: {e}", exc_info=True)


def send_workflow_notification(
    session: Session,
    *,
    execution: WorkflowExecution,
    workflow: Workflow,
    event_type: str,
    error_message: str | None = None,
) -> None:
    """
    Convenience function to send workflow notifications.

    Args:
        session: Database session
        execution: Workflow execution
        workflow: Workflow
        event_type: Event type (started, completed, failed)
        error_message: Error message (for failed events)
    """
    notification_service = WorkflowNotificationService(session)

    if event_type == "started":
        notification_service.send_execution_started_notification(
            execution=execution,
            workflow=workflow,
        )
    elif event_type == "completed":
        notification_service.send_execution_completed_notification(
            execution=execution,
            workflow=workflow,
        )
    elif event_type == "failed":
        notification_service.send_execution_failed_notification(
            execution=execution,
            workflow=workflow,
            error_message=error_message or "Unknown error",
        )
