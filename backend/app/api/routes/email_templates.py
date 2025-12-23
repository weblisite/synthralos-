"""
Email Template Management API Routes

Handles CRUD operations for email templates.
"""

import uuid
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, status

from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.models import Message
from app.services.email_template_service import EmailTemplateService

router = APIRouter(prefix="/email-templates", tags=["email-templates"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_email_template(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    name: str = Body(...),
    slug: str | None = Body(None),
    subject: str = Body(...),
    html_content: str = Body(...),
    text_content: str | None = Body(None),
    category: str = Body("general"),
    variables: dict[str, Any] | None = Body(None),
) -> Any:
    """Create a new email template (admin only)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create email templates",
        )

    template_service = EmailTemplateService(session)
    template = template_service.create_template(
        name=name,
        slug=slug,
        subject=subject,
        html_content=html_content,
        text_content=text_content,
        category=category,
        variables=variables,
        created_by=current_user.id,
    )

    return template


@router.get("")
def list_email_templates(
    *,
    session: SessionDep,
    current_user: CurrentUser,  # noqa: ARG001
    category: str | None = None,
    is_active: bool | None = None,
    include_system: bool = True,
) -> Any:
    """List email templates"""
    template_service = EmailTemplateService(session)
    templates = template_service.list_templates(
        category=category,
        is_active=is_active,
        include_system=include_system,
    )
    return {"templates": templates, "count": len(templates)}


@router.get("/{template_id}")
def get_email_template(
    *,
    session: SessionDep,
    current_user: CurrentUser,  # noqa: ARG001
    template_id: uuid.UUID,
) -> Any:
    """Get email template by ID"""
    template_service = EmailTemplateService(session)
    template = template_service.get_template(template_id)

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
        )

    return template


@router.get("/slug/{slug}")
def get_email_template_by_slug(
    *,
    session: SessionDep,
    current_user: CurrentUser,  # noqa: ARG001
    slug: str,
) -> Any:
    """Get email template by slug"""
    template_service = EmailTemplateService(session)
    template = template_service.get_template_by_slug(slug)

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
        )

    return template


@router.patch("/{template_id}")
def update_email_template(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    template_id: uuid.UUID,
    name: str | None = Body(None),
    subject: str | None = Body(None),
    html_content: str | None = Body(None),
    text_content: str | None = Body(None),
    category: str | None = Body(None),
    variables: dict[str, Any] | None = Body(None),
    is_active: bool | None = Body(None),
) -> Any:
    """Update an email template (admin only)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update email templates",
        )

    template_service = EmailTemplateService(session)
    template = template_service.update_template(
        template_id=template_id,
        name=name,
        subject=subject,
        html_content=html_content,
        text_content=text_content,
        category=category,
        variables=variables,
        is_active=is_active,
    )

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
        )

    return template


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_email_template(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    template_id: uuid.UUID,
) -> None:
    """Delete an email template (admin only)"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete email templates",
        )

    template_service = EmailTemplateService(session)
    success = template_service.delete_template(template_id=template_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
        )


@router.post("/initialize-defaults", status_code=status.HTTP_200_OK)
def initialize_default_templates(
    *,
    session: SessionDep,
    _: Any = Depends(get_current_active_superuser),
) -> Message:
    """Initialize default email templates (superuser only)"""
    template_service = EmailTemplateService(session)
    template_service.initialize_default_templates()
    return Message(message="Default email templates initialized successfully")
