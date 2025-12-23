"""
Email Template Service

Manages email templates for platform notifications.
"""

import logging
import uuid
from typing import Any

from jinja2 import Template
from sqlmodel import Session, select

from app.models import EmailTemplate

logger = logging.getLogger(__name__)


class EmailTemplateService:
    """Service for email template management"""

    def __init__(self, session: Session):
        self.session = session

    def create_template(
        self,
        *,
        name: str,
        slug: str | None = None,
        subject: str,
        html_content: str,
        text_content: str | None = None,
        category: str = "general",
        variables: dict[str, Any] | None = None,
        is_system: bool = False,
        created_by: uuid.UUID | None = None,
    ) -> EmailTemplate:
        """Create a new email template"""
        if not slug:
            # Generate slug from name
            slug = name.lower().replace(" ", "-").replace("_", "-")
            slug = "".join(c for c in slug if c.isalnum() or c == "-")
            # Ensure uniqueness
            base_slug = slug
            counter = 1
            while self.session.exec(
                select(EmailTemplate).where(EmailTemplate.slug == slug)
            ).first():
                slug = f"{base_slug}-{counter}"
                counter += 1

        template = EmailTemplate(
            name=name,
            slug=slug,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            category=category,
            variables=variables or {},
            is_system=is_system,
            created_by=created_by,
        )

        self.session.add(template)
        self.session.commit()
        self.session.refresh(template)

        logger.info(f"Email template created: {template.id} ({template.slug})")
        return template

    def get_template(self, template_id: uuid.UUID) -> EmailTemplate | None:
        """Get template by ID"""
        return self.session.get(EmailTemplate, template_id)

    def get_template_by_slug(self, slug: str) -> EmailTemplate | None:
        """Get template by slug"""
        return self.session.exec(
            select(EmailTemplate).where(EmailTemplate.slug == slug)
        ).first()

    def list_templates(
        self,
        *,
        category: str | None = None,
        is_active: bool | None = None,
        include_system: bool = True,
    ) -> list[EmailTemplate]:
        """List email templates"""
        query = select(EmailTemplate)

        if category:
            query = query.where(EmailTemplate.category == category)

        if is_active is not None:
            query = query.where(EmailTemplate.is_active == is_active)

        if not include_system:
            query = query.where(EmailTemplate.is_system == False)  # noqa: E712

        return list(self.session.exec(query.order_by(EmailTemplate.name)).all())

    def update_template(
        self,
        *,
        template_id: uuid.UUID,
        name: str | None = None,
        subject: str | None = None,
        html_content: str | None = None,
        text_content: str | None = None,
        category: str | None = None,
        variables: dict[str, Any] | None = None,
        is_active: bool | None = None,
    ) -> EmailTemplate | None:
        """Update an email template"""
        template = self.session.get(EmailTemplate, template_id)
        if not template:
            return None

        if template.is_system:
            raise ValueError("Cannot modify system templates")

        if name is not None:
            template.name = name
        if subject is not None:
            template.subject = subject
        if html_content is not None:
            template.html_content = html_content
        if text_content is not None:
            template.text_content = text_content
        if category is not None:
            template.category = category
        if variables is not None:
            template.variables = variables
        if is_active is not None:
            template.is_active = is_active

        from datetime import datetime, timezone

        template.updated_at = datetime.now(timezone.utc)

        self.session.add(template)
        self.session.commit()
        self.session.refresh(template)

        logger.info(f"Email template updated: {template.id}")
        return template

    def delete_template(self, *, template_id: uuid.UUID) -> bool:
        """Delete an email template"""
        template = self.session.get(EmailTemplate, template_id)
        if not template:
            return False

        if template.is_system:
            raise ValueError("Cannot delete system templates")

        self.session.delete(template)
        self.session.commit()

        logger.info(f"Email template deleted: {template_id}")
        return True

    def render_template(
        self,
        *,
        template: EmailTemplate,
        field: str = "html_content",  # html_content or text_content
        context: dict[str, Any],
    ) -> str:
        """
        Render email template with context variables.

        Args:
            template: EmailTemplate instance
            field: Which field to render (html_content or text_content)
            context: Template variables

        Returns:
            Rendered content
        """
        content = getattr(template, field)
        if not content:
            return ""

        try:
            jinja_template = Template(content)
            return jinja_template.render(**context)
        except Exception as e:
            logger.error(f"Template rendering error: {e}", exc_info=True)
            return content  # Return original if rendering fails

    def initialize_default_templates(self) -> None:
        """Initialize default system email templates"""

        default_templates = [
            {
                "name": "Team Invitation",
                "slug": "team-invitation",
                "subject": "Invitation to join {{ team_name }} on {{ project_name }}",
                "html_content": """
                <html>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2>You've been invited to join {{ team_name }}</h2>
                    <p>Hello,</p>
                    <p>{{ inviter_name }} has invited you to join <strong>{{ team_name }}</strong> on {{ project_name }}.</p>
                    <p>Your role will be: <strong>{{ role }}</strong></p>
                    <p style="margin: 30px 0;">
                        <a href="{{ accept_url }}" style="background-color: #4CAF50; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">Accept Invitation</a>
                    </p>
                    <p>This invitation expires on {{ expires_at }}.</p>
                    <p>If you didn't expect this invitation, you can safely ignore this email.</p>
                </body>
                </html>
                """,
                "category": "invitation",
                "variables": {
                    "team_name": "string",
                    "inviter_name": "string",
                    "accept_url": "string",
                    "expires_at": "string",
                    "role": "string",
                    "project_name": "string",
                },
            },
            {
                "name": "Workflow Execution Started",
                "slug": "workflow-started",
                "subject": "Workflow '{{ workflow_name }}' has started",
                "html_content": """
                <html>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2>Workflow Execution Started</h2>
                    <p>Hello {{ user_name }},</p>
                    <p>Your workflow <strong>{{ workflow_name }}</strong> has started executing.</p>
                    <p><strong>Execution ID:</strong> {{ execution_id }}</p>
                    <p><a href="{{ execution_url }}">View Execution Details</a></p>
                </body>
                </html>
                """,
                "category": "workflow",
                "variables": {
                    "user_name": "string",
                    "workflow_name": "string",
                    "execution_id": "string",
                    "execution_url": "string",
                },
            },
            {
                "name": "Workflow Execution Completed",
                "slug": "workflow-completed",
                "subject": "Workflow '{{ workflow_name }}' completed successfully",
                "html_content": """
                <html>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2>Workflow Execution Completed</h2>
                    <p>Hello {{ user_name }},</p>
                    <p>Your workflow <strong>{{ workflow_name }}</strong> has completed successfully.</p>
                    <p><strong>Execution ID:</strong> {{ execution_id }}</p>
                    <p><strong>Duration:</strong> {{ duration }}</p>
                    <p><a href="{{ execution_url }}">View Execution Details</a></p>
                </body>
                </html>
                """,
                "category": "workflow",
                "variables": {
                    "user_name": "string",
                    "workflow_name": "string",
                    "execution_id": "string",
                    "duration": "string",
                    "execution_url": "string",
                },
            },
            {
                "name": "Workflow Execution Failed",
                "slug": "workflow-failed",
                "subject": "Workflow '{{ workflow_name }}' failed",
                "html_content": """
                <html>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2>Workflow Execution Failed</h2>
                    <p>Hello {{ user_name }},</p>
                    <p>Your workflow <strong>{{ workflow_name }}</strong> has failed.</p>
                    <p><strong>Execution ID:</strong> {{ execution_id }}</p>
                    <p><strong>Error:</strong> {{ error_message }}</p>
                    <p><a href="{{ execution_url }}">View Execution Details</a></p>
                </body>
                </html>
                """,
                "category": "workflow",
                "variables": {
                    "user_name": "string",
                    "workflow_name": "string",
                    "execution_id": "string",
                    "error_message": "string",
                    "execution_url": "string",
                },
            },
            {
                "name": "Human Approval Required",
                "slug": "human-approval",
                "subject": "Approval required for workflow '{{ workflow_name }}'",
                "html_content": """
                <html>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2>Approval Required</h2>
                    <p>Hello {{ user_name }},</p>
                    <p>Your workflow <strong>{{ workflow_name }}</strong> is waiting for your approval.</p>
                    <p><strong>Node:</strong> {{ node_name }}</p>
                    <p><strong>Execution ID:</strong> {{ execution_id }}</p>
                    <p><a href="{{ approval_url }}">Review and Approve</a></p>
                </body>
                </html>
                """,
                "category": "notification",
                "variables": {
                    "user_name": "string",
                    "workflow_name": "string",
                    "node_name": "string",
                    "execution_id": "string",
                    "approval_url": "string",
                },
            },
            {
                "name": "Welcome Email",
                "slug": "welcome",
                "subject": "Welcome to {{ project_name }}!",
                "html_content": """
                <html>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2>Welcome to {{ project_name }}!</h2>
                    <p>Hello {{ user_name }},</p>
                    <p>Thank you for joining {{ project_name }}. We're excited to have you on board!</p>
                    <p><a href="{{ dashboard_url }}">Get Started</a></p>
                </body>
                </html>
                """,
                "category": "system",
                "variables": {
                    "user_name": "string",
                    "project_name": "string",
                    "dashboard_url": "string",
                },
            },
        ]

        for template_data in default_templates:
            existing = self.get_template_by_slug(template_data["slug"])
            if not existing:
                self.create_template(
                    name=template_data["name"],
                    slug=template_data["slug"],
                    subject=template_data["subject"],
                    html_content=template_data["html_content"],
                    category=template_data["category"],
                    variables=template_data.get("variables", {}),
                    is_system=True,
                )


# Convenience function for getting service instance
def get_email_template_service(session: Session) -> EmailTemplateService:
    """Get email template service instance"""
    return EmailTemplateService(session)
