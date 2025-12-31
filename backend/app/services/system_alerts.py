"""
System Alert Service

Handles creation and management of system-level alerts for the admin dashboard.
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy.exc import OperationalError
from sqlmodel import Session, select

from app.models import SystemAlert

logger = logging.getLogger(__name__)


def create_system_alert(
    session: Session,
    alert_type: str,
    severity: str,
    title: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> SystemAlert:
    """
    Create a system alert.

    Args:
        session: Database session
        alert_type: Type of alert (e.g., 'circuit_breaker', 'database_error')
        severity: Severity level ('info', 'warning', 'error', 'critical')
        title: Alert title
        message: Alert message
        details: Additional context/metadata

    Returns:
        Created SystemAlert instance
    """
    # Check if there's already an unresolved alert of the same type
    # This prevents duplicate alerts for the same issue
    existing_alert = session.exec(
        select(SystemAlert)
        .where(SystemAlert.alert_type == alert_type)
        .where(SystemAlert.is_resolved == False)
        .order_by(SystemAlert.created_at.desc())
    ).first()

    # If there's a recent unresolved alert (within last 5 minutes), update it instead
    if existing_alert and (datetime.utcnow() - existing_alert.created_at) < timedelta(
        minutes=5
    ):
        existing_alert.message = message
        existing_alert.details = details or {}
        existing_alert.updated_at = datetime.utcnow()
        session.add(existing_alert)
        session.commit()
        session.refresh(existing_alert)
        logger.info(f"Updated existing system alert: {alert_type}")
        return existing_alert

    # Create new alert
    alert = SystemAlert(
        alert_type=alert_type,
        severity=severity,
        title=title,
        message=message,
        details=details or {},
    )
    session.add(alert)
    session.commit()
    session.refresh(alert)
    logger.info(f"Created system alert: {alert_type} - {title}")
    return alert


def detect_circuit_breaker_error(error: Exception) -> bool:
    """
    Detect if an error is a circuit breaker error.

    Args:
        error: Exception to check

    Returns:
        True if error is a circuit breaker error
    """
    error_str = str(error).lower()
    return (
        "circuit breaker" in error_str
        or "too many authentication errors" in error_str
        or "connection failed" in error_str
    )


def handle_database_error(session: Session, error: Exception) -> SystemAlert | None:
    """
    Handle database connection errors and create appropriate system alerts.

    Args:
        session: Database session
        error: Database error exception

    Returns:
        Created SystemAlert if error was handled, None otherwise
    """
    error_str = str(error)

    # Check for circuit breaker errors
    if detect_circuit_breaker_error(error):
        return create_system_alert(
            session=session,
            alert_type="circuit_breaker",
            severity="critical",
            title="Database Circuit Breaker Open",
            message=(
                "Database connection circuit breaker is open due to too many "
                "authentication errors. Connections are temporarily blocked. "
                "The circuit breaker will automatically reset in 1-5 minutes."
            ),
            details={
                "error": error_str,
                "error_type": type(error).__name__,
                "recommendation": (
                    "Check database credentials and connection string. "
                    "Ensure correct port (6543 for pooler, 5432 for direct)."
                ),
            },
        )

    # Check for other database connection errors
    if isinstance(error, OperationalError):
        return create_system_alert(
            session=session,
            alert_type="database_error",
            severity="error",
            title="Database Connection Error",
            message=f"Database connection failed: {error_str}",
            details={
                "error": error_str,
                "error_type": type(error).__name__,
            },
        )

    return None


def resolve_alert(
    session: Session, alert_id: str, resolved_by: str | None = None
) -> SystemAlert | None:
    """
    Mark a system alert as resolved.

    Args:
        session: Database session
        alert_id: Alert ID to resolve
        resolved_by: User ID who resolved the alert (optional)

    Returns:
        Updated SystemAlert instance or None if not found
    """
    import uuid

    try:
        alert_uuid = uuid.UUID(alert_id)
    except ValueError:
        logger.error(f"Invalid alert ID: {alert_id}")
        return None

    alert = session.get(SystemAlert, alert_uuid)
    if not alert:
        logger.warning(f"Alert {alert_id} not found")
        return None

    alert.is_resolved = True
    alert.resolved_at = datetime.utcnow()
    if resolved_by:
        try:
            alert.resolved_by = uuid.UUID(resolved_by)
        except ValueError:
            logger.warning(f"Invalid resolved_by user ID: {resolved_by}")

    session.add(alert)
    session.commit()
    session.refresh(alert)
    logger.info(f"Resolved system alert: {alert_id}")
    return alert
