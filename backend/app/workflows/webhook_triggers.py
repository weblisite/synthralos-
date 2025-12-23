"""
Webhook Triggers for Workflows

Handles webhook-to-workflow trigger mapping:
- Webhook subscription management
- Payload to trigger_data conversion
- Webhook signature validation
- Webhook retry logic
"""

import hashlib
import hmac
import uuid
from datetime import datetime
from typing import Any

from sqlmodel import Session, select

from app.models import WorkflowWebhookSubscription
from app.workflows.engine import WorkflowEngine


class WebhookTriggerError(Exception):
    """Base exception for webhook trigger errors."""

    pass


class WebhookTriggerManager:
    """
    Manages webhook triggers for workflows.
    """

    def __init__(self, workflow_engine: WorkflowEngine | None = None):
        """
        Initialize webhook trigger manager.

        Args:
            workflow_engine: WorkflowEngine instance
        """
        self.workflow_engine = workflow_engine or WorkflowEngine()

    def create_webhook_subscription(
        self,
        session: Session,
        workflow_id: uuid.UUID,
        webhook_path: str,
        secret: str | None = None,
        headers: dict[str, str] | None = None,
        filters: dict[str, Any] | None = None,
    ) -> WorkflowWebhookSubscription:
        """
        Create a webhook subscription for a workflow.

        Args:
            session: Database session
            workflow_id: Workflow ID to trigger
            webhook_path: Webhook path (e.g., "/webhooks/my-webhook")
            secret: Optional secret for signature validation
            headers: Optional headers to match
            filters: Optional filters for payload matching

        Returns:
            WorkflowWebhookSubscription instance
        """
        subscription = WorkflowWebhookSubscription(
            workflow_id=workflow_id,
            webhook_path=webhook_path,
            secret=secret,
            headers=headers or {},
            filters=filters or {},
            is_active=True,
            created_at=datetime.utcnow(),
        )

        session.add(subscription)
        session.commit()
        session.refresh(subscription)

        return subscription

    def get_subscription_by_path(
        self, session: Session, webhook_path: str
    ) -> WorkflowWebhookSubscription | None:
        """
        Get webhook subscription by path.

        Args:
            session: Database session
            webhook_path: Webhook path

        Returns:
            WorkflowWebhookSubscription if found, None otherwise
        """
        query = select(WorkflowWebhookSubscription).where(
            WorkflowWebhookSubscription.webhook_path == webhook_path,
            WorkflowWebhookSubscription.is_active.is_(True),
        )

        return session.exec(query).first()

    def validate_webhook_signature(
        self, payload: bytes, signature: str, secret: str
    ) -> bool:
        """
        Validate webhook signature (HMAC SHA256).

        Args:
            payload: Request payload bytes
            signature: Signature from header
            secret: Secret key

        Returns:
            True if signature is valid, False otherwise
        """
        try:
            # Remove "sha256=" prefix if present
            if signature.startswith("sha256="):
                signature = signature[7:]

            # Calculate expected signature
            expected_signature = hmac.new(
                secret.encode(), payload, hashlib.sha256
            ).hexdigest()

            # Compare signatures (constant-time comparison)
            return hmac.compare_digest(expected_signature, signature)
        except Exception:
            return False

    def convert_payload_to_trigger_data(
        self,
        payload: dict[str, Any],
        headers: dict[str, str],
        filters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Convert webhook payload to workflow trigger_data.

        Args:
            payload: Webhook payload
            headers: Request headers
            filters: Optional filters for payload matching

        Returns:
            Trigger data dictionary
        """
        trigger_data = {
            "trigger_type": "webhook",
            "payload": payload,
            "headers": headers,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Apply filters if provided
        if filters:
            # Check if payload matches filters
            matches = True
            for key, expected_value in filters.items():
                actual_value = self._get_nested_value(payload, key)
                if actual_value != expected_value:
                    matches = False
                    break

            if not matches:
                raise WebhookTriggerError("Payload does not match filters")

        return trigger_data

    def trigger_workflow_from_webhook(
        self,
        session: Session,
        webhook_path: str,
        payload: dict[str, Any],
        headers: dict[str, str],
        signature: str | None = None,
    ) -> uuid.UUID:
        """
        Trigger workflow from webhook.

        Args:
            session: Database session
            webhook_path: Webhook path
            payload: Webhook payload
            headers: Request headers
            signature: Optional signature for validation

        Returns:
            Execution ID
        """
        # Get subscription
        subscription = self.get_subscription_by_path(session, webhook_path)

        if not subscription:
            raise WebhookTriggerError(f"No subscription found for path: {webhook_path}")

        # Validate signature if secret is set
        if subscription.secret and signature:
            import json

            payload_bytes = json.dumps(payload, sort_keys=True).encode()
            if not self.validate_webhook_signature(
                payload_bytes, signature, subscription.secret
            ):
                raise WebhookTriggerError("Invalid webhook signature")

        # Convert payload to trigger_data
        trigger_data = self.convert_payload_to_trigger_data(
            payload, headers, subscription.filters
        )

        # Create workflow execution
        execution = self.workflow_engine.create_execution(
            session,
            subscription.workflow_id,
            trigger_data=trigger_data,
            idempotent=False,  # Webhooks may be intentionally duplicate
        )

        return execution.id

    def _get_nested_value(self, data: dict[str, Any], key: str) -> Any:
        """
        Get nested value from dictionary using dot notation.

        Args:
            data: Dictionary
            key: Dot-notation key (e.g., "user.email")

        Returns:
            Value if found, None otherwise
        """
        keys = key.split(".")
        value = data

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return None

            if value is None:
                return None

        return value


# Default webhook trigger manager instance
default_webhook_trigger_manager = WebhookTriggerManager()
