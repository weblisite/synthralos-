"""
Wazuh Security Monitoring Client

Security event logging and audit trail integration.
"""

import logging
from datetime import datetime
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)

# Wazuh imports (optional - will fail gracefully if not installed)
try:
    import httpx

    WAZUH_AVAILABLE = True
except ImportError:
    WAZUH_AVAILABLE = False
    logger.warning("httpx not installed. Wazuh integration will be limited.")


class WazuhClient:
    """
    Wazuh client wrapper.
    
    Provides methods for:
    - Security event logging
    - Audit trail
    - Alerting
    """
    
    def __init__(self):
        """Initialize Wazuh client."""
        self.is_available = WAZUH_AVAILABLE and bool(settings.WAZUH_URL)
        
        if not self.is_available:
            logger.warning("Wazuh not configured. Security monitoring will be disabled.")
            self.wazuh_url = None
            self.wazuh_auth = None
            return
        
        self.wazuh_url = settings.WAZUH_URL.rstrip("/")
        self.wazuh_auth = (
            (settings.WAZUH_USER, settings.WAZUH_PASSWORD)
            if settings.WAZUH_USER and settings.WAZUH_PASSWORD
            else None
        )
        
        logger.info(f"✅ Wazuh client initialized (URL: {self.wazuh_url})")
    
    def log_security_event(
        self,
        event_type: str,
        severity: str,
        message: str,
        user_id: str | None = None,
        ip_address: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Log a security event to Wazuh.
        
        Args:
            event_type: Type of security event (e.g., "authentication_failure", "unauthorized_access")
            severity: Severity level (low, medium, high, critical)
            message: Event message
            user_id: Optional user ID
            ip_address: Optional IP address
            metadata: Optional additional metadata
        """
        if not self.is_available:
            return
        
        try:
            event_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": event_type,
                "severity": severity,
                "message": message,
                "service": "synthralos-backend",
            }
            
            if user_id:
                event_data["user_id"] = user_id
            
            if ip_address:
                event_data["ip_address"] = ip_address
            
            if metadata:
                event_data["metadata"] = metadata
            
            # Send to Wazuh API
            self._send_event(event_data)
            
        except Exception as e:
            logger.error(f"Failed to log security event to Wazuh: {e}")
    
    def log_audit_event(
        self,
        action: str,
        resource: str,
        user_id: str,
        success: bool,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Log an audit event to Wazuh.
        
        Args:
            action: Action performed (e.g., "create", "update", "delete")
            resource: Resource type (e.g., "workflow", "connector")
            user_id: User ID performing the action
            success: Whether the action succeeded
            metadata: Optional additional metadata
        """
        if not self.is_available:
            return
        
        try:
            event_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": "audit",
                "action": action,
                "resource": resource,
                "user_id": user_id,
                "success": success,
                "service": "synthralos-backend",
            }
            
            if metadata:
                event_data["metadata"] = metadata
            
            # Send to Wazuh API
            self._send_event(event_data)
            
        except Exception as e:
            logger.error(f"Failed to log audit event to Wazuh: {e}")
    
    def _send_event(self, event_data: dict[str, Any]) -> None:
        """
        Send event to Wazuh API.
        
        Args:
            event_data: Event data dictionary
        """
        if not self.is_available or not self.wazuh_url:
            return
        
        try:
            import httpx
            
            # Wazuh API endpoint for events
            endpoint = f"{self.wazuh_url}/api/v1/events"
            
            response = httpx.post(
                endpoint,
                json=event_data,
                auth=self.wazuh_auth,
                timeout=5.0,
            )
            
            if response.status_code not in (200, 201):
                logger.warning(
                    f"Wazuh API returned status {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            logger.error(f"Failed to send event to Wazuh: {e}")
    
    def create_alert(
        self,
        alert_type: str,
        severity: str,
        message: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Create a security alert in Wazuh.
        
        Args:
            alert_type: Type of alert
            severity: Severity level
            message: Alert message
            metadata: Optional metadata
        """
        self.log_security_event(
            event_type=f"alert_{alert_type}",
            severity=severity,
            message=message,
            metadata=metadata,
        )


# Default Wazuh client instance
default_wazuh_client = WazuhClient()

