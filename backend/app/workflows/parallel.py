"""
Parallel Execution Manager

Handles parallel node execution with fan-in patterns:
- Execute multiple nodes in parallel
- Wait for all/any/N of M nodes to complete
- Aggregate results from parallel nodes
"""

import concurrent.futures
import uuid
from datetime import datetime
from typing import Any

from sqlmodel import Session

from app.workflows.engine import WorkflowEngine
from app.workflows.state import NodeExecutionResult


class ParallelExecutionError(Exception):
    """Base exception for parallel execution errors."""

    pass


class ParallelExecutionManager:
    """
    Manages parallel node execution with fan-in patterns.
    """

    def __init__(
        self,
        workflow_engine: WorkflowEngine | None = None,
        max_workers: int = 10,
    ):
        """
        Initialize parallel execution manager.

        Args:
            workflow_engine: WorkflowEngine instance
            max_workers: Maximum number of parallel workers
        """
        self.workflow_engine = workflow_engine or WorkflowEngine()
        self.max_workers = max_workers
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)

    def execute_nodes_parallel(
        self,
        session: Session,
        execution_id: uuid.UUID,
        node_ids: list[str],
        node_configs: dict[str, dict[str, Any]],
        input_data: dict[str, Any],
    ) -> dict[str, NodeExecutionResult]:
        """
        Execute multiple nodes in parallel.

        Args:
            session: Database session
            execution_id: Execution ID
            node_ids: List of node IDs to execute
            node_configs: Dictionary of node_id -> node_config
            input_data: Input data for nodes

        Returns:
            Dictionary of node_id -> NodeExecutionResult
        """
        if not node_ids:
            return {}

        # Create thread-local session for each parallel execution
        def execute_node(node_id: str) -> tuple[str, NodeExecutionResult]:
            # Create new session for this thread
            from app.core.db import engine

            with Session(engine) as thread_session:
                node_config = node_configs.get(node_id, {})
                result = self.workflow_engine.execute_node(
                    thread_session,
                    execution_id,
                    node_id,
                    node_config,
                    input_data,
                )
                return (node_id, result)

        # Execute all nodes in parallel
        futures = {
            self._executor.submit(execute_node, node_id): node_id
            for node_id in node_ids
        }

        results = {}
        for future in concurrent.futures.as_completed(futures):
            node_id = futures[future]
            try:
                _, result = future.result()
                results[node_id] = result
            except Exception as e:
                # Create failed result
                results[node_id] = NodeExecutionResult(
                    node_id=node_id,
                    status="failed",
                    output={},
                    error=f"Parallel execution failed: {str(e)}",
                    started_at=datetime.utcnow(),
                    completed_at=datetime.utcnow(),
                    duration_ms=0,
                )

        return results

    def wait_for_all(
        self,
        session: Session,
        execution_id: uuid.UUID,
        node_ids: list[str],
        node_configs: dict[str, dict[str, Any]],
        input_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Wait for all parallel nodes to complete (fan-in: all).

        Args:
            session: Database session
            execution_id: Execution ID
            node_ids: List of node IDs to execute
            node_configs: Dictionary of node_id -> node_config
            input_data: Input data for nodes

        Returns:
            Aggregated results dictionary
        """
        results = self.execute_nodes_parallel(
            session, execution_id, node_ids, node_configs, input_data
        )

        # Aggregate results
        aggregated = {
            "all_completed": all(r.status == "success" for r in results.values()),
            "results": {
                node_id: {
                    "status": result.status,
                    "output": result.output,
                    "error": result.error,
                }
                for node_id, result in results.items()
            },
            "success_count": sum(1 for r in results.values() if r.status == "success"),
            "failed_count": sum(1 for r in results.values() if r.status == "failed"),
        }

        return aggregated

    def wait_for_any(
        self,
        session: Session,
        execution_id: uuid.UUID,
        node_ids: list[str],
        node_configs: dict[str, dict[str, Any]],
        input_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Wait for any parallel node to complete (fan-in: any).

        Args:
            session: Database session
            execution_id: Execution ID
            node_ids: List of node IDs to execute
            node_configs: Dictionary of node_id -> node_config
            input_data: Input data for nodes

        Returns:
            First successful result or all results if none succeed
        """
        if not node_ids:
            return {"completed": False, "result": None}

        # Create thread-local session for each parallel execution
        def execute_node(node_id: str) -> tuple[str, NodeExecutionResult]:
            from app.core.db import engine

            with Session(engine) as thread_session:
                node_config = node_configs.get(node_id, {})
                result = self.workflow_engine.execute_node(
                    thread_session,
                    execution_id,
                    node_id,
                    node_config,
                    input_data,
                )
                return (node_id, result)

        # Execute all nodes in parallel, return first success
        futures = {
            self._executor.submit(execute_node, node_id): node_id
            for node_id in node_ids
        }

        completed_results = {}
        first_success = None

        for future in concurrent.futures.as_completed(futures):
            node_id = futures[future]
            try:
                _, result = future.result()
                completed_results[node_id] = result

                # If this is the first success, we can return early
                if result.status == "success" and first_success is None:
                    first_success = (node_id, result)
                    # Cancel remaining futures (they'll continue but we don't wait)
                    for f in futures:
                        if f != future:
                            f.cancel()

            except Exception as e:
                completed_results[node_id] = NodeExecutionResult(
                    node_id=node_id,
                    status="failed",
                    output={},
                    error=f"Parallel execution failed: {str(e)}",
                    started_at=datetime.utcnow(),
                    completed_at=datetime.utcnow(),
                    duration_ms=0,
                )

        if first_success:
            return {
                "completed": True,
                "first_success": first_success[0],
                "result": first_success[1].output,
                "all_results": {
                    node_id: {
                        "status": result.status,
                        "output": result.output,
                        "error": result.error,
                    }
                    for node_id, result in completed_results.items()
                },
            }
        else:
            return {
                "completed": False,
                "all_failed": True,
                "results": {
                    node_id: {
                        "status": result.status,
                        "output": result.output,
                        "error": result.error,
                    }
                    for node_id, result in completed_results.items()
                },
            }

    def wait_for_n_of_m(
        self,
        session: Session,
        execution_id: uuid.UUID,
        node_ids: list[str],
        node_configs: dict[str, dict[str, Any]],
        input_data: dict[str, Any],
        n: int,
    ) -> dict[str, Any]:
        """
        Wait for N of M parallel nodes to complete (fan-in: N of M).

        Args:
            session: Database session
            execution_id: Execution ID
            node_ids: List of node IDs to execute
            node_configs: Dictionary of node_id -> node_config
            input_data: Input data for nodes
            n: Number of nodes that must complete successfully

        Returns:
            Aggregated results when N nodes complete
        """
        if n > len(node_ids):
            raise ParallelExecutionError(
                f"Cannot wait for {n} nodes when only {len(node_ids)} nodes provided"
            )

        # Create thread-local session for each parallel execution
        def execute_node(node_id: str) -> tuple[str, NodeExecutionResult]:
            from app.core.db import engine

            with Session(engine) as thread_session:
                node_config = node_configs.get(node_id, {})
                result = self.workflow_engine.execute_node(
                    thread_session,
                    execution_id,
                    node_id,
                    node_config,
                    input_data,
                )
                return (node_id, result)

        # Execute all nodes in parallel
        futures = {
            self._executor.submit(execute_node, node_id): node_id
            for node_id in node_ids
        }

        completed_results = {}
        success_count = 0

        for future in concurrent.futures.as_completed(futures):
            node_id = futures[future]
            try:
                _, result = future.result()
                completed_results[node_id] = result

                if result.status == "success":
                    success_count += 1

                # If we've reached N successes, we can return
                if success_count >= n:
                    # Cancel remaining futures
                    for f in futures:
                        if f != future:
                            f.cancel()
                    break

            except Exception as e:
                completed_results[node_id] = NodeExecutionResult(
                    node_id=node_id,
                    status="failed",
                    output={},
                    error=f"Parallel execution failed: {str(e)}",
                    started_at=datetime.utcnow(),
                    completed_at=datetime.utcnow(),
                    duration_ms=0,
                )

        return {
            "completed": success_count >= n,
            "success_count": success_count,
            "required_count": n,
            "results": {
                node_id: {
                    "status": result.status,
                    "output": result.output,
                    "error": result.error,
                }
                for node_id, result in completed_results.items()
            },
        }

    def aggregate_results(
        self,
        results: dict[str, NodeExecutionResult],
        aggregation_type: str = "merge",
    ) -> dict[str, Any]:
        """
        Aggregate results from parallel node executions.

        Args:
            results: Dictionary of node_id -> NodeExecutionResult
            aggregation_type: Type of aggregation ("merge", "array", "first", "last")

        Returns:
            Aggregated result dictionary
        """
        if aggregation_type == "merge":
            # Merge all outputs into single dictionary
            aggregated = {}
            for node_id, result in results.items():
                if result.status == "success" and isinstance(result.output, dict):
                    aggregated.update(result.output)
                aggregated[f"{node_id}_status"] = result.status
            return aggregated

        elif aggregation_type == "array":
            # Return array of results
            return [
                {
                    "node_id": node_id,
                    "status": result.status,
                    "output": result.output,
                    "error": result.error,
                }
                for node_id, result in results.items()
            ]

        elif aggregation_type == "first":
            # Return first successful result
            for node_id, result in results.items():
                if result.status == "success":
                    return {"node_id": node_id, "result": result.output}
            return {"result": None, "all_failed": True}

        elif aggregation_type == "last":
            # Return last result
            if results:
                last_node_id = list(results.keys())[-1]
                last_result = results[last_node_id]
                return {
                    "node_id": last_node_id,
                    "result": last_result.output,
                    "status": last_result.status,
                }
            return {"result": None}

        else:
            # Default: return all results
            return {
                "results": {
                    node_id: {
                        "status": result.status,
                        "output": result.output,
                        "error": result.error,
                    }
                    for node_id, result in results.items()
                }
            }


# Default parallel execution manager
default_parallel_manager = ParallelExecutionManager()
