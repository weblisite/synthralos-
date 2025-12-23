"""
LangGraph Workflow Engine

Builds and executes LangGraph workflows from Workflow models.
Integrates LangGraph for business logic orchestration.
"""

import uuid
from typing import Any

from sqlmodel import Session

from app.models import Workflow
from app.workflows.activities import get_activity_handler


class LangGraphEngineError(Exception):
    """Base exception for LangGraph engine errors."""

    pass


class LangGraphEngine:
    """
    LangGraph-based workflow execution engine.

    Builds LangGraph graphs from Workflow models and executes them.
    This provides more sophisticated workflow execution than the basic engine.
    """

    def __init__(self):
        """Initialize LangGraph engine."""
        # Try to import LangGraph, but don't fail if not installed
        try:
            from langgraph.graph import END, START, StateGraph

            self.langgraph_available = True
            self.StateGraph = StateGraph
            self.END = END
            self.START = START
        except ImportError:
            self.langgraph_available = False
            self.StateGraph = None
            self.END = None
            self.START = None

    def build_graph(
        self,
        session: Session,
        workflow_id: uuid.UUID,
        version: int | None = None,
    ) -> Any:
        """
        Build a LangGraph graph from a Workflow model.

        Args:
            session: Database session
            workflow_id: Workflow ID
            version: Workflow version (uses current if None)

        Returns:
            LangGraph StateGraph instance

        Raises:
            LangGraphEngineError: If LangGraph is not available or build fails
        """
        if not self.langgraph_available:
            raise LangGraphEngineError(
                "LangGraph is not installed. Install with: pip install langgraph>=0.0.20"
            )

        workflow = session.get(Workflow, workflow_id)
        if not workflow:
            raise LangGraphEngineError(f"Workflow {workflow_id} not found")

        target_version = version or workflow.version

        # Get workflow state
        from app.workflows.engine import WorkflowEngine

        engine = WorkflowEngine()
        workflow_state = engine.get_workflow_state(session, workflow_id, target_version)

        # Create LangGraph StateGraph
        graph = self.StateGraph(dict)  # State is a simple dict for now

        # Get execution_id and session for node function closure
        exec_id = (
            execution_id or workflow_id
        )  # Use provided execution_id or workflow_id as fallback
        session_ref = session

        # Add nodes
        for node_id, node_config in workflow_state.nodes.items():
            node_type = node_config.get("node_type", "unknown")

            # Create node function with closure over exec_id and session_ref
            def make_node_func(n_id: str, n_config: dict[str, Any]):
                def node_func(state: dict[str, Any]) -> dict[str, Any]:
                    # Get execution UUID from state if available
                    exec_uuid_str = state.get("_execution_uuid")
                    exec_uuid = None
                    if exec_uuid_str:
                        try:
                            exec_uuid = uuid.UUID(exec_uuid_str)
                        except (ValueError, TypeError):
                            pass

                    # Use execution_id from closure or state
                    final_exec_id = exec_uuid or exec_id

                    # Get activity handler
                    handler = get_activity_handler(n_config.get("node_type", "unknown"))
                    if handler:
                        # Pass execution_id and session to handler
                        result = handler.execute(
                            node_id=n_id,
                            node_config=n_config,
                            input_data=state.get("data", {}),
                            execution_id=final_exec_id,
                            session=session_ref,
                        )
                        # Update state with node output
                        if result.status == "success":
                            state["data"] = state.get("data", {})
                            state["data"][f"{n_id}_output"] = result.output
                            state["current_node"] = n_id
                            state["last_result"] = {
                                "status": "success",
                                "output": result.output,
                            }
                        else:
                            state["last_result"] = {
                                "status": "failed",
                                "error": result.error,
                            }
                            state["error"] = result.error
                    else:
                        # Default handler
                        state["data"] = state.get("data", {})
                        state["current_node"] = n_id
                        state["last_result"] = {"status": "success", "output": {}}

                    return state

                return node_func

            graph.add_node(node_id, make_node_func(node_id, node_config))

        # Add edges
        if workflow_state.entry_node_id:
            graph.add_edge(self.START, workflow_state.entry_node_id)

        # Add edges between nodes
        for edge in workflow_state.edges:
            from_node = edge.get("from")
            to_node = edge.get("to")

            if from_node and to_node:
                # Check if this is a conditional edge
                if edge.get("condition"):
                    # Conditional edge - route based on condition
                    def make_condition_func(condition_expr: str):
                        def condition_func(state: dict[str, Any]) -> str:
                            # Simple condition evaluation (can be enhanced)
                            # For now, check last_result status
                            last_result = state.get("last_result", {})
                            if (
                                condition_expr == "success"
                                and last_result.get("status") == "success"
                            ):
                                return to_node
                            elif (
                                condition_expr == "failed"
                                and last_result.get("status") == "failed"
                            ):
                                return to_node
                            return self.END

                        return condition_func

                    graph.add_conditional_edges(
                        from_node,
                        make_condition_func(edge["condition"]),
                        {to_node: to_node, self.END: self.END},
                    )
                else:
                    # Simple edge
                    graph.add_edge(from_node, to_node)

        # Add end edges for nodes with no outgoing edges
        for node_id in workflow_state.nodes.keys():
            outgoing_edges = [
                e for e in workflow_state.edges if e.get("from") == node_id
            ]
            if not outgoing_edges:
                graph.add_edge(node_id, self.END)

        # Compile graph
        compiled_graph = graph.compile()

        return compiled_graph

    def execute_graph(
        self,
        graph: Any,
        initial_state: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Execute a LangGraph graph.

        Args:
            graph: Compiled LangGraph graph
            initial_state: Initial state dictionary

        Returns:
            Final state dictionary
        """
        if not self.langgraph_available:
            raise LangGraphEngineError("LangGraph is not installed")

        # Execute graph
        final_state = graph.invoke(initial_state)

        return final_state

    def execute_workflow(
        self,
        session: Session,
        execution_id: uuid.UUID,
    ) -> dict[str, Any]:
        """
        Execute a workflow using LangGraph.

        This is a higher-level method that:
        1. Gets the execution state
        2. Builds the graph
        3. Executes it
        4. Updates the execution state

        Args:
            session: Database session
            execution_id: Execution ID

        Returns:
            Final execution state
        """
        from app.workflows.engine import WorkflowEngine

        engine = WorkflowEngine()
        execution_state = engine.get_execution_state(session, execution_id)

        # Build graph with execution_id
        graph = self.build_graph(
            session,
            execution_state.workflow_id,
            execution_state.workflow_version,
            execution_id=execution_id,
        )

        # Prepare initial state
        initial_state = {
            "data": execution_state.execution_data,
            "execution_id": execution_state.execution_id,
            "workflow_id": str(execution_state.workflow_id),
        }

        # Execute graph
        try:
            final_state = self.execute_graph(graph, initial_state)

            # Update execution state
            execution_state.execution_data = final_state.get("data", {})

            # Check for errors
            if final_state.get("error"):
                execution_state.status = "failed"
                execution_state.error_message = final_state.get("error")
            else:
                execution_state.status = "completed"

            # Save updated state
            engine.save_execution_state(session, execution_id, execution_state)

            return final_state

        except Exception as e:
            # Mark execution as failed
            execution_state.status = "failed"
            execution_state.error_message = str(e)
            engine.save_execution_state(session, execution_id, execution_state)
            raise


# Default LangGraph engine instance
default_langgraph_engine = LangGraphEngine()
