"""
Workflow Execution State Management

Manages workflow execution state, including:
- Current execution point
- Node execution history
- State snapshots for replay
"""

import uuid
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class NodeExecutionResult(BaseModel):
    """Result of a single node execution."""

    node_id: str
    status: str  # "success", "failed", "skipped"
    output: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    started_at: datetime
    completed_at: datetime | None = None
    duration_ms: int = 0


class ExecutionState(BaseModel):
    """
    Execution state for a workflow run.

    This represents the current state of a workflow execution,
    including which nodes have been executed and their results.
    """

    execution_id: str
    workflow_id: UUID
    workflow_version: int
    status: str  # "running", "completed", "failed", "paused", "waiting_for_signal"
    current_node_id: str | None = None
    completed_node_ids: list[str] = Field(default_factory=list)
    node_results: dict[str, NodeExecutionResult] = Field(default_factory=dict)
    execution_data: dict[str, Any] = Field(
        default_factory=dict
    )  # Data passed between nodes
    started_at: datetime
    error_message: str | None = None
    retry_count: int = 0
    next_retry_at: datetime | None = None

    # Parallel execution tracking
    parallel_nodes: dict[str, list[str]] = Field(
        default_factory=dict
    )  # Track parallel node groups: group_id -> [node_ids]
    parallel_results: dict[str, dict[str, NodeExecutionResult]] = Field(
        default_factory=dict
    )  # Track parallel execution results: group_id -> {node_id: result}
    parallel_wait_mode: dict[str, str] = Field(
        default_factory=dict
    )  # Track wait mode for parallel groups: group_id -> "all"|"any"|"n_of_m"
    parallel_wait_n: dict[str, int] = Field(
        default_factory=dict
    )  # Track N for "n_of_m" mode: group_id -> n

    # Loop tracking
    loop_stacks: dict[str, list[dict[str, Any]]] = Field(
        default_factory=dict
    )  # Track loop contexts: loop_node_id -> [iteration_contexts]
    loop_iterations: dict[str, int] = Field(
        default_factory=dict
    )  # Track loop iteration counts: loop_node_id -> iteration_count
    loop_break_flags: dict[str, bool] = Field(
        default_factory=dict
    )  # Track break flags: loop_node_id -> should_break
    loop_continue_flags: dict[str, bool] = Field(
        default_factory=dict
    )  # Track continue flags: loop_node_id -> should_continue

    # Variable scoping
    variables: dict[str, dict[str, Any]] = Field(
        default_factory=dict
    )  # Track scoped variables: scope -> {var_name: value}

    # Timeout tracking
    node_timeouts: dict[str, datetime] = Field(
        default_factory=dict
    )  # Track node timeout deadlines: node_id -> deadline
    workflow_timeout: datetime | None = None

    # Error handling
    try_catch_blocks: dict[str, dict[str, Any]] = Field(
        default_factory=dict
    )  # Track try/catch blocks: block_id -> {try_node, catch_node, finally_node, error}

    # Sub-workflow tracking
    sub_workflow_executions: dict[str, uuid.UUID] = Field(
        default_factory=dict
    )  # Track sub-workflow executions: node_id -> sub_execution_id
    sub_workflow_waiting: dict[str, bool] = Field(
        default_factory=dict
    )  # Track if waiting for sub-workflow: node_id -> is_waiting

    def mark_node_completed(self, node_id: str, result: NodeExecutionResult) -> None:
        """Mark a node as completed and store its result."""
        if node_id not in self.completed_node_ids:
            self.completed_node_ids.append(node_id)
        self.node_results[node_id] = result
        self.current_node_id = None

    def set_current_node(self, node_id: str) -> None:
        """Set the current executing node."""
        self.current_node_id = node_id

    def get_node_result(self, node_id: str) -> NodeExecutionResult | None:
        """Get the execution result for a node."""
        return self.node_results.get(node_id)

    def to_dict(self) -> dict[str, Any]:
        """Convert state to dictionary for persistence."""
        return {
            "execution_id": self.execution_id,
            "workflow_id": str(self.workflow_id),
            "workflow_version": self.workflow_version,
            "status": self.status,
            "current_node_id": self.current_node_id,
            "completed_node_ids": self.completed_node_ids,
            "node_results": {
                node_id: {
                    "node_id": result.node_id,
                    "status": result.status,
                    "output": result.output,
                    "error": result.error,
                    "started_at": result.started_at.isoformat(),
                    "completed_at": result.completed_at.isoformat()
                    if result.completed_at
                    else None,
                    "duration_ms": result.duration_ms,
                }
                for node_id, result in self.node_results.items()
            },
            "execution_data": self.execution_data,
            "started_at": self.started_at.isoformat(),
            "error_message": self.error_message,
            "retry_count": self.retry_count,
            "next_retry_at": self.next_retry_at.isoformat()
            if self.next_retry_at
            else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ExecutionState":
        """Create ExecutionState from dictionary."""
        node_results = {}
        for node_id, result_data in data.get("node_results", {}).items():
            node_results[node_id] = NodeExecutionResult(
                node_id=result_data["node_id"],
                status=result_data["status"],
                output=result_data.get("output", {}),
                error=result_data.get("error"),
                started_at=datetime.fromisoformat(result_data["started_at"]),
                completed_at=datetime.fromisoformat(result_data["completed_at"])
                if result_data.get("completed_at")
                else None,
                duration_ms=result_data.get("duration_ms", 0),
            )

        # Parse parallel results
        parallel_results = {}
        for group_id, group_data in data.get("parallel_results", {}).items():
            parallel_results[group_id] = {
                node_id: NodeExecutionResult(
                    node_id=result_data["node_id"],
                    status=result_data["status"],
                    output=result_data.get("output", {}),
                    error=result_data.get("error"),
                    started_at=datetime.fromisoformat(result_data["started_at"]),
                    completed_at=datetime.fromisoformat(result_data["completed_at"])
                    if result_data.get("completed_at")
                    else None,
                    duration_ms=result_data.get("duration_ms", 0),
                )
                for node_id, result_data in group_data.items()
            }

        # Parse node timeouts
        node_timeouts = {}
        for node_id, timeout_str in data.get("node_timeouts", {}).items():
            node_timeouts[node_id] = datetime.fromisoformat(timeout_str)

        # Parse sub-workflow executions
        sub_workflow_executions = {}
        for node_id, exec_id_str in data.get("sub_workflow_executions", {}).items():
            sub_workflow_executions[node_id] = UUID(exec_id_str)

        return cls(
            execution_id=data["execution_id"],
            workflow_id=UUID(data["workflow_id"]),
            workflow_version=data["workflow_version"],
            status=data["status"],
            current_node_id=data.get("current_node_id"),
            completed_node_ids=data.get("completed_node_ids", []),
            node_results=node_results,
            execution_data=data.get("execution_data", {}),
            started_at=datetime.fromisoformat(data["started_at"]),
            error_message=data.get("error_message"),
            retry_count=data.get("retry_count", 0),
            next_retry_at=datetime.fromisoformat(data["next_retry_at"])
            if data.get("next_retry_at")
            else None,
            # Parallel execution tracking
            parallel_nodes=data.get("parallel_nodes", {}),
            parallel_results=parallel_results,
            parallel_wait_mode=data.get("parallel_wait_mode", {}),
            parallel_wait_n=data.get("parallel_wait_n", {}),
            # Loop tracking
            loop_stacks=data.get("loop_stacks", {}),
            loop_iterations=data.get("loop_iterations", {}),
            loop_break_flags=data.get("loop_break_flags", {}),
            loop_continue_flags=data.get("loop_continue_flags", {}),
            # Variable scoping
            variables=data.get("variables", {}),
            # Timeout tracking
            node_timeouts=node_timeouts,
            workflow_timeout=datetime.fromisoformat(data["workflow_timeout"])
            if data.get("workflow_timeout")
            else None,
            # Error handling
            try_catch_blocks=data.get("try_catch_blocks", {}),
            # Sub-workflow tracking
            sub_workflow_executions=sub_workflow_executions,
            sub_workflow_waiting=data.get("sub_workflow_waiting", {}),
        )


class WorkflowState(BaseModel):
    """
    Workflow definition state.

    Represents the structure and configuration of a workflow,
    including its nodes and graph configuration.
    """

    workflow_id: UUID
    version: int
    nodes: dict[str, dict[str, Any]] = Field(
        default_factory=dict
    )  # node_id -> node config
    edges: list[dict[str, str]] = Field(
        default_factory=list
    )  # [{"from": "node1", "to": "node2"}]
    entry_node_id: str | None = None

    def get_node_config(self, node_id: str) -> dict[str, Any] | None:
        """Get configuration for a specific node."""
        return self.nodes.get(node_id)

    def get_next_nodes(self, node_id: str, branch: str | None = None) -> list[str]:
        """
        Get list of nodes that come after the given node.

        Args:
            node_id: Source node ID
            branch: Optional branch name ("true", "false", etc.) for conditional routing

        Returns:
            List of next node IDs
        """
        next_nodes = []

        # Filter edges by source node
        for edge in self.edges:
            if edge.get("from") == node_id:
                # Check if edge has branch condition
                edge_branch = edge.get("branch") or edge.get("condition")

                # If branch is specified, only return nodes matching that branch
                if branch and edge_branch:
                    if edge_branch == branch:
                        next_nodes.append(edge["to"])
                elif not branch or not edge_branch:
                    # No branch filtering, or edge has no branch condition
                    next_nodes.append(edge["to"])

        return next_nodes

    def get_entry_node(self) -> str | None:
        """Get the entry node ID."""
        return self.entry_node_id
