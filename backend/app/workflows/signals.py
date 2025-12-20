"""
Workflow Signal System

Handles event-driven workflow continuation via signals.
Signals can be:
- Webhooks (from connectors)
- Human input (user responses)
- Connector ready (OAuth completion)
- Custom signals
"""

import uuid
from datetime import datetime
from typing import Any

from sqlmodel import Session, select

from app.models import WorkflowExecution, WorkflowSignal


class SignalError(Exception):
    """Base exception for signal errors."""

    pass


class SignalNotFoundError(SignalError):
    """Signal not found."""

    pass


class SignalHandler:
    """
    Handles workflow signals.

    Signals allow workflows to pause and wait for external events,
    then resume execution when the signal is received.
    """

    def emit_signal(
        self,
        session: Session,
        execution_id: uuid.UUID,
        signal_type: str,
        signal_data: dict[str, Any],
    ) -> WorkflowSignal:
        """
        Emit a signal to a workflow execution.

        Args:
            session: Database session
            execution_id: Execution ID to signal
            signal_type: Type of signal (webhook, human_input, connector_ready, etc.)
            signal_data: Signal payload data

        Returns:
            WorkflowSignal instance
        """
        # Verify execution exists
        execution = session.get(WorkflowExecution, execution_id)
        if not execution:
            raise SignalError(f"Execution {execution_id} not found")

        # Create signal record
        signal = WorkflowSignal(
            execution_id=execution_id,
            signal_type=signal_type,
            signal_data=signal_data,
            received_at=datetime.utcnow(),
            processed=False,
        )

        session.add(signal)
        session.commit()
        session.refresh(signal)

        return signal

    def get_pending_signals(
        self,
        session: Session,
        execution_id: uuid.UUID,
        signal_type: str | None = None,
    ) -> list[WorkflowSignal]:
        """
        Get pending signals for an execution.

        Args:
            session: Database session
            execution_id: Execution ID
            signal_type: Optional filter by signal type

        Returns:
            List of pending signals
        """
        query = select(WorkflowSignal).where(
            WorkflowSignal.execution_id == execution_id,
            WorkflowSignal.processed == False,
        )

        if signal_type:
            query = query.where(WorkflowSignal.signal_type == signal_type)

        signals = session.exec(query).all()
        return list(signals)

    def mark_signal_processed(
        self,
        session: Session,
        signal_id: uuid.UUID,
    ) -> None:
        """
        Mark a signal as processed.

        Args:
            session: Database session
            signal_id: Signal ID
        """
        signal = session.get(WorkflowSignal, signal_id)
        if not signal:
            raise SignalNotFoundError(f"Signal {signal_id} not found")

        signal.processed = True
        session.add(signal)
        session.commit()

    def wait_for_signal(
        self,
        session: Session,
        execution_id: uuid.UUID,
        signal_type: str,
        timeout_seconds: int | None = None,
    ) -> WorkflowSignal | None:
        """
        Wait for a specific signal type.

        This checks if a signal of the given type exists and is pending.
        In a real implementation, this would be used by the worker to check for signals.

        Args:
            session: Database session
            execution_id: Execution ID
            signal_type: Signal type to wait for
            timeout_seconds: Optional timeout (not implemented yet, would require async/queue)

        Returns:
            WorkflowSignal if found, None otherwise
        """
        signals = self.get_pending_signals(session, execution_id, signal_type)
        return signals[0] if signals else None


class SignalRouter:
    """
    Routes signals to appropriate handlers based on signal type.
    """

    def __init__(self):
        """Initialize signal router."""
        self.handlers: dict[str, callable] = {}

    def register_handler(self, signal_type: str, handler: callable) -> None:
        """
        Register a handler for a specific signal type.

        Args:
            signal_type: Signal type (e.g., "webhook", "human_input")
            handler: Handler function that processes the signal
        """
        self.handlers[signal_type] = handler

    def route_signal(
        self,
        session: Session,
        signal: WorkflowSignal,
    ) -> dict[str, Any]:
        """
        Route a signal to its handler.

        Args:
            session: Database session
            signal: Signal to route

        Returns:
            Handler result
        """
        handler = self.handlers.get(signal.signal_type)
        if not handler:
            # Default handler - just return signal data
            return {"signal_type": signal.signal_type, "data": signal.signal_data}

        return handler(session, signal)


# Default signal handler instance
default_signal_handler = SignalHandler()

# Default signal router instance
default_signal_router = SignalRouter()
