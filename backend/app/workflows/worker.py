"""
Workflow Worker Service

Background worker for executing workflows, processing nodes, and handling signals.
This worker runs continuously, polling for work and executing workflow steps.
"""

import time
import uuid
from datetime import datetime
from typing import Any

from sqlmodel import Session, select

from app.core.config import settings
from app.core.db import engine
from app.models import Workflow, WorkflowExecution
from app.workflows.engine import WorkflowEngine
from app.workflows.scheduler import WorkflowScheduler
from app.workflows.signals import SignalHandler
from app.workflows.timeout import TimeoutManager


class WorkerError(Exception):
    """Base exception for worker errors."""

    pass


class WorkflowWorker:
    """
    Background worker for workflow execution.

    Polls for:
    - Running executions that need processing
    - Executions waiting for retry
    - Executions waiting for signals
    - Scheduled executions (via scheduler)
    """

    def __init__(
        self,
        workflow_engine: WorkflowEngine | None = None,
        scheduler: WorkflowScheduler | None = None,
        signal_handler: SignalHandler | None = None,
        poll_interval: float = 1.0,
    ):
        """
        Initialize workflow worker.

        Args:
            workflow_engine: WorkflowEngine instance
            scheduler: WorkflowScheduler instance
            signal_handler: SignalHandler instance
            poll_interval: Seconds between polls
        """
        self.workflow_engine = workflow_engine or WorkflowEngine()
        self.scheduler = scheduler or WorkflowScheduler(self.workflow_engine)
        self.signal_handler = signal_handler or SignalHandler()
        self.timeout_manager = TimeoutManager(self.workflow_engine)
        self.poll_interval = poll_interval
        self.running = False

    def start(self) -> None:
        """Start the worker loop."""
        self.running = True
        print(f"🚀 Workflow worker started (poll_interval={self.poll_interval}s)")

        while self.running:
            try:
                self._process_cycle()
                time.sleep(self.poll_interval)
            except KeyboardInterrupt:
                print("\n🛑 Worker stopping...")
                self.stop()
                break
            except Exception as e:
                print(f"❌ Worker error: {e}")
                time.sleep(self.poll_interval)

    def stop(self) -> None:
        """Stop the worker."""
        self.running = False
        print("✅ Workflow worker stopped")

    def _process_cycle(self) -> None:
        """Process one cycle of work."""
        with Session(engine) as session:
            # 1. Check for timeouts
            self._check_timeouts(session)

            # 2. Process scheduled executions
            self._process_scheduled_executions(session)

            # 3. Process retry executions
            self._process_retry_executions(session)

            # 4. Process signal-waiting executions
            self._process_signal_executions(session)

            # 5. Process running executions
            self._process_running_executions(session)

    def _check_timeouts(self, session: Session) -> None:
        """Check for timed-out executions and handle them."""
        try:
            # Get all running executions
            query = select(WorkflowExecution).where(
                WorkflowExecution.status == "running"
            )
            executions = session.exec(query).all()

            for execution in executions:
                try:
                    # Check workflow timeout
                    if self.timeout_manager.check_workflow_timeout(
                        session, execution.id
                    ):
                        self.timeout_manager.handle_workflow_timeout(
                            session, execution.id
                        )
                        print(f"⏱️  Workflow execution {execution.id} timed out")

                    # Check node timeout if there's a current node
                    state = self.workflow_engine.get_execution_state(
                        session, execution.id
                    )
                    if state.current_node_id:
                        if self.timeout_manager.check_node_timeout(
                            session, execution.id, state.current_node_id
                        ):
                            self.timeout_manager.handle_node_timeout(
                                session,
                                execution.id,
                                state.current_node_id,
                                retry=False,
                            )
                            print(
                                f"⏱️  Node {state.current_node_id} in execution {execution.id} timed out"
                            )
                except Exception as e:
                    print(
                        f"⚠️  Error checking timeout for execution {execution.id}: {e}"
                    )
        except Exception as e:
            print(f"⚠️  Error checking timeouts: {e}")

    def _process_scheduled_executions(self, session: Session) -> None:
        """Process due scheduled executions."""
        try:
            execution_ids = self.scheduler.process_due_schedules(session, limit=10)
            if execution_ids:
                print(f"📅 Triggered {len(execution_ids)} scheduled executions")
        except Exception as e:
            print(f"⚠️  Error processing scheduled executions: {e}")

    def _process_retry_executions(self, session: Session) -> None:
        """Process executions that are due for retry."""
        now = datetime.utcnow()

        query = (
            select(WorkflowExecution)
            .where(
                WorkflowExecution.status == "failed",
                WorkflowExecution.next_retry_at <= now,
                WorkflowExecution.next_retry_at.isnot(None),
            )
            .limit(settings.WORKFLOW_WORKER_CONCURRENCY)
        )

        executions = session.exec(query).all()

        for execution in executions:
            try:
                # Resume execution for retry
                state = self.workflow_engine.get_execution_state(session, execution.id)
                state.status = "running"
                state.next_retry_at = None
                self.workflow_engine.save_execution_state(session, execution.id, state)

                print(f"🔄 Retrying execution: {execution.execution_id}")
            except Exception as e:
                print(f"⚠️  Error retrying execution {execution.id}: {e}")

    def _process_signal_executions(self, session: Session) -> None:
        """Process executions waiting for signals."""
        query = (
            select(WorkflowExecution)
            .where(
                WorkflowExecution.status == "waiting_for_signal",
            )
            .limit(settings.WORKFLOW_WORKER_CONCURRENCY)
        )

        executions = session.exec(query).all()

        for execution in executions:
            try:
                # Check for pending signals
                state = self.workflow_engine.get_execution_state(session, execution.id)

                # Get pending signals
                pending_signals = self.signal_handler.get_pending_signals(
                    session,
                    execution.id,
                )

                if pending_signals:
                    # Process first signal
                    signal = pending_signals[0]
                    self.workflow_engine.process_signal(
                        session,
                        execution.id,
                        signal.signal_type,
                        signal.signal_data,
                    )
                    print(
                        f"📨 Processed signal for execution: {execution.execution_id}"
                    )
            except Exception as e:
                print(f"⚠️  Error processing signal execution {execution.id}: {e}")

    def _process_running_executions(self, session: Session) -> None:
        """Process running executions (prioritized)."""
        from app.workflows.prioritization import default_prioritization_manager

        # Get prioritized executions
        executions = default_prioritization_manager.get_prioritized_executions(
            session,
            status="running",
            limit=settings.WORKFLOW_WORKER_CONCURRENCY,
        )

        for execution in executions:
            try:
                self._execute_workflow_step(session, execution.id)
            except Exception as e:
                print(f"⚠️  Error processing execution {execution.id}: {e}")
                # Mark as failed if error persists
                try:
                    self.workflow_engine.fail_execution(
                        session,
                        execution.id,
                        f"Worker error: {str(e)}",
                        schedule_retry=True,
                    )
                except Exception:
                    pass

    def _execute_workflow_step(
        self,
        session: Session,
        execution_id: uuid.UUID,
    ) -> None:
        """
        Execute one step of a workflow.

        Uses LangGraph for complex workflows if available, otherwise falls back to
        simplified sequential execution.
        """
        state = self.workflow_engine.get_execution_state(session, execution_id)
        workflow_state = self.workflow_engine.get_workflow_state(
            session,
            state.workflow_id,
            state.workflow_version,
        )

        # Check if workflow should use LangGraph
        # Use LangGraph if:
        # 1. LangGraph is available
        # 2. Workflow has complex structure (multiple branches, loops, etc.)
        # 3. Or explicitly enabled in workflow config
        use_langgraph = False
        try:
            from app.workflows.langgraph_engine import LangGraphEngine

            langgraph_engine = LangGraphEngine()
            if langgraph_engine.langgraph_available:
                # Check if workflow has complex structure
                workflow = session.get(Workflow, state.workflow_id)
                if workflow:
                    graph_config = workflow.graph_config or {}
                    # Use LangGraph if workflow has complex features
                    has_conditions = any(
                        node.get("node_type") in ("condition", "if", "switch")
                        for node in workflow_state.nodes.values()
                    )
                    has_parallel = (
                        len(workflow_state.edges) > len(workflow_state.nodes) - 1
                    )
                    use_langgraph = (
                        has_conditions
                        or has_parallel
                        or graph_config.get("use_langgraph", False)
                    )

                    if use_langgraph:
                        # Execute using LangGraph
                        try:
                            final_state = langgraph_engine.execute_workflow(
                                session=session,
                                execution_id=execution_id,
                            )
                            # LangGraph handles state updates internally
                            return
                        except Exception as e:
                            # Fallback to simple execution if LangGraph fails
                            print(
                                f"⚠️  LangGraph execution failed, falling back to simple execution: {e}"
                            )
                            use_langgraph = False
        except ImportError:
            # LangGraph not available, use simple execution
            pass
        except Exception as e:
            print(f"⚠️  Error checking LangGraph availability: {e}")

        # Use simplified sequential execution
        self._execute_workflow_step_simple(session, execution_id, state, workflow_state)

    def _execute_workflow_step_simple(
        self,
        session: Session,
        execution_id: uuid.UUID,
        state: Any,
        workflow_state: Any,
    ) -> None:
        """
        Execute one step using simplified sequential execution.

        This is the original implementation for basic workflows.
        """

        # Determine next node to execute
        current_node_id = state.current_node_id

        if not current_node_id:
            # Start from entry node
            entry_node_id = workflow_state.get_entry_node()
            if not entry_node_id:
                # No entry node, mark as completed
                self.workflow_engine.complete_execution(session, execution_id)
                return

            current_node_id = entry_node_id
            state.set_current_node(current_node_id)
            self.workflow_engine.save_execution_state(session, execution_id, state)

        # Get node config
        node_config = workflow_state.get_node_config(current_node_id)
        if not node_config:
            # Node not found, mark as failed
            self.workflow_engine.fail_execution(
                session,
                execution_id,
                f"Node {current_node_id} not found in workflow",
            )
            return

        # Execute node
        result = self.workflow_engine.execute_node(
            session,
            execution_id,
            current_node_id,
            node_config,
            state.execution_data,
        )

        # Update state
        state.mark_node_completed(current_node_id, result)

        # Update execution data with node output
        if result.status == "success":
            state.execution_data[f"{current_node_id}_output"] = result.output

        # Determine next node(s)
        if result.status == "success":
            # Check if node output indicates a branch (for condition nodes)
            branch = None
            if isinstance(result.output, dict):
                branch = result.output.get(
                    "branch"
                )  # "true" or "false" from condition node

            # Get next nodes (filtered by branch if condition node)
            next_nodes = workflow_state.get_next_nodes(current_node_id, branch=branch)

            # Check if we should execute nodes in parallel
            # If multiple next nodes and no explicit sequential flag, execute in parallel
            execute_parallel = (
                len(next_nodes) > 1
                and not node_config.get("sequential", False)
                and node_config.get(
                    "parallel", True
                )  # Default to parallel for multiple outputs
            )

            if execute_parallel:
                # Execute all next nodes in parallel using ParallelExecutionManager
                from app.workflows.parallel import default_parallel_manager

                # Get parallel execution configuration
                parallel_group_id = f"{current_node_id}_parallel"
                wait_mode = node_config.get(
                    "parallel_wait_mode", "all"
                )  # "all", "any", "n_of_m"
                wait_n = node_config.get("parallel_wait_n")

                # Prepare node configs for parallel execution
                node_configs = {}
                for next_node_id in next_nodes:
                    node_configs[next_node_id] = (
                        workflow_state.get_node_config(next_node_id) or {}
                    )

                # Track parallel execution
                state.parallel_nodes[parallel_group_id] = next_nodes
                state.parallel_wait_mode[parallel_group_id] = wait_mode
                if wait_n:
                    state.parallel_wait_n[parallel_group_id] = wait_n

                # Execute nodes in parallel
                if wait_mode == "all":
                    aggregated = default_parallel_manager.wait_for_all(
                        session,
                        execution_id,
                        next_nodes,
                        node_configs,
                        state.execution_data,
                    )
                elif wait_mode == "any":
                    aggregated = default_parallel_manager.wait_for_any(
                        session,
                        execution_id,
                        next_nodes,
                        node_configs,
                        state.execution_data,
                    )
                elif wait_mode == "n_of_m" and wait_n:
                    aggregated = default_parallel_manager.wait_for_n_of_m(
                        session,
                        execution_id,
                        next_nodes,
                        node_configs,
                        state.execution_data,
                        wait_n,
                    )
                else:
                    # Default to "all"
                    aggregated = default_parallel_manager.wait_for_all(
                        session,
                        execution_id,
                        next_nodes,
                        node_configs,
                        state.execution_data,
                    )

                # Store parallel results
                # Note: Results are already stored by execute_node, but we aggregate them here
                state.parallel_results[parallel_group_id] = {
                    node_id: state.node_results.get(node_id)
                    for node_id in next_nodes
                    if node_id in state.node_results
                }

                # Check if all parallel nodes completed successfully
                all_success = (
                    aggregated.get("all_completed", False)
                    if wait_mode == "all"
                    else True
                )

                if not all_success and wait_mode == "all":
                    # Some parallel nodes failed
                    failed_count = aggregated.get("failed_count", 0)
                    self.workflow_engine.fail_execution(
                        session,
                        execution_id,
                        f"Parallel execution failed: {failed_count} of {len(next_nodes)} nodes failed",
                        schedule_retry=True,
                    )
                    return

                # Aggregate results into execution_data
                aggregation_type = node_config.get("parallel_aggregation", "merge")
                aggregated_output = default_parallel_manager.aggregate_results(
                    state.parallel_results[parallel_group_id],
                    aggregation_type,
                )
                state.execution_data[f"{parallel_group_id}_result"] = aggregated_output

                # Get next nodes after parallel execution
                # Find nodes that come after ALL parallel nodes (fan-in)
                fan_in_nodes = []
                for parallel_node_id in next_nodes:
                    fan_in_nodes.extend(workflow_state.get_next_nodes(parallel_node_id))

                # Remove duplicates while preserving order
                seen = set()
                unique_fan_in_nodes = []
                for node_id in fan_in_nodes:
                    if node_id not in seen:
                        seen.add(node_id)
                        unique_fan_in_nodes.append(node_id)

                if unique_fan_in_nodes:
                    # Continue to fan-in nodes
                    state.set_current_node(unique_fan_in_nodes[0])
                    if len(unique_fan_in_nodes) > 1:
                        # Multiple fan-in nodes, will be handled in next iteration
                        state.execution_data["_fan_in_queue"] = unique_fan_in_nodes[1:]
                else:
                    # No fan-in nodes, workflow complete
                    self.workflow_engine.complete_execution(
                        session,
                        execution_id,
                        final_data=state.execution_data,
                    )
                    return
            elif next_nodes:
                # Sequential execution: take first next node
                next_node_id = next_nodes[0]
                state.set_current_node(next_node_id)
            else:
                # No more nodes, workflow complete
                self.workflow_engine.complete_execution(
                    session,
                    execution_id,
                    final_data=state.execution_data,
                )
                return
        else:
            # Node failed, mark execution as failed
            self.workflow_engine.fail_execution(
                session,
                execution_id,
                f"Node {current_node_id} failed: {result.error}",
                schedule_retry=True,
            )
            return

        # Save updated state
        self.workflow_engine.save_execution_state(session, execution_id, state)

        # Check if we need to process parallel nodes
        if state.execution_data.get(f"{current_node_id}_parallel_executing"):
            parallel_queue = state.execution_data.get("_parallel_queue", [])
            if parallel_queue:
                # Process next parallel node
                next_parallel_node = parallel_queue[0]
                state.execution_data["_parallel_queue"] = parallel_queue[1:]
                state.set_current_node(next_parallel_node)
                self.workflow_engine.save_execution_state(session, execution_id, state)


def run_worker() -> None:
    """Entry point for running the worker."""
    worker = WorkflowWorker()
    worker.start()


if __name__ == "__main__":
    run_worker()
