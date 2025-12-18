"""
PostHog Client

Product analytics and feature flagging integration.
"""

import logging
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)

# PostHog imports (optional - will fail gracefully if not installed)
try:
    from posthog import Posthog

    POSTHOG_AVAILABLE = True
except ImportError:
    POSTHOG_AVAILABLE = False
    logger.warning("PostHog package not installed. Analytics features will be limited.")


class PostHogClient:
    """
    PostHog client wrapper.
    
    Provides methods for:
    - Event tracking
    - Feature flag evaluation
    - User identification
    """
    
    def __init__(self):
        """Initialize PostHog client."""
        self.is_available = POSTHOG_AVAILABLE and bool(settings.POSTHOG_KEY)
        
        if not self.is_available:
            logger.warning("PostHog not configured (POSTHOG_KEY not set). Analytics will be disabled.")
            logger.info("To enable PostHog: Set POSTHOG_KEY environment variable. See docs/OBSERVABILITY_SETUP.md")
            self.client = None
            return
        
        try:
            self.client = Posthog(
                project_api_key=settings.POSTHOG_KEY,
                host="https://app.posthog.com",  # or custom host
            )
            logger.info("✅ PostHog client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize PostHog client: {e}")
            self.client = None
            self.is_available = False
    
    def capture(
        self,
        distinct_id: str,
        event: str,
        properties: dict[str, Any] | None = None,
    ) -> None:
        """
        Capture an event.
        
        Args:
            distinct_id: User ID or session ID
            event: Event name
            properties: Optional event properties
        """
        if not self.is_available or not self.client:
            return
        
        try:
            self.client.capture(
                distinct_id=distinct_id,
                event=event,
                properties=properties or {},
            )
        except Exception as e:
            logger.error(f"Failed to capture PostHog event: {e}")
    
    def identify(
        self,
        distinct_id: str,
        properties: dict[str, Any] | None = None,
    ) -> None:
        """
        Identify a user.
        
        Args:
            distinct_id: User ID
            properties: Optional user properties
        """
        if not self.is_available or not self.client:
            return
        
        try:
            self.client.identify(
                distinct_id=distinct_id,
                properties=properties or {},
            )
        except Exception as e:
            logger.error(f"Failed to identify user in PostHog: {e}")
    
    def is_feature_enabled(
        self,
        distinct_id: str,
        feature_flag: str,
    ) -> bool:
        """
        Check if a feature flag is enabled.
        
        Args:
            distinct_id: User ID
            feature_flag: Feature flag key
            
        Returns:
            True if feature is enabled, False otherwise
        """
        if not self.is_available or not self.client:
            return False
        
        try:
            return self.client.is_feature_enabled(
                feature_flag=feature_flag,
                distinct_id=distinct_id,
            )
        except Exception as e:
            logger.error(f"Failed to check feature flag in PostHog: {e}")
            return False
    
    def get_feature_flag(
        self,
        distinct_id: str,
        feature_flag: str,
    ) -> Any:
        """
        Get feature flag value.
        
        Args:
            distinct_id: User ID
            feature_flag: Feature flag key
            
        Returns:
            Feature flag value or None
        """
        if not self.is_available or not self.client:
            return None
        
        try:
            return self.client.get_feature_flag(
                feature_flag=feature_flag,
                distinct_id=distinct_id,
            )
        except Exception as e:
            logger.error(f"Failed to get feature flag from PostHog: {e}")
            return None
    
    def shutdown(self) -> None:
        """Shutdown PostHog client."""
        if self.client:
            try:
                self.client.shutdown()
            except Exception:
                pass


# Default PostHog client instance
default_posthog_client = PostHogClient()

