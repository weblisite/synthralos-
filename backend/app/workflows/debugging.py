"""
Workflow Debugging

Provides debugging capabilities:
- Step-by-step debugging
- Breakpoints
- Variable inspection
- Execution state inspection
- Debug mode execution
"""

import uuid
from typing import Any

from sqlmodel import Session

from app.workflows.engine import WorkflowEngine


class DebuggerError(Exception):
    """Base exception for debugger errors."""

    pass


class WorkflowDebugger:
    """
    Debugger for workflow execution.
    """

    def __init__(self, workflow_engine: WorkflowEngine | None = None):
        """
        Initialize debugger.

        Args:
            workflow_engine: WorkflowEngine instance
        """
        self.workflow_engine = workflow_engine or WorkflowEngine()
        self.breakpoints: set[str] = set()  # Set of node IDs with breakpoints
        self.debug_mode_executions: set[uuid.UUID] = set()  # Executions in debug mode

    def set_breakpoint(
        self,
        execution_id: uuid.UUID,
        node_id: str,
    ) -> None:
        """
        Set breakpoint at a node.

        Args:
            execution_id: Execution ID
            node_id: Node ID
        """
        self.breakpoints.add(f"{execution_id}:{node_id}")

    def remove_breakpoint(
        self,
        execution_id: uuid.UUID,
        node_id: str,
    ) -> None:
        """
        Remove breakpoint at a node.

        Args:
            execution_id: Execution ID
            node_id: Node ID
        """
        self.breakpoints.discard(f"{execution_id}:{node_id}")

    def enable_debug_mode(
        self,
        session: Session,
        execution_id: uuid.UUID,
    ) -> None:
        """
        Enable debug mode for an execution.

        Args:
            session: Database session
            execution_id: Execution ID
        """
        state = self.workflow_engine.get_execution_state(session, execution_id)
        state.execution_data["debug_mode"] = True
        state.status = "paused"  # Pause execution for debugging
        self.workflow_engine.save_execution_state(session, execution_id, state)

        self.debug_mode_executions.add(execution_id)

    def disable_debug_mode(
        self,
        session: Session,
        execution_id: uuid.UUID,
    ) -> None:
        """
        Disable debug mode for an execution.

        Args:
            session: Database session
            execution_id: Execution ID
        """
        state = self.workflow_engine.get_execution_state(session, execution_id)
        state.execution_data.pop("debug_mode", None)
        if state.status == "paused":
            state.status = "running"  # Resume execution
        self.workflow_engine.save_execution_state(session, execution_id, state)

        self.debug_mode_executions.discard(execution_id)

    def step_over(
        self,
        session: Session,
        execution_id: uuid.UUID,
    ) -> dict[str, Any]:
        """
        Execute next step in debug mode.

        Args:
            session: Database session
            execution_id: Execution ID

        Returns:
            Step execution result
        """
        state = self.workflow_engine.get_execution_state(session, execution_id)

        if execution_id not in self.debug_mode_executions:
            raise DebuggerError("Execution is not in debug mode")

        # Resume execution for one step
        state.status = "running"
        self.workflow_engine.save_execution_state(session, execution_id, state)

        # Execute one step (would be handled by worker)
        # For now, return current state

        return {
            "execution_id": str(execution_id),
            "current_node_id": state.current_node_id,
            "status": state.status,
        }

    def inspect_variables(
        self,
        session: Session,
        execution_id: uuid.UUID,
        scope: str | None = None,
    ) -> dict[str, Any]:
        """
        Inspect variables in execution.

        Args:
            session: Database session
            execution_id: Execution ID
            scope: Optional scope (workflow, node, loop)

        Returns:
            Variables dictionary
        """
        state = self.workflow_engine.get_execution_state(session, execution_id)

        if scope:
            return state.variables.get(scope, {})
        else:
            # Return all variables
            all_variables = {}
            for scope_name, scope_vars in state.variables.items():
                all_variables[scope_name] = scope_vars
            return all_variables

    def inspect_execution_state(
        self,
        session: Session,
        execution_id: uuid.UUID,
    ) -> dict[str, Any]:
        """
        Inspect execution state.

        Args:
            session: Database session
            execution_id: Execution ID

        Returns:
            Execution state dictionary
        """
        state = self.workflow_engine.get_execution_state(session, execution_id)

        return {
            "execution_id": str(execution_id),
            "workflow_id": str(state.workflow_id),
            "status": state.status,
            "current_node_id": state.current_node_id,
            "completed_node_ids": state.completed_node_ids,
            "execution_data": state.execution_data,
            "node_results": {
                node_id: {
                    "status": result.status,
                    "output": result.output,
                    "error": result.error,
                }
                for node_id, result in state.node_results.items()
            },
        }

    def check_breakpoint(
        self,
        execution_id: uuid.UUID,
        node_id: str,
    ) -> bool:
        """
        Check if breakpoint is hit.

        Args:
            execution_id: Execution ID
            node_id: Node ID

        Returns:
            True if breakpoint is set
        """
        return f"{execution_id}:{node_id}" in self.breakpoints


# Default debugger instance
default_debugger = WorkflowDebugger()
