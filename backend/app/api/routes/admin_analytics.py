"""
Admin Analytics API Routes

Endpoints for admin-only analytics and cost tracking.
Requires is_superuser = True
"""

from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlmodel import func, select

from app.api.deps import SessionDep, get_current_active_superuser
from app.models import ModelCostLog, User, WorkflowExecution

router = APIRouter(prefix="/admin/analytics", tags=["admin", "analytics"])


@router.get("/costs")
def get_cost_analytics(
    session: SessionDep,
    current_user: User = Depends(get_current_active_superuser),
    date_from: datetime | None = Query(None, description="Start date (ISO format)"),
    date_to: datetime | None = Query(None, description="End date (ISO format)"),
    group_by: str = Query("day", description="Group by: day, week, month"),
) -> Any:
    """
    Get cost analytics (admin only).

    Aggregates costs from ModelCostLog and provides:
    - Total cost
    - Total executions
    - Average cost per execution
    - Cost breakdown by service/model
    - Cost trend over time
    """
    # Default to last 30 days if no date range specified
    if not date_to:
        date_to = datetime.utcnow()
    if not date_from:
        date_from = date_to - timedelta(days=30)

    # Base query for cost logs
    cost_query = select(ModelCostLog).where(
        ModelCostLog.created_at >= date_from,
        ModelCostLog.created_at <= date_to,
    )

    cost_logs = session.exec(cost_query).all()

    # Calculate total cost
    total_cost = sum(log.usd_cost for log in cost_logs)

    # Count total executions (workflow executions in the same period)
    execution_query = select(func.count(WorkflowExecution.id)).where(
        WorkflowExecution.started_at >= date_from,
        WorkflowExecution.started_at <= date_to,
    )
    total_executions = session.exec(execution_query).one() or 0

    # Calculate average cost per execution
    avg_cost_per_execution = (
        total_cost / total_executions if total_executions > 0 else 0.0
    )

    # Group costs by service/model
    cost_by_service: dict[str, dict[str, Any]] = {}
    for log in cost_logs:
        # Extract service name from model (e.g., "gpt-4" -> "openai", "claude-3" -> "anthropic")
        service = _extract_service_name(log.model)

        if service not in cost_by_service:
            cost_by_service[service] = {
                "service": service,
                "cost": 0.0,
                "executions": 0,
                "models": {},
            }

        cost_by_service[service]["cost"] += log.usd_cost

        # Track by model
        if log.model not in cost_by_service[service]["models"]:
            cost_by_service[service]["models"][log.model] = {
                "cost": 0.0,
                "tokens_input": 0,
                "tokens_output": 0,
            }

        cost_by_service[service]["models"][log.model]["cost"] += log.usd_cost
        cost_by_service[service]["models"][log.model][
            "tokens_input"
        ] += log.tokens_input
        cost_by_service[service]["models"][log.model][
            "tokens_output"
        ] += log.tokens_output

    # Count executions per service (approximate - based on cost logs)
    for service_data in cost_by_service.values():
        # Estimate executions based on cost log entries
        service_data["executions"] = len(
            [
                log
                for log in cost_logs
                if _extract_service_name(log.model) == service_data["service"]
            ]
        )

    # Generate cost trend
    cost_trend = _generate_cost_trend(session, date_from, date_to, group_by)

    return {
        "total_cost": round(total_cost, 2),
        "total_executions": total_executions,
        "avg_cost_per_execution": round(avg_cost_per_execution, 4),
        "cost_by_service": [
            {
                "service": data["service"],
                "cost": round(data["cost"], 2),
                "executions": data["executions"],
                "models": {
                    model: {
                        "cost": round(model_data["cost"], 2),
                        "tokens_input": model_data["tokens_input"],
                        "tokens_output": model_data["tokens_output"],
                    }
                    for model, model_data in data["models"].items()
                },
            }
            for data in cost_by_service.values()
        ],
        "cost_trend": cost_trend,
        "date_from": date_from.isoformat(),
        "date_to": date_to.isoformat(),
    }


def _extract_service_name(model: str) -> str:
    """Extract service name from model identifier."""
    model_lower = model.lower()

    if "gpt" in model_lower or "openai" in model_lower:
        return "openai"
    elif "claude" in model_lower or "anthropic" in model_lower:
        return "anthropic"
    elif "gemini" in model_lower or "google" in model_lower:
        return "google"
    elif "llama" in model_lower or "meta" in model_lower:
        return "meta"
    elif "mistral" in model_lower:
        return "mistral"
    else:
        return "other"


def _generate_cost_trend(
    session: SessionDep,
    date_from: datetime,
    date_to: datetime,
    group_by: str,
) -> list[dict[str, Any]]:
    """Generate cost trend data grouped by time period."""
    trend = []

    # Determine time delta based on group_by
    if group_by == "day":
        delta = timedelta(days=1)
        date_format = "%Y-%m-%d"
    elif group_by == "week":
        delta = timedelta(weeks=1)
        date_format = "%Y-W%W"
    elif group_by == "month":
        delta = timedelta(days=30)
        date_format = "%Y-%m"
    else:
        delta = timedelta(days=1)
        date_format = "%Y-%m-%d"

    current_date = date_from
    while current_date <= date_to:
        period_end = min(current_date + delta, date_to)

        # Query costs for this period
        period_query = select(func.sum(ModelCostLog.usd_cost)).where(
            ModelCostLog.created_at >= current_date,
            ModelCostLog.created_at < period_end,
        )
        period_cost = session.exec(period_query).one() or 0.0

        # Query executions for this period
        execution_query = select(func.count(WorkflowExecution.id)).where(
            WorkflowExecution.started_at >= current_date,
            WorkflowExecution.started_at < period_end,
        )
        period_executions = session.exec(execution_query).one() or 0

        trend.append(
            {
                "date": current_date.strftime(date_format),
                "cost": round(period_cost, 2),
                "executions": period_executions,
            }
        )

        current_date = period_end

    return trend
