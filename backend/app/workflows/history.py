"""
Workflow Execution History and Replay

Provides complete audit trail and replay capability for workflow executions.
"""

import uuid
from datetime import datetime
from typing import Any

from sqlmodel import Session, select

from app.models import ExecutionLog, WorkflowExecution
from app.workflows.engine import WorkflowEngine
from app.workflows.state import ExecutionState, NodeExecutionResult


class HistoryError(Exception):
    """Base exception for history errors."""
    pass


class ExecutionHistory:
    """
    Manages execution history and replay.
    
    Provides:
    - Complete audit trail
    - Node-level logs
    - Replay capability
    """
    
    def __init__(self, workflow_engine: WorkflowEngine | None = None):
        """
        Initialize history manager.
        
        Args:
            workflow_engine: WorkflowEngine instance (creates new if None)
        """
        self.workflow_engine = workflow_engine or WorkflowEngine()
    
    def get_execution_logs(
        self,
        session: Session,
        execution_id: uuid.UUID,
        node_id: str | None = None,
        level: str | None = None,
        limit: int = 1000,
    ) -> list[ExecutionLog]:
        """
        Get execution logs with optional filtering.
        
        Args:
            session: Database session
            execution_id: Execution ID
            node_id: Optional filter by node ID
            level: Optional filter by log level (info, error, debug, warning)
            limit: Maximum number of logs to return
            
        Returns:
            List of execution logs
        """
        query = select(ExecutionLog).where(
            ExecutionLog.execution_id == execution_id,
        )
        
        if node_id:
            query = query.where(ExecutionLog.node_id == node_id)
        
        if level:
            query = query.where(ExecutionLog.level == level)
        
        query = query.order_by(ExecutionLog.timestamp).limit(limit)
        
        logs = session.exec(query).all()
        return list(logs)
    
    def get_execution_timeline(
        self,
        session: Session,
        execution_id: uuid.UUID,
    ) -> list[dict[str, Any]]:
        """
        Get complete execution timeline with all events.
        
        Args:
            session: Database session
            execution_id: Execution ID
            
        Returns:
            List of timeline events
        """
        execution = session.get(WorkflowExecution, execution_id)
        if not execution:
            return []
        
        timeline = []
        
        # Add execution start
        timeline.append({
            "timestamp": execution.started_at.isoformat(),
            "event_type": "execution_started",
            "node_id": None,
            "message": f"Workflow execution started: {execution.execution_id}",
            "data": {
                "workflow_id": str(execution.workflow_id),
                "workflow_version": execution.workflow_version,
            },
        })
        
        # Get state to extract node execution history
        state = self.workflow_engine.get_execution_state(session, execution_id)
        
        # Add node execution events
        for node_id, result in state.node_results.items():
            timeline.append({
                "timestamp": result.started_at.isoformat(),
                "event_type": "node_started",
                "node_id": node_id,
                "message": f"Node {node_id} started",
                "data": {
                    "node_type": result.output.get("node_type", "unknown"),
                },
            })
            
            if result.completed_at:
                timeline.append({
                    "timestamp": result.completed_at.isoformat(),
                    "event_type": "node_completed" if result.status == "success" else "node_failed",
                    "node_id": node_id,
                    "message": f"Node {node_id} {result.status}",
                    "data": {
                        "status": result.status,
                        "duration_ms": result.duration_ms,
                        "error": result.error,
                        "output": result.output,
                    },
                })
        
        # Add execution completion/failure
        if execution.completed_at:
            timeline.append({
                "timestamp": execution.completed_at.isoformat(),
                "event_type": "execution_completed" if execution.status == "completed" else "execution_failed",
                "node_id": None,
                "message": f"Workflow execution {execution.status}",
                "data": {
                    "status": execution.status,
                    "error_message": execution.error_message,
                },
            })
        
        # Add logs
        logs = self.get_execution_logs(session, execution_id)
        for log in logs:
            timeline.append({
                "timestamp": log.timestamp.isoformat(),
                "event_type": "log",
                "node_id": log.node_id,
                "message": log.message,
                "data": {
                    "level": log.level,
                },
            })
        
        # Sort by timestamp
        timeline.sort(key=lambda x: x["timestamp"])
        
        return timeline
    
    def get_execution_summary(
        self,
        session: Session,
        execution_id: uuid.UUID,
    ) -> dict[str, Any]:
        """
        Get execution summary with statistics.
        
        Args:
            session: Database session
            execution_id: Execution ID
            
        Returns:
            Execution summary dictionary
        """
        execution = session.get(WorkflowExecution, execution_id)
        if not execution:
            raise HistoryError(f"Execution {execution_id} not found")
        
        state = self.workflow_engine.get_execution_state(session, execution_id)
        
        # Calculate statistics
        total_nodes = len(state.node_results)
        completed_nodes = len([r for r in state.node_results.values() if r.status == "success"])
        failed_nodes = len([r for r in state.node_results.values() if r.status == "failed"])
        
        total_duration_ms = sum(
            r.duration_ms for r in state.node_results.values() if r.completed_at
        )
        
        logs = self.get_execution_logs(session, execution_id)
        error_logs = [log for log in logs if log.level == "error"]
        warning_logs = [log for log in logs if log.level == "warning"]
        
        return {
            "execution_id": execution.execution_id,
            "workflow_id": str(execution.workflow_id),
            "workflow_version": execution.workflow_version,
            "status": execution.status,
            "started_at": execution.started_at.isoformat(),
            "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
            "duration_ms": (
                int((execution.completed_at - execution.started_at).total_seconds() * 1000)
                if execution.completed_at
                else None
            ),
            "statistics": {
                "total_nodes": total_nodes,
                "completed_nodes": completed_nodes,
                "failed_nodes": failed_nodes,
                "total_node_duration_ms": total_duration_ms,
                "total_logs": len(logs),
                "error_logs": len(error_logs),
                "warning_logs": len(warning_logs),
            },
            "current_node_id": state.current_node_id,
            "retry_count": state.retry_count,
            "error_message": execution.error_message,
        }
    
    def replay_execution(
        self,
        session: Session,
        execution_id: uuid.UUID,
        from_node_id: str | None = None,
    ) -> uuid.UUID:
        """
        Replay an execution from a specific point.
        
        Creates a new execution based on the original, optionally starting
        from a specific node.
        
        Args:
            session: Database session
            execution_id: Original execution ID
            from_node_id: Optional node ID to start replay from (defaults to beginning)
            
        Returns:
            New execution ID
        """
        original_execution = session.get(WorkflowExecution, execution_id)
        if not original_execution:
            raise HistoryError(f"Execution {execution_id} not found")
        
        original_state = self.workflow_engine.get_execution_state(
            session,
            execution_id,
        )
        
        # Create new execution
        new_execution = self.workflow_engine.create_execution(
            session,
            original_execution.workflow_id,
            trigger_data={
                "trigger_type": "replay",
                "original_execution_id": str(execution_id),
                "replay_from_node": from_node_id,
            },
        )
        
        # If replaying from a specific node, copy state up to that point
        if from_node_id:
            new_state = self.workflow_engine.get_execution_state(
                session,
                new_execution.id,
            )
            
            # Copy execution data
            new_state.execution_data = original_state.execution_data.copy()
            
            # Copy node results up to the replay point
            for node_id, result in original_state.node_results.items():
                if node_id == from_node_id:
                    break
                new_state.mark_node_completed(node_id, result)
            
            self.workflow_engine.save_execution_state(session, new_execution.id, new_state)
            
            self.workflow_engine._log_execution(
                session,
                new_execution.id,
                "system",
                "info",
                f"Replay started from node: {from_node_id}",
            )
        else:
            self.workflow_engine._log_execution(
                session,
                new_execution.id,
                "system",
                "info",
                f"Replay started from beginning of execution {execution_id}",
            )
        
        return new_execution.id
    
    def get_node_execution_history(
        self,
        session: Session,
        execution_id: uuid.UUID,
        node_id: str,
    ) -> dict[str, Any]:
        """
        Get complete history for a specific node execution.
        
        Args:
            session: Database session
            execution_id: Execution ID
            node_id: Node ID
            
        Returns:
            Node execution history
        """
        state = self.workflow_engine.get_execution_state(session, execution_id)
        result = state.get_node_result(node_id)
        
        if not result:
            return {
                "node_id": node_id,
                "status": "not_executed",
                "logs": [],
            }
        
        # Get logs for this node
        logs = self.get_execution_logs(session, execution_id, node_id=node_id)
        
        return {
            "node_id": node_id,
            "status": result.status,
            "started_at": result.started_at.isoformat(),
            "completed_at": result.completed_at.isoformat() if result.completed_at else None,
            "duration_ms": result.duration_ms,
            "output": result.output,
            "error": result.error,
            "logs": [
                {
                    "timestamp": log.timestamp.isoformat(),
                    "level": log.level,
                    "message": log.message,
                }
                for log in logs
            ],
        }


# Default history manager instance
default_history = ExecutionHistory()

