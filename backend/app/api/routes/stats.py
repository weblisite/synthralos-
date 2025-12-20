"""
Statistics API Routes

Endpoints for dashboard statistics and metrics.
"""

from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    AgentTask,
    BrowserSession,
    CodeExecution,
    Connector,
    OCRJob,
    OSINTStream,
    RAGIndex,
    RAGQuery,
    ScrapeJob,
    Workflow,
    WorkflowExecution,
)

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/dashboard")
def get_dashboard_stats(
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Get comprehensive dashboard statistics for the current user.

    Returns:
    - Workflow statistics
    - Agent task statistics
    - Connector statistics
    - RAG statistics
    - OCR statistics
    - Scraping statistics
    - Browser statistics
    - OSINT statistics
    - Code execution statistics
    - Recent activity
    """
    now = datetime.utcnow()
    last_24h = now - timedelta(days=1)
    last_7d = now - timedelta(days=7)
    last_30d = now - timedelta(days=30)

    # Workflow Statistics
    total_workflows = session.exec(
        select(func.count(Workflow.id)).where(Workflow.owner_id == current_user.id)
    ).one()

    active_workflows = session.exec(
        select(func.count(Workflow.id)).where(
            Workflow.owner_id == current_user.id,
            Workflow.is_active == True,
        )
    ).one()

    # Workflow Executions (last 30 days)
    recent_executions = session.exec(
        select(WorkflowExecution)
        .join(Workflow)
        .where(
            Workflow.owner_id == current_user.id,
            WorkflowExecution.started_at >= last_30d,
        )
        .order_by(WorkflowExecution.started_at.desc())
        .limit(10)
    ).all()

    # Get execution stats
    all_executions = session.exec(
        select(WorkflowExecution)
        .join(Workflow)
        .where(
            Workflow.owner_id == current_user.id,
            WorkflowExecution.started_at >= last_30d,
        )
    ).all()

    execution_stats = {
        "total": len(all_executions),
        "completed": sum(1 for e in all_executions if e.status == "completed"),
        "failed": sum(1 for e in all_executions if e.status == "failed"),
        "running": sum(1 for e in all_executions if e.status == "running"),
    }

    # Agent Task Statistics
    all_agent_tasks = session.exec(
        select(AgentTask).where(AgentTask.started_at >= last_30d)
    ).all()

    agent_stats = {
        "total": len(all_agent_tasks),
        "completed": sum(1 for t in all_agent_tasks if t.status == "completed"),
        "failed": sum(1 for t in all_agent_tasks if t.status == "failed"),
        "running": sum(1 for t in all_agent_tasks if t.status == "running"),
    }

    # Connector Statistics
    total_connectors = session.exec(select(func.count(Connector.id))).one()

    active_connectors = session.exec(
        select(func.count(Connector.id)).where(Connector.status == "stable")
    ).one()

    # RAG Statistics
    rag_indexes = session.exec(
        select(func.count(RAGIndex.id)).where(RAGIndex.owner_id == current_user.id)
    ).one()

    rag_queries_30d = session.exec(
        select(func.count(RAGQuery.id))
        .join(RAGIndex)
        .where(
            RAGIndex.owner_id == current_user.id,
            RAGQuery.created_at >= last_30d,
        )
    ).one()

    # OCR Statistics
    all_ocr_jobs = session.exec(
        select(OCRJob).where(OCRJob.started_at >= last_30d)
    ).all()

    ocr_stats = {
        "total": len(all_ocr_jobs),
        "completed": sum(1 for j in all_ocr_jobs if j.status == "completed"),
        "failed": sum(1 for j in all_ocr_jobs if j.status == "failed"),
    }

    # Scraping Statistics
    all_scrape_jobs = session.exec(
        select(ScrapeJob).where(ScrapeJob.started_at >= last_30d)
    ).all()

    scraping_stats = {
        "total": len(all_scrape_jobs),
        "completed": sum(1 for j in all_scrape_jobs if j.status == "completed"),
        "failed": sum(1 for j in all_scrape_jobs if j.status == "failed"),
    }

    # Browser Statistics
    browser_sessions_30d = session.exec(
        select(func.count(BrowserSession.id)).where(
            BrowserSession.started_at >= last_30d
        )
    ).one()

    # OSINT Statistics
    osint_streams = session.exec(select(func.count(OSINTStream.id))).one()

    # Code Execution Statistics
    all_code_executions = session.exec(
        select(CodeExecution).where(CodeExecution.started_at >= last_30d)
    ).all()

    code_stats = {
        "total": len(all_code_executions),
        "completed": sum(1 for e in all_code_executions if e.status == "completed"),
        "failed": sum(1 for e in all_code_executions if e.status == "failed"),
    }

    # Recent Activity (last 10 items)
    recent_activity = []

    # Add recent workflow executions
    for exec in recent_executions[:5]:
        workflow = session.get(Workflow, exec.workflow_id)
        recent_activity.append(
            {
                "type": "workflow_execution",
                "id": str(exec.id),
                "title": workflow.name if workflow else "Unknown Workflow",
                "status": exec.status,
                "timestamp": exec.started_at.isoformat(),
            }
        )

    # Add recent agent tasks
    recent_agent_tasks = session.exec(
        select(AgentTask)
        .where(AgentTask.started_at >= last_7d)
        .order_by(AgentTask.started_at.desc())
        .limit(5)
    ).all()

    for task in recent_agent_tasks:
        recent_activity.append(
            {
                "type": "agent_task",
                "id": str(task.id),
                "title": f"{task.agent_framework} - {task.task_type}",
                "status": task.status,
                "timestamp": task.started_at.isoformat(),
            }
        )

    # Sort by timestamp and take top 10
    recent_activity.sort(key=lambda x: x["timestamp"], reverse=True)
    recent_activity = recent_activity[:10]

    return {
        "workflows": {
            "total": total_workflows or 0,
            "active": active_workflows or 0,
            "inactive": (total_workflows or 0) - (active_workflows or 0),
        },
        "executions": {
            "total_30d": execution_stats["total"],
            "completed_30d": execution_stats["completed"],
            "failed_30d": execution_stats["failed"],
            "running": execution_stats["running"],
            "success_rate": (
                (execution_stats["completed"] / execution_stats["total"] * 100)
                if execution_stats["total"] > 0
                else 0
            ),
        },
        "agents": {
            "total_30d": agent_stats["total"],
            "completed_30d": agent_stats["completed"],
            "failed_30d": agent_stats["failed"],
            "running": agent_stats["running"],
            "success_rate": (
                (agent_stats["completed"] / agent_stats["total"] * 100)
                if agent_stats["total"] > 0
                else 0
            ),
        },
        "connectors": {
            "total": total_connectors or 0,
            "active": active_connectors or 0,
        },
        "rag": {
            "indexes": rag_indexes or 0,
            "queries_30d": rag_queries_30d or 0,
        },
        "ocr": {
            "total_30d": ocr_stats["total"],
            "completed_30d": ocr_stats["completed"],
            "failed_30d": ocr_stats["failed"],
            "success_rate": (
                (ocr_stats["completed"] / ocr_stats["total"] * 100)
                if ocr_stats["total"] > 0
                else 0
            ),
        },
        "scraping": {
            "total_30d": scraping_stats["total"],
            "completed_30d": scraping_stats["completed"],
            "failed_30d": scraping_stats["failed"],
            "success_rate": (
                (scraping_stats["completed"] / scraping_stats["total"] * 100)
                if scraping_stats["total"] > 0
                else 0
            ),
        },
        "browser": {
            "sessions_30d": browser_sessions_30d or 0,
        },
        "osint": {
            "streams": osint_streams or 0,
        },
        "code": {
            "total_30d": code_stats["total"],
            "completed_30d": code_stats["completed"],
            "failed_30d": code_stats["failed"],
            "success_rate": (
                (code_stats["completed"] / code_stats["total"] * 100)
                if code_stats["total"] > 0
                else 0
            ),
        },
        "recent_activity": recent_activity,
    }
