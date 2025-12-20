"""
Agent API Routes

Endpoints for agent task execution and management.
"""

import uuid
from typing import Any

from fastapi import APIRouter, Body, HTTPException, status
from sqlmodel import select

from app.agents.router import (
    AgentRouterError,
    FrameworkNotFoundError,
    TaskExecutionError,
    default_agent_router,
)
from app.api.deps import CurrentUser, SessionDep
from app.models import AgentFrameworkConfig, AgentTask

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("/run", status_code=status.HTTP_201_CREATED)
def run_agent_task(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    task_type: str = Body(...),
    input_data: dict[str, Any] = Body(...),
    framework: str | None = Body(None),
    agent_id: str | None = Body(None),
    task_requirements: dict[str, Any] | None = Body(None),
) -> Any:
    """
    Execute an agent task.

    Request Body:
    - task_type: Type of task to execute
    - input_data: Task input data
    - framework: Optional framework name (auto-selected if not provided)
    - agent_id: Optional agent ID for context caching
    - task_requirements: Optional task requirements for framework selection

    Returns:
    - Task execution result with task ID
    """
    router = default_agent_router

    try:
        # Select framework if not provided
        selected_framework = framework
        if not selected_framework:
            selected_framework = router.select_framework(
                session=session,
                task_type=task_type,
                task_requirements=task_requirements,
            )

        # Execute task
        task = router.execute_task(
            session=session,
            framework=selected_framework,
            task_type=task_type,
            input_data=input_data,
            agent_id=agent_id,
        )

        return {
            "id": str(task.id),
            "agent_framework": task.agent_framework,
            "task_type": task.task_type,
            "status": task.status,
            "started_at": task.started_at.isoformat(),
            "framework_selected": selected_framework,
        }
    except FrameworkNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except TaskExecutionError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    except AgentRouterError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/status/{task_id}")
def get_task_status(
    task_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Get status and details of an agent task.

    Path Parameters:
    - task_id: Task ID

    Returns:
    - Task status with logs and execution details
    """
    router = default_agent_router

    try:
        status_data = router.get_task_status(session=session, task_id=task_id)
        return status_data
    except TaskExecutionError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post("/switch/evaluate")
def evaluate_routing_decision(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    task_type: str = Body(...),
    task_requirements: dict[str, Any] = Body(...),
) -> Any:
    """
    Evaluate which framework would be selected for a task.

    Request Body:
    - task_type: Type of task
    - task_requirements: Task requirements dictionary

    Returns:
    - Routing decision with selected framework and reasoning
    """
    router = default_agent_router

    try:
        # Get framework selection
        selected_framework = router.select_framework(
            session=session,
            task_type=task_type,
            task_requirements=task_requirements,
        )

        # Get framework capabilities
        handler = router._get_framework_handler(selected_framework)
        capabilities = handler.get_capabilities()

        # Get framework config
        framework_config = session.exec(
            select(AgentFrameworkConfig).where(
                AgentFrameworkConfig.framework == selected_framework
            )
        ).first()

        return {
            "selected_framework": selected_framework,
            "capabilities": capabilities,
            "framework_config": framework_config.config if framework_config else {},
            "reasoning": _generate_routing_reasoning(
                task_requirements=task_requirements,
                selected_framework=selected_framework,
                capabilities=capabilities,
            ),
        }
    except FrameworkNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except AgentRouterError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/catalog")
def list_available_agents(
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    List all available agent frameworks.

    Returns:
    - List of available frameworks with their capabilities (both enabled and disabled)
    """
    # Get all framework configs from database
    framework_configs = session.exec(select(AgentFrameworkConfig)).all()

    # Also include frameworks that might not be in the database yet
    # Get all known framework names
    known_frameworks = {
        "agentgpt",
        "autogpt",
        "metagpt",
        "autogen",
        "archon",
        "crewai",
        "swarm",
        "camel_ai",
        "kush_ai",
        "kyro",
        "riona",
        "babyagi",
    }

    # Create a map of framework configs by framework name
    config_map = {config.framework: config for config in framework_configs}

    result = []
    for framework_name in sorted(known_frameworks):
        framework_config = config_map.get(framework_name)

        # Get framework handler if available (safely)
        capabilities = {}
        is_available = False
        try:
            router = default_agent_router
            if (
                hasattr(router, "_framework_handlers")
                and framework_name in router._framework_handlers
            ):
                handler = router._framework_handlers[framework_name]
                if hasattr(handler, "get_capabilities"):
                    capabilities = handler.get_capabilities()
                if hasattr(handler, "is_available"):
                    is_available = handler.is_available
        except Exception:
            # Framework not initialized or not available, but still include it
            pass

        result.append(
            {
                "framework": framework_name,
                "is_enabled": framework_config.is_enabled
                if framework_config
                else False,
                "is_available": is_available,
                "capabilities": capabilities,
                "config": framework_config.config if framework_config else {},
                "created_at": framework_config.created_at.isoformat()
                if framework_config and hasattr(framework_config, "created_at")
                else None,
                "updated_at": framework_config.updated_at.isoformat()
                if framework_config and hasattr(framework_config, "updated_at")
                else None,
            }
        )

    return {
        "frameworks": result,
        "total": len(result),
    }


@router.get("/tasks")
def list_agent_tasks(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
    framework: str | None = None,
    status_filter: str | None = None,
) -> Any:
    """
    List agent tasks.

    Query Parameters:
    - skip: Number of tasks to skip
    - limit: Maximum number of tasks to return
    - framework: Optional filter by framework
    - status_filter: Optional filter by status (running, completed, failed)

    Returns:
    - List of agent tasks
    """
    statement = select(AgentTask)

    if framework:
        statement = statement.where(AgentTask.agent_framework == framework)

    if status_filter:
        statement = statement.where(AgentTask.status == status_filter)

    statement = (
        statement.order_by(AgentTask.started_at.desc()).offset(skip).limit(limit)
    )

    tasks = session.exec(statement).all()

    return [
        {
            "id": str(task.id),
            "agent_framework": task.agent_framework,
            "task_type": task.task_type,
            "status": task.status,
            "started_at": task.started_at.isoformat(),
            "completed_at": task.completed_at.isoformat()
            if task.completed_at
            else None,
            "error_message": task.error_message,
        }
        for task in tasks
    ]


def _generate_routing_reasoning(
    task_requirements: dict[str, Any],
    selected_framework: str,
    capabilities: dict[str, Any],
) -> str:
    """
    Generate human-readable reasoning for routing decision.

    Args:
        task_requirements: Task requirements
        selected_framework: Selected framework
        capabilities: Framework capabilities

    Returns:
        Reasoning string
    """
    reasons = []

    # Check explicit preference
    if task_requirements.get("framework"):
        reasons.append(
            f"Explicit framework preference: {task_requirements.get('framework')}"
        )

    # Check multi-role requirement
    agent_roles = task_requirements.get("agent_roles", 1)
    if agent_roles > 1:
        reasons.append(
            f"Multi-role requirement ({agent_roles} roles) → {selected_framework}"
        )

    # Check recursive planning
    if task_requirements.get("recursive_planning"):
        reasons.append(f"Recursive planning required → {selected_framework}")

    # Check self-healing
    if task_requirements.get("agent_self_fix"):
        reasons.append(f"Self-healing required → {selected_framework}")

    # Check copilot UI preference
    if task_requirements.get("user_prefers_copilot_ui"):
        reasons.append(f"Copilot UI preference → {selected_framework}")

    # Default reasoning
    if not reasons:
        reasons.append(f"Default framework selection → {selected_framework}")

    return "; ".join(reasons)
