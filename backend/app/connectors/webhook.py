"""
Connector Webhook Service

Handles webhook ingress for connectors.
Validates signatures, maps payloads, and emits workflow signals.
"""

import hmac
import hashlib
import logging
from typing import Any

from sqlmodel import Session, select

from app.models import WebhookSubscription, ConnectorVersion
from app.connectors.registry import ConnectorNotFoundError, default_connector_registry
from app.workflows.signals import SignalHandler, default_signal_handler

logger = logging.getLogger(__name__)


class WebhookError(Exception):
    """Base exception for webhook errors."""
    pass


class InvalidWebhookSignatureError(WebhookError):
    """Invalid webhook signature."""
    pass


class WebhookNotFoundError(WebhookError):
    """Webhook subscription not found."""
    pass


class ConnectorWebhookService:
    """
    Webhook service for connector webhook ingress.
    
    Handles:
    - Webhook signature validation
    - Payload mapping
    - Workflow signal emission
    """
    
    def __init__(self):
        """Initialize webhook service."""
        self.registry = default_connector_registry
        self.signal_handler: SignalHandler = default_signal_handler
    
    def validate_webhook_signature(
        self,
        payload: bytes | str,
        signature: str,
        secret: str,
        algorithm: str = "sha256",
    ) -> bool:
        """
        Validate webhook signature.
        
        Args:
            payload: Webhook payload (raw bytes or string)
            signature: Signature from webhook header
            secret: Webhook secret
            algorithm: Hash algorithm (sha256, sha1, etc.)
            
        Returns:
            True if signature is valid, False otherwise
        """
        if isinstance(payload, str):
            payload = payload.encode("utf-8")
        
        if algorithm == "sha256":
            expected_signature = hmac.new(
                secret.encode("utf-8"),
                payload,
                hashlib.sha256,
            ).hexdigest()
        elif algorithm == "sha1":
            expected_signature = hmac.new(
                secret.encode("utf-8"),
                payload,
                hashlib.sha1,
            ).hexdigest()
        else:
            logger.warning(f"Unsupported signature algorithm: {algorithm}")
            return False
        
        # Compare signatures (constant-time comparison)
        return hmac.compare_digest(expected_signature, signature)
    
    def process_webhook(
        self,
        session: Session,
        connector_slug: str,
        trigger_id: str,
        payload: dict[str, Any],
        signature: str | None = None,
        signature_header: str | None = None,
    ) -> dict[str, Any]:
        """
        Process incoming webhook and emit workflow signals.
        
        Args:
            session: Database session
            connector_slug: Connector slug
            trigger_id: Trigger ID from connector manifest
            payload: Webhook payload
            signature: Webhook signature (if provided directly)
            signature_header: Signature header name (e.g., "X-Hub-Signature-256")
            
        Returns:
            Dictionary with processing result
            
        Raises:
            WebhookNotFoundError: If webhook subscription not found
            InvalidWebhookSignatureError: If signature validation fails
        """
        # Get connector version
        connector_version = self.registry.get_connector(session, connector_slug)
        manifest = connector_version.manifest
        
        # Get trigger configuration
        triggers = manifest.get("triggers", {})
        if trigger_id not in triggers:
            raise WebhookNotFoundError(
                f"Trigger '{trigger_id}' not found in connector '{connector_slug}'"
            )
        
        trigger_config = triggers[trigger_id]
        
        # Find webhook subscriptions for this trigger
        subscriptions = session.exec(
            select(WebhookSubscription).where(
                WebhookSubscription.connector_version_id == connector_version.id,
                WebhookSubscription.trigger_id == trigger_id,
            )
        ).all()
        
        if not subscriptions:
            raise WebhookNotFoundError(
                f"No webhook subscriptions found for trigger '{trigger_id}' in connector '{connector_slug}'"
            )
        
        # Validate signature if required
        webhook_config = trigger_config.get("webhook", {})
        requires_signature = webhook_config.get("requires_signature", True)
        
        if requires_signature and signature:
            # Validate signature for each subscription
            for subscription in subscriptions:
                if not self.validate_webhook_signature(
                    payload=str(payload),
                    signature=signature,
                    secret=subscription.endpoint_secret,
                    algorithm=webhook_config.get("signature_algorithm", "sha256"),
                ):
                    raise InvalidWebhookSignatureError(
                        f"Invalid webhook signature for subscription {subscription.id}"
                    )
        
        # Map payload to signal data
        signal_data = self._map_payload_to_signal(
            payload=payload,
            trigger_config=trigger_config,
        )
        
        # Emit signals for each subscription
        emitted_signals = []
        for subscription in subscriptions:
            try:
                # Create signal for workflow execution
                # Note: We need to find the workflow execution that's waiting for this signal
                # For now, we'll create a generic signal that can be processed by the workflow engine
                signal_type = f"connector_webhook_{connector_slug}_{trigger_id}"
                
                # Enhanced signal data with subscription context
                enhanced_signal_data = {
                    **signal_data,
                    "subscription_id": str(subscription.id),
                    "tenant_id": str(subscription.tenant_id),
                    "connector_slug": connector_slug,
                    "trigger_id": trigger_id,
                }
                
                # Emit signal (this will be picked up by workflows waiting for this signal)
                # TODO: Need to find the specific workflow execution(s) waiting for this signal
                # For now, we'll store the signal and let the workflow engine process it
                # Note: SignalHandler.emit_signal requires an execution_id, so we need to find
                # workflows waiting for this signal type. For now, we'll create a signal record
                # that can be matched later by the workflow engine.
                from app.models import WorkflowSignal
                from datetime import datetime
                
                signal = WorkflowSignal(
                    execution_id=None,  # Will be matched to execution by workflow engine
                    signal_type=signal_type,
                    signal_data=enhanced_signal_data,
                    received_at=datetime.utcnow(),
                    processed=False,
                )
                session.add(signal)
                session.commit()
                session.refresh(signal)
                
                emitted_signals.append({
                    "subscription_id": str(subscription.id),
                    "signal_id": str(signal.id),
                    "signal_type": signal_type,
                })
                
                logger.info(
                    f"Emitted webhook signal for connector '{connector_slug}' trigger '{trigger_id}' "
                    f"(subscription: {subscription.id})"
                )
            except Exception as e:
                logger.error(
                    f"Failed to emit signal for subscription {subscription.id}: {e}",
                    exc_info=True,
                )
        
        return {
            "success": True,
            "connector_slug": connector_slug,
            "trigger_id": trigger_id,
            "emitted_signals": emitted_signals,
            "subscriptions_processed": len(subscriptions),
        }
    
    def _map_payload_to_signal(
        self,
        payload: dict[str, Any],
        trigger_config: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Map webhook payload to workflow signal data.
        
        Args:
            payload: Raw webhook payload
            trigger_config: Trigger configuration from manifest
            
        Returns:
            Mapped signal data dictionary
        """
        # Get payload mapping configuration
        webhook_config = trigger_config.get("webhook", {})
        payload_mapping = webhook_config.get("payload_mapping", {})
        
        if not payload_mapping:
            # No mapping configured, return payload as-is
            return {"payload": payload}
        
        # Apply mapping
        signal_data = {}
        for signal_key, payload_path in payload_mapping.items():
            # Extract value from payload using dot notation
            value = self._extract_nested_value(payload, payload_path)
            signal_data[signal_key] = value
        
        return signal_data
    
    def _extract_nested_value(
        self,
        data: dict[str, Any],
        path: str,
    ) -> Any:
        """
        Extract nested value from dictionary using dot notation.
        
        Args:
            data: Dictionary to extract from
            path: Dot-notation path (e.g., "user.email" or "data.items[0].id")
            
        Returns:
            Extracted value or None if not found
        """
        parts = path.split(".")
        current = data
        
        for part in parts:
            if "[" in part and "]" in part:
                # Handle array access (e.g., "items[0]")
                key = part[: part.index("[")]
                index = int(part[part.index("[") + 1 : part.index("]")])
                if key:
                    current = current.get(key, [])
                if isinstance(current, list) and 0 <= index < len(current):
                    current = current[index]
                else:
                    return None
            else:
                if isinstance(current, dict):
                    current = current.get(part)
                else:
                    return None
            
            if current is None:
                return None
        
        return current


# Default webhook service instance
default_webhook_service = ConnectorWebhookService()

