"""
Core Workflow Engine

Custom workflow orchestration engine that replicates Temporal-like functionality.
Handles execution state management, node execution, and state persistence.
"""

import uuid
from datetime import datetime
from typing import Any

from sqlmodel import Session, select

from app.models import ExecutionLog, Workflow, WorkflowExecution, WorkflowNode
from app.self_healing.service import SelfHealingService, default_self_healing_service
from app.workflows.retry import RetryManager, default_retry_manager
from app.workflows.signals import SignalHandler, default_signal_handler
from app.workflows.state import ExecutionState, NodeExecutionResult, WorkflowState


class WorkflowEngineError(Exception):
    """Base exception for workflow engine errors."""
    pass


class WorkflowNotFoundError(WorkflowEngineError):
    """Workflow not found."""
    pass


class ExecutionNotFoundError(WorkflowEngineError):
    """Execution not found."""
    pass


class WorkflowEngine:
    """
    Core workflow execution engine.
    
    Manages workflow execution lifecycle:
    - Creating executions
    - Executing nodes
    - Persisting state
    - Handling errors
    - Supporting pause/resume
    """
    
    def __init__(
        self,
        retry_manager: RetryManager | None = None,
        signal_handler: SignalHandler | None = None,
        self_healing_service: SelfHealingService | None = None,
    ):
        """
        Initialize the workflow engine.
        
        Args:
            retry_manager: Retry manager instance (defaults to default_retry_manager)
            signal_handler: Signal handler instance (defaults to default_signal_handler)
            self_healing_service: Self-healing service instance (defaults to default_self_healing_service)
        """
        self.retry_manager = retry_manager or default_retry_manager
        self.signal_handler = signal_handler or default_signal_handler
        self.self_healing_service = self_healing_service or default_self_healing_service
    
    def create_execution(
        self,
        session: Session,
        workflow_id: uuid.UUID,
        trigger_data: dict[str, Any] | None = None,
    ) -> WorkflowExecution:
        """
        Create a new workflow execution.
        
        Args:
            session: Database session
            workflow_id: ID of the workflow to execute
            trigger_data: Initial data for the workflow
            
        Returns:
            WorkflowExecution instance
        """
        # Get workflow
        workflow = session.get(Workflow, workflow_id)
        if not workflow:
            raise WorkflowNotFoundError(f"Workflow {workflow_id} not found")
        
        # Generate execution ID
        execution_id = f"exec-{uuid.uuid4().hex[:12]}"
        
        # Create execution record
        execution = WorkflowExecution(
            workflow_id=workflow_id,
            workflow_version=workflow.version,
            execution_id=execution_id,
            status="running",
            started_at=datetime.utcnow(),
            execution_state={
                "execution_id": execution_id,
                "workflow_id": str(workflow_id),
                "workflow_version": workflow.version,
                "status": "running",
                "current_node_id": None,
                "completed_node_ids": [],
                "node_results": {},
                "execution_data": trigger_data or {},
                "started_at": datetime.utcnow().isoformat(),
                "retry_count": 0,
            },
        )
        
        session.add(execution)
        session.commit()
        session.refresh(execution)
        
        # Log execution start
        self._log_execution(
            session,
            execution.id,
            "start",
            "info",
            f"Workflow execution started: {execution_id}",
        )
        
        return execution
    
    def get_execution_state(
        self,
        session: Session,
        execution_id: uuid.UUID,
    ) -> ExecutionState:
        """
        Get execution state from database.
        
        Args:
            session: Database session
            execution_id: Execution ID
            
        Returns:
            ExecutionState instance
        """
        execution = session.get(WorkflowExecution, execution_id)
        if not execution:
            raise ExecutionNotFoundError(f"Execution {execution_id} not found")
        
        return ExecutionState.from_dict(execution.execution_state)
    
    def save_execution_state(
        self,
        session: Session,
        execution_id: uuid.UUID,
        state: ExecutionState,
    ) -> None:
        """
        Save execution state to database.
        
        Args:
            session: Database session
            execution_id: Execution ID
            state: ExecutionState to save
        """
        execution = session.get(WorkflowExecution, execution_id)
        if not execution:
            raise ExecutionNotFoundError(f"Execution {execution_id} not found")
        
        # Update execution record
        execution.status = state.status
        execution.current_node_id = state.current_node_id
        execution.execution_state = state.to_dict()
        execution.error_message = state.error_message
        execution.retry_count = state.retry_count
        
        session.add(execution)
        session.commit()
    
    def get_workflow_state(
        self,
        session: Session,
        workflow_id: uuid.UUID,
        version: int | None = None,
    ) -> WorkflowState:
        """
        Get workflow state (nodes and graph configuration).
        
        Args:
            session: Database session
            workflow_id: Workflow ID
            version: Specific version (uses workflow version if None)
            
        Returns:
            WorkflowState instance
        """
        workflow = session.get(Workflow, workflow_id)
        if not workflow:
            raise WorkflowNotFoundError(f"Workflow {workflow_id} not found")
        
        # Use specified version or workflow's current version
        target_version = version or workflow.version
        
        # Get nodes for this workflow
        nodes_query = select(WorkflowNode).where(WorkflowNode.workflow_id == workflow_id)
        nodes = session.exec(nodes_query).all()
        
        # Build node dictionary
        node_dict = {}
        entry_node_id = None
        
        for node in nodes:
            node_dict[node.node_id] = {
                "node_type": node.node_type,
                "config": node.config,
                "position_x": node.position_x,
                "position_y": node.position_y,
            }
            
            # Find entry node (first trigger node or first node)
            if entry_node_id is None and (node.node_type == "trigger" or not entry_node_id):
                entry_node_id = node.node_id
        
        # Extract edges from graph_config
        edges = []
        graph_config = workflow.graph_config or {}
        
        # Support both LangGraph format and simple edge format
        if "edges" in graph_config:
            edges = graph_config["edges"]
        elif "nodes" in graph_config:
            # LangGraph format - extract edges from node connections
            for node_id, node_config in graph_config.get("nodes", {}).items():
                if "next" in node_config:
                    next_nodes = node_config["next"]
                    if isinstance(next_nodes, list):
                        for next_node in next_nodes:
                            edges.append({"from": node_id, "to": next_node})
                    elif isinstance(next_nodes, str):
                        edges.append({"from": node_id, "to": next_nodes})
        
        return WorkflowState(
            workflow_id=workflow_id,
            version=target_version,
            nodes=node_dict,
            edges=edges,
            entry_node_id=entry_node_id or (list(node_dict.keys())[0] if node_dict else None),
        )
    
    def execute_node(
        self,
        session: Session,
        execution_id: uuid.UUID,
        node_id: str,
        node_config: dict[str, Any],
        input_data: dict[str, Any],
    ) -> NodeExecutionResult:
        """
        Execute a single workflow node.
        
        This is a placeholder that will be extended with actual node execution logic.
        For now, it just records the execution.
        
        Args:
            session: Database session
            execution_id: Execution ID
            node_id: Node ID to execute
            node_config: Node configuration
            input_data: Input data for the node
            
        Returns:
            NodeExecutionResult
        """
        started_at = datetime.utcnow()
        
        # Log node execution start
        self._log_execution(
            session,
            execution_id,
            node_id,
            "info",
            f"Executing node: {node_id}",
        )
        
        try:
            # TODO: Actual node execution will be implemented in Phase 1.5 (LangGraph integration)
            # For now, simulate successful execution
            output = {
                "status": "success",
                "node_id": node_id,
                "node_type": node_config.get("node_type", "unknown"),
                "input_received": True,
            }
            
            completed_at = datetime.utcnow()
            duration_ms = int((completed_at - started_at).total_seconds() * 1000)
            
            result = NodeExecutionResult(
                node_id=node_id,
                status="success",
                output=output,
                started_at=started_at,
                completed_at=completed_at,
                duration_ms=duration_ms,
            )
            
            # Log success
            self._log_execution(
                session,
                execution_id,
                node_id,
                "info",
                f"Node {node_id} completed successfully",
            )
            
            return result
            
        except Exception as e:
            completed_at = datetime.utcnow()
            duration_ms = int((completed_at - started_at).total_seconds() * 1000)
            
            # Attempt self-healing before marking as failed
            healing_result = self.self_healing_service.heal_task(
                error=e,
                task={
                    "node_id": node_id,
                    "node_config": node_config,
                    "input_data": input_data,
                },
                context={
                    "execution_id": str(execution_id),
                    "workflow_id": str(execution_id),  # Will be updated with actual workflow_id
                },
            )
            
            if healing_result.get("success"):
                # Log healing success
                self._log_execution(
                    session,
                    execution_id,
                    node_id,
                    "info",
                    f"Node {node_id} healed using {healing_result.get('fix_type', 'unknown')}",
                )
                
                # Try executing with healed task
                try:
                    healed_task = healing_result.get("healed_task", {})
                    healed_node_config = healed_task.get("node_config", node_config)
                    healed_input_data = healed_task.get("input_data", input_data)
                    
                    # Retry execution with healed configuration
                    # Note: This is a simplified retry - full implementation would re-execute the node
                    output = {
                        "status": "success",
                        "node_id": node_id,
                        "node_type": healed_node_config.get("node_type", node_config.get("node_type", "unknown")),
                        "input_received": True,
                        "healed": True,
                        "healing_type": healing_result.get("fix_type"),
                    }
                    
                    completed_at = datetime.utcnow()
                    duration_ms = int((completed_at - started_at).total_seconds() * 1000)
                    
                    result = NodeExecutionResult(
                        node_id=node_id,
                        status="success",
                        output=output,
                        started_at=started_at,
                        completed_at=completed_at,
                        duration_ms=duration_ms,
                    )
                    
                    # Log success after healing
                    self._log_execution(
                        session,
                        execution_id,
                        node_id,
                        "info",
                        f"Node {node_id} completed successfully after healing",
                    )
                    
                    return result
                    
                except Exception as retry_error:
                    # Healing didn't work, proceed with failure
                    self._log_execution(
                        session,
                        execution_id,
                        node_id,
                        "warning",
                        f"Node {node_id} healing attempt failed: {str(retry_error)}",
                    )
            
            # If healing failed or wasn't attempted, mark as failed
            result = NodeExecutionResult(
                node_id=node_id,
                status="failed",
                output={},
                error=str(e),
                started_at=started_at,
                completed_at=completed_at,
                duration_ms=duration_ms,
            )
            
            # Log error
            self._log_execution(
                session,
                execution_id,
                node_id,
                "error",
                f"Node {node_id} failed: {str(e)}",
            )
            
            return result
    
    def pause_execution(
        self,
        session: Session,
        execution_id: uuid.UUID,
    ) -> None:
        """Pause a running execution."""
        state = self.get_execution_state(session, execution_id)
        state.status = "paused"
        self.save_execution_state(session, execution_id, state)
        
        self._log_execution(
            session,
            execution_id,
            state.current_node_id or "system",
            "info",
            "Execution paused",
        )
    
    def resume_execution(
        self,
        session: Session,
        execution_id: uuid.UUID,
    ) -> None:
        """Resume a paused execution."""
        state = self.get_execution_state(session, execution_id)
        if state.status not in ("paused", "waiting_for_signal"):
            raise WorkflowEngineError(f"Execution {execution_id} is not paused or waiting for signal")
        
        state.status = "running"
        self.save_execution_state(session, execution_id, state)
        
        self._log_execution(
            session,
            execution_id,
            state.current_node_id or "system",
            "info",
            "Execution resumed",
        )
    
    def terminate_execution(
        self,
        session: Session,
        execution_id: uuid.UUID,
        reason: str | None = None,
    ) -> None:
        """Terminate a running or paused execution."""
        state = self.get_execution_state(session, execution_id)
        if state.status not in ("running", "paused", "waiting_for_signal"):
            raise WorkflowEngineError(f"Execution {execution_id} cannot be terminated (status: {state.status})")
        
        # Mark as failed with termination reason
        state.status = "failed"
        if reason:
            state.error_message = reason
        else:
            state.error_message = "Execution terminated by user"
        
        self.save_execution_state(session, execution_id, state)
        
        # Update execution record
        execution = session.get(WorkflowExecution, execution_id)
        if execution:
            execution.status = "failed"
            execution.completed_at = datetime.utcnow()
            execution.error_message = state.error_message
            session.add(execution)
        
        self._log_execution(
            session,
            execution_id,
            state.current_node_id or "system",
            "warning",
            f"Execution terminated: {state.error_message}",
        )
    
    def wait_for_signal(
        self,
        session: Session,
        execution_id: uuid.UUID,
        signal_type: str,
    ) -> None:
        """
        Mark execution as waiting for a signal.
        
        Args:
            session: Database session
            execution_id: Execution ID
            signal_type: Type of signal to wait for
        """
        state = self.get_execution_state(session, execution_id)
        state.status = "waiting_for_signal"
        self.save_execution_state(session, execution_id, state)
        
        self._log_execution(
            session,
            execution_id,
            state.current_node_id or "system",
            "info",
            f"Execution waiting for signal: {signal_type}",
        )
    
    def process_signal(
        self,
        session: Session,
        execution_id: uuid.UUID,
        signal_type: str,
        signal_data: dict[str, Any],
    ) -> None:
        """
        Process a signal and resume execution if waiting.
        
        Args:
            session: Database session
            execution_id: Execution ID
            signal_type: Type of signal
            signal_data: Signal data
        """
        # Emit the signal
        signal = self.signal_handler.emit_signal(
            session,
            execution_id,
            signal_type,
            signal_data,
        )
        
        # Check if execution is waiting for this signal
        state = self.get_execution_state(session, execution_id)
        if state.status == "waiting_for_signal":
            # Resume execution
            state.status = "running"
            # Add signal data to execution data
            state.execution_data[f"signal_{signal_type}"] = signal_data
            self.save_execution_state(session, execution_id, state)
            
            self._log_execution(
                session,
                execution_id,
                state.current_node_id or "system",
                "info",
                f"Signal received and processed: {signal_type}",
            )
        
        # Mark signal as processed
        self.signal_handler.mark_signal_processed(session, signal.id)
    
    def complete_execution(
        self,
        session: Session,
        execution_id: uuid.UUID,
        final_data: dict[str, Any] | None = None,
    ) -> None:
        """Mark execution as completed."""
        state = self.get_execution_state(session, execution_id)
        state.status = "completed"
        if final_data:
            state.execution_data.update(final_data)
        
        execution = session.get(WorkflowExecution, execution_id)
        if execution:
            execution.completed_at = datetime.utcnow()
            session.add(execution)
        
        self.save_execution_state(session, execution_id, state)
        
        self._log_execution(
            session,
            execution_id,
            "end",
            "info",
            "Workflow execution completed",
        )
    
    def fail_execution(
        self,
        session: Session,
        execution_id: uuid.UUID,
        error_message: str,
        schedule_retry: bool = True,
    ) -> None:
        """
        Mark execution as failed, optionally scheduling a retry.
        
        Args:
            session: Database session
            execution_id: Execution ID
            error_message: Error message
            schedule_retry: Whether to schedule a retry if retry count allows
        """
        state = self.get_execution_state(session, execution_id)
        execution = session.get(WorkflowExecution, execution_id)
        
        if not execution:
            raise ExecutionNotFoundError(f"Execution {execution_id} not found")
        
        # Check if we should retry
        if schedule_retry and self.retry_manager.should_retry_execution(state.retry_count):
            # Schedule retry
            state.retry_count += 1
            state.status = "failed"
            state.error_message = error_message
            state.next_retry_at = self.retry_manager.schedule_retry(
                state.retry_count - 1,  # retry_count is already incremented
                datetime.utcnow(),
            )
            
            execution.retry_count = state.retry_count
            execution.next_retry_at = state.next_retry_at
            execution.error_message = error_message
            
            self.save_execution_state(session, execution_id, state)
            
            retry_info = self.retry_manager.get_retry_info(state.retry_count - 1)
            self._log_execution(
                session,
                execution_id,
                state.current_node_id or "system",
                "warning",
                f"Workflow execution failed, retry {state.retry_count}/{self.retry_manager.policy.max_retries} scheduled: {error_message}",
            )
        else:
            # Final failure - no more retries
            state.status = "failed"
            state.error_message = error_message
            
            execution.completed_at = datetime.utcnow()
            execution.error_message = error_message
            
            self.save_execution_state(session, execution_id, state)
            
            self._log_execution(
                session,
                execution_id,
                state.current_node_id or "system",
                "error",
                f"Workflow execution failed permanently: {error_message}",
            )
    
    def _log_execution(
        self,
        session: Session,
        execution_id: uuid.UUID,
        node_id: str,
        level: str,
        message: str,
    ) -> None:
        """Log execution event."""
        log = ExecutionLog(
            execution_id=execution_id,
            node_id=node_id,
            level=level,
            message=message,
            timestamp=datetime.utcnow(),
        )
        session.add(log)
        session.commit()

