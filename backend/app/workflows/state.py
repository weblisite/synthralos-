"""
Workflow Execution State Management

Manages workflow execution state, including:
- Current execution point
- Node execution history
- State snapshots for replay
"""

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

    def get_next_nodes(self, node_id: str) -> list[str]:
        """Get list of nodes that come after the given node."""
        return [edge["to"] for edge in self.edges if edge.get("from") == node_id]

    def get_entry_node(self) -> str | None:
        """Get the entry node ID."""
        return self.entry_node_id
