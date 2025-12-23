"""
Idempotency and Exactly-Once Guarantees

Provides idempotent execution keys and duplicate execution detection:
- Idempotent execution keys
- Duplicate execution detection
- Deduplication logic
- Idempotent node execution
"""

import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Any

from sqlmodel import Session, select

from app.models import WorkflowExecution


class IdempotencyError(Exception):
    """Base exception for idempotency errors."""

    pass


class IdempotencyManager:
    """
    Manages idempotency and exactly-once guarantees for workflow executions.
    """

    def __init__(self, deduplication_window_hours: int = 24):
        """
        Initialize idempotency manager.

        Args:
            deduplication_window_hours: Hours to keep idempotency keys (default: 24)
        """
        self.deduplication_window_hours = deduplication_window_hours
        self._idempotency_cache: dict[
            str, uuid.UUID
        ] = {}  # idempotency_key -> execution_id

    def generate_idempotency_key(
        self,
        workflow_id: uuid.UUID,
        trigger_data: dict[str, Any],
        user_id: uuid.UUID | None = None,
    ) -> str:
        """
        Generate idempotency key for execution.

        Args:
            workflow_id: Workflow ID
            trigger_data: Trigger data
            user_id: Optional user ID

        Returns:
            Idempotency key (SHA256 hash)
        """
        # Create deterministic key from workflow_id, trigger_data, and user_id
        key_data = {
            "workflow_id": str(workflow_id),
            "trigger_data": self._normalize_dict(trigger_data),
            "user_id": str(user_id) if user_id else None,
        }

        # Convert to JSON-like string for hashing
        key_string = self._dict_to_string(key_data)

        # Generate SHA256 hash
        return hashlib.sha256(key_string.encode()).hexdigest()

    def check_duplicate_execution(
        self,
        session: Session,
        idempotency_key: str,
    ) -> uuid.UUID | None:
        """
        Check if execution with this idempotency key already exists.

        Args:
            session: Database session
            idempotency_key: Idempotency key

        Returns:
            Existing execution ID if found, None otherwise
        """
        # Check cache first
        if idempotency_key in self._idempotency_cache:
            cached_execution_id = self._idempotency_cache[idempotency_key]
            # Verify execution still exists
            execution = session.get(WorkflowExecution, cached_execution_id)
            if execution:
                return cached_execution_id
            else:
                # Remove from cache if execution doesn't exist
                del self._idempotency_cache[idempotency_key]

        # Check database for recent executions with same idempotency key
        # Store idempotency_key in trigger_data for now (could be separate column)
        cutoff_time = datetime.utcnow() - timedelta(
            hours=self.deduplication_window_hours
        )

        query = (
            select(WorkflowExecution)
            .where(WorkflowExecution.started_at >= cutoff_time)
            .where(
                WorkflowExecution.trigger_data.op("->>")("idempotency_key")
                == idempotency_key
            )
        )

        existing_execution = session.exec(query).first()

        if existing_execution:
            # Cache the result
            self._idempotency_cache[idempotency_key] = existing_execution.id
            return existing_execution.id

        return None

    def register_execution(
        self,
        session: Session,
        execution_id: uuid.UUID,
        idempotency_key: str,
    ) -> None:
        """
        Register execution with idempotency key.

        Args:
            session: Database session
            execution_id: Execution ID
            idempotency_key: Idempotency key
        """
        # Store in cache
        self._idempotency_cache[idempotency_key] = execution_id

        # Store in execution trigger_data (could be separate column)
        execution = session.get(WorkflowExecution, execution_id)
        if execution:
            trigger_data = execution.trigger_data or {}
            trigger_data["idempotency_key"] = idempotency_key
            execution.trigger_data = trigger_data
            session.add(execution)
            session.commit()

    def ensure_idempotent_execution(
        self,
        session: Session,
        workflow_id: uuid.UUID,
        trigger_data: dict[str, Any],
        user_id: uuid.UUID | None = None,
    ) -> tuple[uuid.UUID, bool]:
        """
        Ensure execution is idempotent, returning existing execution if duplicate.

        Args:
            session: Database session
            workflow_id: Workflow ID
            trigger_data: Trigger data
            user_id: Optional user ID

        Returns:
            Tuple of (execution_id, is_duplicate)
        """
        # Generate idempotency key
        idempotency_key = self.generate_idempotency_key(
            workflow_id, trigger_data, user_id
        )

        # Check for duplicate
        existing_execution_id = self.check_duplicate_execution(session, idempotency_key)

        if existing_execution_id:
            return (existing_execution_id, True)

        # Create new execution (caller should register it)
        return (uuid.uuid4(), False)

    def _normalize_dict(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Normalize dictionary for consistent hashing.

        Args:
            data: Dictionary to normalize

        Returns:
            Normalized dictionary
        """
        normalized = {}
        for key, value in sorted(data.items()):
            if isinstance(value, dict):
                normalized[key] = self._normalize_dict(value)
            elif isinstance(value, list):
                normalized[key] = [
                    self._normalize_dict(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                normalized[key] = value
        return normalized

    def _dict_to_string(self, data: dict[str, Any]) -> str:
        """
        Convert dictionary to deterministic string.

        Args:
            data: Dictionary to convert

        Returns:
            String representation
        """
        import json

        return json.dumps(data, sort_keys=True, separators=(",", ":"))


# Default idempotency manager instance
default_idempotency_manager = IdempotencyManager()
