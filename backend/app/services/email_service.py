"""
Email Service

Provides unified email sending interface supporting both SMTP and Resend.
"""

import logging
from typing import Any

import emails  # type: ignore
from jinja2 import Template

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Unified email service supporting SMTP and Resend"""

    def __init__(self):
        self.use_resend = settings.USE_RESEND
        self.resend_api_key = settings.RESEND_API_KEY

    def send_email(
        self,
        *,
        email_to: str,
        subject: str = "",
        html_content: str = "",
        text_content: str | None = None,
    ) -> bool:
        """
        Send email using configured provider (Resend or SMTP).

        Args:
            email_to: Recipient email address
            subject: Email subject
            html_content: HTML email content
            text_content: Optional plain text content

        Returns:
            True if email sent successfully, False otherwise
        """
        if not settings.emails_enabled:
            logger.warning("Email service not enabled - missing configuration")
            return False

        try:
            if self.use_resend and self.resend_api_key:
                return self._send_via_resend(
                    email_to=email_to,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content,
                )
            else:
                return self._send_via_smtp(
                    email_to=email_to,
                    subject=subject,
                    html_content=html_content,
                )
        except Exception as e:
            logger.error(f"Failed to send email to {email_to}: {e}", exc_info=True)
            return False

    def _send_via_resend(
        self,
        *,
        email_to: str,
        subject: str,
        html_content: str,
        text_content: str | None = None,
    ) -> bool:
        """Send email via Resend API"""
        try:
            import resend

            resend.api_key = self.resend_api_key

            params: dict[str, Any] = {
                "from": f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>",
                "to": [email_to],
                "subject": subject,
                "html": html_content,
            }

            if text_content:
                params["text"] = text_content

            response = resend.Emails.send(params)

            if hasattr(response, "id"):
                logger.info(f"Email sent via Resend to {email_to}, id: {response.id}")
                return True
            else:
                logger.error(f"Resend API error: {response}")
                return False
        except ImportError:
            logger.error(
                "Resend package not installed. Install with: pip install resend"
            )
            return False
        except Exception as e:
            logger.error(f"Resend API error: {e}", exc_info=True)
            return False

    def _send_via_smtp(
        self,
        *,
        email_to: str,
        subject: str,
        html_content: str,
    ) -> bool:
        """Send email via SMTP"""
        try:
            message = emails.Message(
                subject=subject,
                html=html_content,
                mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
            )
            smtp_options: dict[str, Any] = {
                "host": settings.SMTP_HOST,
                "port": settings.SMTP_PORT,
            }
            if settings.SMTP_TLS:
                smtp_options["tls"] = True
            elif settings.SMTP_SSL:
                smtp_options["ssl"] = True
            if settings.SMTP_USER:
                smtp_options["user"] = settings.SMTP_USER
            if settings.SMTP_PASSWORD:
                smtp_options["password"] = settings.SMTP_PASSWORD

            response = message.send(to=email_to, smtp=smtp_options)
            logger.info(f"Email sent via SMTP to {email_to}, result: {response}")
            return True
        except Exception as e:
            logger.error(f"SMTP error: {e}", exc_info=True)
            return False

    def render_template(
        self,
        *,
        template_content: str,
        context: dict[str, Any],
    ) -> str:
        """
        Render email template with context variables.

        Args:
            template_content: Template HTML content (can be Jinja2 template)
            context: Template variables

        Returns:
            Rendered HTML content
        """
        try:
            template = Template(template_content)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Template rendering error: {e}", exc_info=True)
            return template_content  # Return original if rendering fails


# Global email service instance
email_service = EmailService()
