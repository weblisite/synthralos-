"""
Workflow API Routes

Endpoints for managing workflows and executions.
"""

import logging
import uuid
from typing import Any

from datetime import datetime, timedelta
from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.exc import SQLAlchemyError, OperationalError, IntegrityError
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.core.db import check_db_connectivity
from app.models import (
    ExecutionLog,
    ModelCostLog,
    User,
    Workflow,
    WorkflowCreate,
    WorkflowExecution,
    WorkflowNode,
    WorkflowPublic,
    WorkflowUpdate,
)
from app.workflows.engine import WorkflowEngine, WorkflowNotFoundError
from app.workflows.history import ExecutionHistory
from app.workflows.scheduler import WorkflowScheduler

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workflows", tags=["workflows"])

# Initialize engines
workflow_engine = WorkflowEngine()
scheduler = WorkflowScheduler(workflow_engine)
history = ExecutionHistory(workflow_engine)


@router.post("/", response_model=WorkflowPublic, status_code=201)
def create_workflow(
    workflow_in: WorkflowCreate,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Create a new workflow.
    
    Includes proper error handling, logging, and transaction management.
    """
    logger.info(
        f"Creating workflow: name='{workflow_in.name}', "
        f"user_id={current_user.id}, "
        f"has_graph_config={bool(workflow_in.graph_config)}, "
        f"has_trigger_config={bool(workflow_in.trigger_config)}"
    )
    
    # Quick database connectivity check
    if not check_db_connectivity():
        logger.error("Database connectivity check failed before creating workflow")
        raise HTTPException(
            status_code=503,
            detail="Database is currently unavailable. Please try again later."
        )
    
    try:
        # Validate workflow data
        if not workflow_in.name or not workflow_in.name.strip():
            raise HTTPException(
                status_code=400,
                detail="Workflow name is required and cannot be empty"
            )
        
        # Create workflow object
        workflow = Workflow(
            **workflow_in.model_dump(),
            owner_id=current_user.id,
        )
        
        logger.debug(f"Workflow object created: {workflow.id}")
        
        # Add to session
        session.add(workflow)
        logger.debug("Workflow added to session")
        
        # Commit transaction with error handling
        try:
            session.commit()
            logger.info(f"Workflow created successfully: id={workflow.id}, name='{workflow.name}'")
        except IntegrityError as e:
            session.rollback()
            logger.error(
                f"Database integrity error creating workflow: {str(e)}, "
                f"user_id={current_user.id}, workflow_name='{workflow_in.name}'"
            )
            # Check for specific constraint violations
            error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            if "foreign key" in error_msg.lower():
                raise HTTPException(
                    status_code=400,
                    detail="Invalid user or reference. Please ensure you are properly authenticated."
                )
            elif "unique constraint" in error_msg.lower() or "duplicate" in error_msg.lower():
                raise HTTPException(
                    status_code=409,
                    detail="A workflow with this name already exists"
                )
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Database constraint violation: {error_msg}"
                )
        except OperationalError as e:
            session.rollback()
            logger.error(
                f"Database operational error creating workflow: {str(e)}, "
                f"user_id={current_user.id}, workflow_name='{workflow_in.name}'"
            )
            # Check for connection/timeout issues
            error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            if "timeout" in error_msg.lower() or "connection" in error_msg.lower():
                raise HTTPException(
                    status_code=503,
                    detail="Database connection timeout. Please try again."
                )
            else:
                raise HTTPException(
                    status_code=503,
                    detail="Database operation failed. Please try again later."
                )
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(
                f"Database error creating workflow: {str(e)}, "
                f"user_id={current_user.id}, workflow_name='{workflow_in.name}'",
                exc_info=True
            )
            raise HTTPException(
                status_code=500,
                detail="Failed to create workflow due to database error"
            )
        
        # Refresh to get database-generated fields
        try:
            session.refresh(workflow)
            logger.debug(f"Workflow refreshed: id={workflow.id}")
        except SQLAlchemyError as e:
            logger.warning(
                f"Failed to refresh workflow after creation: {str(e)}, "
                f"workflow_id={workflow.id}"
            )
            # Workflow was created, so we can still return it
        
        return workflow
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Rollback on any unexpected error
        try:
            session.rollback()
        except Exception:
            pass  # Ignore rollback errors if session is already closed
        
        logger.error(
            f"Unexpected error creating workflow: {str(e)}, "
            f"user_id={current_user.id}, workflow_name='{workflow_in.name}'",
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while creating the workflow"
        )


@router.get("/", response_model=list[WorkflowPublic])
def read_workflows(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get all workflows for the current user.
    """
    statement = (
        select(Workflow)
        .where(Workflow.owner_id == current_user.id)
        .offset(skip)
        .limit(limit)
    )
    workflows = session.exec(statement).all()
    return list(workflows)


@router.get("/executions/failed")
def list_failed_executions(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    retry_count_min: int | None = Query(None, ge=0),
) -> Any:
    """
    List all failed executions (admin only).
    
    Returns executions with status='failed', optionally filtered by retry count.
    """
    # Check if user is superuser
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    statement = select(WorkflowExecution).where(WorkflowExecution.status == "failed")
    
    if retry_count_min is not None:
        statement = statement.where(WorkflowExecution.retry_count >= retry_count_min)
    
    statement = statement.order_by(WorkflowExecution.started_at.desc()).offset(skip).limit(limit)
    executions = session.exec(statement).all()
    
    return [
        {
            "id": str(execution.id),
            "execution_id": execution.execution_id,
            "workflow_id": str(execution.workflow_id),
            "status": execution.status,
            "started_at": execution.started_at.isoformat(),
            "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
            "error_message": execution.error_message,
            "retry_count": execution.retry_count,
            "next_retry_at": None,  # TODO: Implement retry scheduling
        }
        for execution in executions
    ]


@router.get("/executions")
def list_all_executions(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    workflow_id: uuid.UUID | None = Query(None),
) -> Any:
    """
    List all workflow executions.
    
    For regular users: returns only their own executions.
    For admins: returns all executions (or filtered by workflow_id).
    """
    if current_user.is_superuser:
        # Admin can see all executions
        statement = select(WorkflowExecution)
        if workflow_id:
            statement = statement.where(WorkflowExecution.workflow_id == workflow_id)
    else:
        # Regular users see only their own executions
        statement = (
            select(WorkflowExecution)
            .join(Workflow)
            .where(Workflow.owner_id == current_user.id)
        )
        if workflow_id:
            statement = statement.where(WorkflowExecution.workflow_id == workflow_id)
    
    statement = statement.order_by(WorkflowExecution.started_at.desc()).offset(skip).limit(limit)
    executions = session.exec(statement).all()
    
    return [
        {
            "id": str(execution.id),
            "execution_id": execution.execution_id,
            "workflow_id": str(execution.workflow_id),
            "status": execution.status,
            "started_at": execution.started_at.isoformat(),
            "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
            "error_message": execution.error_message,
            "retry_count": execution.retry_count,
            "duration_ms": (
                int((execution.completed_at - execution.started_at).total_seconds() * 1000)
                if execution.completed_at and execution.started_at
                else None
            ),
        }
        for execution in executions
    ]


@router.get("/by-workflow/{workflow_id}/executions")
def get_workflow_executions(
    workflow_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get all executions for a workflow.
    """
    workflow = session.get(Workflow, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Check ownership
    if workflow.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    statement = (
        select(WorkflowExecution)
        .where(WorkflowExecution.workflow_id == workflow_id)
        .order_by(WorkflowExecution.started_at.desc())
        .offset(skip)
        .limit(limit)
    )
    executions = session.exec(statement).all()
    
    return [
        {
            "id": str(execution.id),
            "execution_id": execution.execution_id,
            "status": execution.status,
            "started_at": execution.started_at.isoformat(),
            "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
            "error_message": execution.error_message,
            "retry_count": execution.retry_count,
        }
        for execution in executions
    ]


@router.get("/executions/{execution_id}/status")
def get_execution_status(
    execution_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Get execution status and details.
    """
    execution = session.get(WorkflowExecution, execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    # Check ownership via workflow
    workflow = session.get(Workflow, execution.workflow_id)
    if not workflow or workflow.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Get execution summary
    summary = history.get_execution_summary(session, execution_id)
    
    return summary


@router.get("/executions/{execution_id}/logs")
def get_execution_logs(
    execution_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
    node_id: str | None = None,
    level: str | None = None,
    limit: int = 1000,
) -> Any:
    """
    Get execution logs.
    """
    execution = session.get(WorkflowExecution, execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    # Check ownership via workflow
    workflow = session.get(Workflow, execution.workflow_id)
    if not workflow or workflow.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    logs = history.get_execution_logs(
        session,
        execution_id,
        node_id=node_id,
        level=level,
        limit=limit,
    )
    
    return [
        {
            "id": str(log.id),
            "node_id": log.node_id,
            "level": log.level,
            "message": log.message,
            "timestamp": log.timestamp.isoformat(),
        }
        for log in logs
    ]


@router.get("/executions/{execution_id}/timeline")
def get_execution_timeline(
    execution_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Get complete execution timeline.
    """
    execution = session.get(WorkflowExecution, execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    # Check ownership via workflow
    workflow = session.get(Workflow, execution.workflow_id)
    if not workflow or workflow.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    timeline = history.get_execution_timeline(session, execution_id)
    return timeline


@router.post("/executions/{execution_id}/replay", status_code=201)
def replay_execution(
    execution_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
    from_node_id: str | None = Query(default=None),
) -> Any:
    """
    Replay an execution from a specific point.
    
    Creates a new execution based on the original, optionally starting
    from a specific node.
    """
    execution = session.get(WorkflowExecution, execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    # Check ownership via workflow
    workflow = session.get(Workflow, execution.workflow_id)
    if not workflow or workflow.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    try:
        new_execution_id = history.replay_execution(
            session,
            execution_id,
            from_node_id=from_node_id,
        )
        
        new_execution = session.get(WorkflowExecution, new_execution_id)
        
        return {
            "execution_id": new_execution.execution_id,
            "id": str(new_execution.id),
            "status": new_execution.status,
            "started_at": new_execution.started_at.isoformat(),
            "replay_from": from_node_id,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Replay failed: {str(e)}")


@router.post("/executions/{execution_id}/pause", status_code=200)
def pause_execution(
    execution_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Pause a running execution.
    """
    execution = session.get(WorkflowExecution, execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    # Check ownership via workflow
    workflow = session.get(Workflow, execution.workflow_id)
    if not workflow or workflow.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    try:
        workflow_engine.pause_execution(session, execution_id)
        return {"status": "paused", "execution_id": execution.execution_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Pause failed: {str(e)}")


@router.post("/executions/{execution_id}/resume", status_code=200)
def resume_execution(
    execution_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Resume a paused execution.
    """
    execution = session.get(WorkflowExecution, execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    # Check ownership via workflow
    workflow = session.get(Workflow, execution.workflow_id)
    if not workflow or workflow.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    try:
        workflow_engine.resume_execution(session, execution_id)
        return {"status": "running", "execution_id": execution.execution_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Resume failed: {str(e)}")


@router.post("/executions/{execution_id}/terminate", status_code=200)
def terminate_execution(
    execution_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
    reason: str | None = Body(default=None, embed=True),
) -> Any:
    """
    Terminate a running or paused execution.
    """
    execution = session.get(WorkflowExecution, execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    # Check ownership via workflow
    workflow = session.get(Workflow, execution.workflow_id)
    if not workflow or workflow.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    try:
        workflow_engine.terminate_execution(session, execution_id, reason=reason)
        session.commit()
        return {"status": "terminated", "execution_id": execution.execution_id}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=f"Terminate failed: {str(e)}")


@router.get("/{workflow_id}", response_model=WorkflowPublic)
def read_workflow(
    workflow_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Get a specific workflow by ID.
    """
    workflow = session.get(Workflow, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Check ownership
    if workflow.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return workflow


@router.patch("/{workflow_id}", response_model=WorkflowPublic)
def update_workflow(
    workflow_id: uuid.UUID,
    workflow_in: WorkflowUpdate,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Update a workflow.
    """
    workflow = session.get(Workflow, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Check ownership
    if workflow.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Update fields
    update_data = workflow_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(workflow, field, value)
    
    session.add(workflow)
    session.commit()
    session.refresh(workflow)
    return workflow


@router.delete("/{workflow_id}", status_code=204)
def delete_workflow(
    workflow_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> None:
    """
    Delete a workflow.
    """
    workflow = session.get(Workflow, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Check ownership
    if workflow.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    session.delete(workflow)
    session.commit()


@router.post("/{workflow_id}/run", status_code=201)
def run_workflow(
    workflow_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
    trigger_data: dict[str, Any] | None = Body(default=None),
) -> Any:
    """
    Run a workflow execution.
    
    Creates a new execution and returns the execution ID.
    The worker will pick up and execute the workflow.
    """
    workflow = session.get(Workflow, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Check ownership
    if workflow.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Check if workflow is active
    if not workflow.is_active:
        raise HTTPException(status_code=400, detail="Workflow is not active")
    
    try:
        # Create execution
        execution = workflow_engine.create_execution(
            session,
            workflow_id,
            trigger_data=trigger_data,
        )
        
        return {
            "execution_id": execution.execution_id,
            "id": str(execution.id),
            "status": execution.status,
            "started_at": execution.started_at.isoformat(),
        }
    except WorkflowNotFoundError:
        raise HTTPException(status_code=404, detail="Workflow not found")

