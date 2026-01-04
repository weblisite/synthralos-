"""
Admin System Management API Routes

Endpoints for system health, metrics, and platform management.
Requires is_superuser = True
"""

from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends
from sqlmodel import func, select

from app.api.deps import SessionDep, get_current_active_superuser
from app.core.config import settings
from app.models import (
    BrowserSession,
    CodeToolRegistry,
    Connector,
    OCRJob,
    OSINTStream,
    PlatformSettings,
    RAGIndex,
    ScrapeJob,
    SystemAlert,
    User,
    Workflow,
    WorkflowExecution,
)

router = APIRouter(prefix="/admin/system", tags=["admin", "system"])


@router.get("/health")
def get_system_health(
    session: SessionDep,
    _current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Get system health status (admin only).

    Returns:
    - Database connectivity status
    - Service availability
    - System metrics
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {},
        "database": {},
        "checks": [],
    }

    # Check database connectivity
    try:
        # Simple query to test database
        test_query = select(func.count(User.id))
        user_count = session.exec(test_query).one()
        health_status["database"]["status"] = "connected"
        health_status["database"]["user_count"] = user_count
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["database"]["status"] = "error"
        health_status["database"]["error"] = str(e)
        health_status["checks"].append(
            {
                "name": "database",
                "status": "failed",
                "message": f"Database connection failed: {str(e)}",
            }
        )
        # Create system alert for database errors
        try:
            from app.services.system_alerts import handle_database_error

            handle_database_error(session, e)
        except Exception as alert_error:
            # Don't fail if alert creation fails
            import logging

            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to create system alert: {alert_error}")

    # Get unresolved alerts count
    try:
        unresolved_alerts = (
            session.exec(
                select(func.count(SystemAlert.id)).where(
                    SystemAlert.is_resolved.is_(False)
                )
            ).one()
            or 0
        )
        health_status["unresolved_alerts"] = unresolved_alerts
        if unresolved_alerts > 0:
            health_status["status"] = "degraded"
    except Exception:
        # If SystemAlert table doesn't exist yet, skip
        health_status["unresolved_alerts"] = 0

    # Check service availability (based on configuration)
    services = {
        "supabase": bool(settings.SUPABASE_URL and settings.SUPABASE_ANON_KEY),
        "redis": bool(settings.REDIS_URL),
        "chromadb": bool(settings.CHROMADB_PATH),
        "openai": bool(settings.OPENAI_API_KEY),
        "anthropic": bool(settings.ANTHROPIC_API_KEY),
        "google": bool(settings.GOOGLE_API_KEY),
        "nango": bool(
            getattr(settings, "NANGO_BASE_URL", None)
            or getattr(settings, "NANGO_URL", None)
        )
        and bool(getattr(settings, "NANGO_SECRET_KEY", "")),
    }

    health_status["services"] = services

    # Count available services
    available_services = sum(1 for available in services.values() if available)
    total_services = len(services)

    if available_services < total_services:
        health_status["status"] = "degraded"

    # Add service checks
    for service_name, is_available in services.items():
        health_status["checks"].append(
            {
                "name": service_name,
                "status": "available" if is_available else "unavailable",
                "message": f"{service_name} is {'configured' if is_available else 'not configured'}",
            }
        )

    return health_status


@router.get("/metrics")
def get_system_metrics(
    session: SessionDep,
    _current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Get system-wide metrics (admin only).

    Returns:
    - User statistics
    - Workflow statistics
    - Execution statistics
    - Resource usage statistics
    """
    # User statistics
    total_users = session.exec(select(func.count(User.id))).one() or 0
    active_users = (
        session.exec(select(func.count(User.id)).where(User.is_active.is_(True))).one()
        or 0
    )
    admin_users = (
        session.exec(
            select(func.count(User.id)).where(User.is_superuser.is_(True))
        ).one()
        or 0
    )

    # Workflow statistics
    total_workflows = session.exec(select(func.count(Workflow.id))).one() or 0
    active_workflows = (
        session.exec(
            select(func.count(Workflow.id)).where(Workflow.is_active.is_(True))
        ).one()
        or 0
    )

    # Execution statistics (last 24 hours)
    last_24h = datetime.utcnow() - timedelta(hours=24)
    executions_24h = (
        session.exec(
            select(func.count(WorkflowExecution.id)).where(
                WorkflowExecution.started_at >= last_24h
            )
        ).one()
        or 0
    )

    # Execution statistics (all time)
    total_executions = session.exec(select(func.count(WorkflowExecution.id))).one() or 0
    completed_executions = (
        session.exec(
            select(func.count(WorkflowExecution.id)).where(
                WorkflowExecution.status == "completed"
            )
        ).one()
        or 0
    )
    failed_executions = (
        session.exec(
            select(func.count(WorkflowExecution.id)).where(
                WorkflowExecution.status == "failed"
            )
        ).one()
        or 0
    )
    running_executions = (
        session.exec(
            select(func.count(WorkflowExecution.id)).where(
                WorkflowExecution.status == "running"
            )
        ).one()
        or 0
    )

    # Resource statistics
    total_rag_indexes = session.exec(select(func.count(RAGIndex.id))).one() or 0
    total_connectors = session.exec(select(func.count(Connector.id))).one() or 0
    total_ocr_jobs = session.exec(select(func.count(OCRJob.id))).one() or 0
    total_scrape_jobs = session.exec(select(func.count(ScrapeJob.id))).one() or 0
    total_browser_sessions = (
        session.exec(select(func.count(BrowserSession.id))).one() or 0
    )
    total_osint_streams = session.exec(select(func.count(OSINTStream.id))).one() or 0
    total_code_tools = session.exec(select(func.count(CodeToolRegistry.id))).one() or 0

    # Calculate success rate
    success_rate = (
        (completed_executions / total_executions * 100) if total_executions > 0 else 0.0
    )

    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "admins": admin_users,
            "regular": total_users - admin_users,
        },
        "workflows": {
            "total": total_workflows,
            "active": active_workflows,
            "inactive": total_workflows - active_workflows,
        },
        "executions": {
            "total": total_executions,
            "last_24h": executions_24h,
            "completed": completed_executions,
            "failed": failed_executions,
            "running": running_executions,
            "success_rate": round(success_rate, 2),
        },
        "resources": {
            "rag_indexes": total_rag_indexes,
            "connectors": total_connectors,
            "ocr_jobs": total_ocr_jobs,
            "scrape_jobs": total_scrape_jobs,
            "browser_sessions": total_browser_sessions,
            "osint_streams": total_osint_streams,
            "code_tools": total_code_tools,
        },
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/activity")
def get_recent_activity(
    session: SessionDep,
    _current_user: User = Depends(get_current_active_superuser),
    limit: int = 50,
) -> Any:
    """
    Get recent platform activity (admin only).

    Returns:
    - Recent workflow executions
    - Recent user registrations
    - Recent connector registrations
    """
    # Get recent executions (last 24 hours)
    last_24h = datetime.utcnow() - timedelta(hours=24)

    recent_executions = session.exec(
        select(WorkflowExecution)
        .where(WorkflowExecution.started_at >= last_24h)
        .order_by(WorkflowExecution.started_at.desc())
        .limit(limit)
    ).all()

    # Note: User model doesn't have created_at, so we'll skip recent users for now

    # Format activity log
    activity = []

    for execution in recent_executions:
        activity.append(
            {
                "type": "execution",
                "id": str(execution.id),
                "execution_id": execution.execution_id,
                "workflow_id": str(execution.workflow_id),
                "status": execution.status,
                "timestamp": execution.started_at.isoformat(),
                "description": f"Workflow execution {execution.status}",
            }
        )

    return {
        "activity": activity[:limit],
        "total": len(activity),
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/alerts")
def get_system_alerts(
    session: SessionDep,
    _current_user: User = Depends(get_current_active_superuser),
    limit: int = 50,
    resolved: bool | None = None,
    severity: str | None = None,
) -> Any:
    """
    Get system alerts (admin only).

    Args:
        session: Database session
        current_user: Current admin user
        limit: Maximum number of alerts to return
        resolved: Filter by resolved status (True/False/None for all)
        severity: Filter by severity level

    Returns:
        List of system alerts
    """
    query = select(SystemAlert)

    # Apply filters
    if resolved is not None:
        query = query.where(SystemAlert.is_resolved == resolved)
    if severity:
        query = query.where(SystemAlert.severity == severity)

    # Order by created_at descending (newest first)
    query = query.order_by(SystemAlert.created_at.desc())

    alerts = session.exec(query.limit(limit)).all()

    return {
        "alerts": [
            {
                "id": str(alert.id),
                "alert_type": alert.alert_type,
                "severity": alert.severity,
                "title": alert.title,
                "message": alert.message,
                "details": alert.details,
                "is_resolved": alert.is_resolved,
                "resolved_at": alert.resolved_at.isoformat()
                if alert.resolved_at
                else None,
                "resolved_by": str(alert.resolved_by) if alert.resolved_by else None,
                "created_at": alert.created_at.isoformat(),
                "updated_at": alert.updated_at.isoformat(),
            }
            for alert in alerts
        ],
        "total": len(alerts),
        "unresolved_count": session.exec(
            select(func.count(SystemAlert.id)).where(SystemAlert.is_resolved.is_(False))
        ).one()
        or 0,
    }


@router.post("/alerts/{alert_id}/resolve", status_code=200)
def resolve_system_alert(
    alert_id: str,
    session: SessionDep,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Resolve a system alert (admin only).

    Args:
        alert_id: Alert ID to resolve
        session: Database session
        current_user: Current admin user

    Returns:
        Updated alert details
    """
    from app.services.system_alerts import resolve_alert

    alert = resolve_alert(session, alert_id, str(current_user.id))
    if not alert:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Alert {alert_id} not found"
        )

    return {
        "id": str(alert.id),
        "alert_type": alert.alert_type,
        "severity": alert.severity,
        "title": alert.title,
        "message": alert.message,
        "is_resolved": alert.is_resolved,
        "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
        "resolved_by": str(alert.resolved_by) if alert.resolved_by else None,
    }


@router.get("/settings")
def get_platform_settings(
    session: SessionDep,
    _current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Get platform settings (admin only).

    Returns:
        Platform settings as key-value pairs
    """
    settings = session.exec(select(PlatformSettings)).all()

    # Convert to dictionary format
    result = {}
    for setting in settings:
        # Extract value from dict if it's stored as {"value": ...}
        value = setting.value
        if isinstance(value, dict) and "value" in value:
            value = value["value"]

        result[setting.key] = {
            "value": value,
            "description": setting.description,
            "updated_at": setting.updated_at.isoformat(),
            "updated_by": str(setting.updated_by) if setting.updated_by else None,
        }

    # Return default settings if none exist
    if not result:
        return {
            "platform_name": {"value": "SynthralOS", "description": None},
            "maintenance_mode": {"value": False, "description": None},
            "registration_enabled": {"value": True, "description": None},
            "max_users": {"value": 1000, "description": None},
            "max_workflows_per_user": {"value": 100, "description": None},
            "default_execution_timeout": {"value": 300, "description": None},
            "maintenance_message": {"value": "", "description": None},
        }

    return result


@router.put("/settings")
def update_platform_settings(
    settings: dict[str, Any],
    session: SessionDep,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Update platform settings (admin only).

    Args:
        settings: Dictionary of settings to update (key-value pairs)
        session: Database session
        current_user: Current admin user

    Returns:
        Updated settings
    """
    updated_settings = {}

    for key, value in settings.items():
        # Get existing setting or create new one
        existing = session.exec(
            select(PlatformSettings).where(PlatformSettings.key == key)
        ).first()

        # Store value as dict (for consistency)
        value_dict = value if isinstance(value, dict) else {"value": value}

        if existing:
            existing.value = value_dict
            existing.updated_by = current_user.id
            existing.updated_at = datetime.utcnow()
            session.add(existing)
            updated_settings[key] = {
                "value": existing.value.get("value")
                if isinstance(existing.value, dict) and "value" in existing.value
                else existing.value,
                "description": existing.description,
                "updated_at": existing.updated_at.isoformat(),
                "updated_by": str(existing.updated_by),
            }
        else:
            new_setting = PlatformSettings(
                key=key,
                value=value_dict,
                updated_by=current_user.id,
            )
            session.add(new_setting)
            updated_settings[key] = {
                "value": value_dict.get("value")
                if isinstance(value_dict, dict) and "value" in value_dict
                else value_dict,
                "description": new_setting.description,
                "updated_at": new_setting.updated_at.isoformat(),
                "updated_by": str(new_setting.updated_by),
            }

    session.commit()

    # Log admin action
    from app.observability.wazuh import default_wazuh_client

    default_wazuh_client.log_audit_event(
        action="update_platform_settings",
        resource="platform_settings",
        user_id=str(current_user.id),
        success=True,
        metadata={"updated_keys": list(settings.keys())},
    )

    return {"settings": updated_settings, "message": "Settings updated successfully"}
