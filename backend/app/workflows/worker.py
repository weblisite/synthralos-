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
from app.models import WorkflowExecution
from app.workflows.engine import WorkflowEngine
from app.workflows.scheduler import WorkflowScheduler
from app.workflows.signals import SignalHandler


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
            # 1. Process scheduled executions
            self._process_scheduled_executions(session)
            
            # 2. Process retry executions
            self._process_retry_executions(session)
            
            # 3. Process signal-waiting executions
            self._process_signal_executions(session)
            
            # 4. Process running executions
            self._process_running_executions(session)
    
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
        
        query = select(WorkflowExecution).where(
            WorkflowExecution.status == "failed",
            WorkflowExecution.next_retry_at <= now,
            WorkflowExecution.next_retry_at.isnot(None),
        ).limit(settings.WORKFLOW_WORKER_CONCURRENCY)
        
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
        query = select(WorkflowExecution).where(
            WorkflowExecution.status == "waiting_for_signal",
        ).limit(settings.WORKFLOW_WORKER_CONCURRENCY)
        
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
                    print(f"📨 Processed signal for execution: {execution.execution_id}")
            except Exception as e:
                print(f"⚠️  Error processing signal execution {execution.id}: {e}")
    
    def _process_running_executions(self, session: Session) -> None:
        """Process running executions."""
        query = select(WorkflowExecution).where(
            WorkflowExecution.status == "running",
        ).limit(settings.WORKFLOW_WORKER_CONCURRENCY)
        
        executions = session.exec(query).all()
        
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
        
        This is a simplified version that will be enhanced when LangGraph integration
        is complete. For now, it handles basic node execution.
        """
        state = self.workflow_engine.get_execution_state(session, execution_id)
        workflow_state = self.workflow_engine.get_workflow_state(
            session,
            state.workflow_id,
            state.workflow_version,
        )
        
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
        
        # Determine next node
        if result.status == "success":
            next_nodes = workflow_state.get_next_nodes(current_node_id)
            
            if next_nodes:
                # Continue to next node
                next_node_id = next_nodes[0]  # Simple: take first next node
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


def run_worker() -> None:
    """Entry point for running the worker."""
    worker = WorkflowWorker()
    worker.start()


if __name__ == "__main__":
    run_worker()

