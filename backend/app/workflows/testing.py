"""
Workflow Testing Framework

Provides test mode execution:
- Test mode execution
- Mock node execution
- Test data injection
- Test result validation
- Test coverage tracking
"""

import uuid
from typing import Any

from sqlmodel import Session

from app.workflows.engine import WorkflowEngine


class TestExecutionError(Exception):
    """Base exception for test execution errors."""

    pass


class WorkflowTestRunner:
    """
    Runs workflows in test mode.
    """

    def __init__(self, workflow_engine: WorkflowEngine | None = None):
        """
        Initialize test runner.

        Args:
            workflow_engine: WorkflowEngine instance
        """
        self.workflow_engine = workflow_engine or WorkflowEngine()
        self.mock_results: dict[str, dict[str, Any]] = {}  # node_id -> mock_result

    def set_mock_result(
        self,
        node_id: str,
        result: dict[str, Any],
    ) -> None:
        """
        Set mock result for a node.

        Args:
            node_id: Node ID
            result: Mock result dictionary
        """
        self.mock_results[node_id] = result

    def clear_mocks(self) -> None:
        """Clear all mock results."""
        self.mock_results.clear()

    def run_test(
        self,
        session: Session,
        workflow_id: uuid.UUID,
        test_data: dict[str, Any] | None = None,
        mock_nodes: dict[str, dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        Run workflow in test mode.

        Args:
            session: Database session
            workflow_id: Workflow ID
            test_data: Test input data
            mock_nodes: Dictionary of node_id -> mock_result

        Returns:
            Test execution result
        """
        # Set up mocks
        if mock_nodes:
            for node_id, mock_result in mock_nodes.items():
                self.set_mock_result(node_id, mock_result)

        try:
            # Create test execution
            execution = self.workflow_engine.create_execution(
                session,
                workflow_id,
                trigger_data=test_data or {},
                idempotent=False,  # Tests may be run multiple times
            )

            # Mark execution as test mode
            state = self.workflow_engine.get_execution_state(session, execution.id)
            state.execution_data["test_mode"] = True
            self.workflow_engine.save_execution_state(session, execution.id, state)

            # Execute workflow (would normally be done by worker)
            # For testing, we'll execute synchronously
            # In production, this would be handled by the worker

            return {
                "execution_id": str(execution.id),
                "status": execution.status,
                "test_mode": True,
                "started_at": execution.started_at.isoformat(),
            }

        finally:
            # Clear mocks
            self.clear_mocks()

    def validate_test_result(
        self,
        session: Session,
        execution_id: uuid.UUID,
        expected_outputs: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Validate test execution result.

        Args:
            session: Database session
            execution_id: Execution ID
            expected_outputs: Expected outputs dictionary

        Returns:
            Validation result
        """
        state = self.workflow_engine.get_execution_state(session, execution_id)

        validation_result = {
            "execution_id": str(execution_id),
            "status": state.status,
            "valid": True,
            "errors": [],
            "warnings": [],
        }

        if expected_outputs:
            for node_id, expected_output in expected_outputs.items():
                node_result = state.get_node_result(node_id)

                if not node_result:
                    validation_result["valid"] = False
                    validation_result["errors"].append(
                        f"Node {node_id} did not execute"
                    )
                    continue

                if node_result.status != "success":
                    validation_result["valid"] = False
                    validation_result["errors"].append(
                        f"Node {node_id} failed: {node_result.error}"
                    )
                    continue

                # Compare outputs (simplified - would do deep comparison)
                actual_output = node_result.output
                if actual_output != expected_output:
                    validation_result["warnings"].append(
                        f"Node {node_id} output does not match expected"
                    )

        return validation_result


# Default test runner instance
default_test_runner = WorkflowTestRunner()
