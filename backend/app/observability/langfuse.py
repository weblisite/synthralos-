"""
Langfuse Client

LLM observability and tracing integration.
"""

import logging
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)

# Langfuse imports (optional - will fail gracefully if not installed)
try:
    from langfuse import Langfuse

    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    logger.warning("Langfuse package not installed. LLM observability features will be limited.")


class LangfuseClient:
    """
    Langfuse client wrapper.
    
    Provides methods for:
    - LLM call tracing
    - Agent thought logging
    - Customer-visible traces
    """
    
    def __init__(self):
        """Initialize Langfuse client."""
        self.is_available = LANGFUSE_AVAILABLE and bool(settings.LANGFUSE_KEY)
        
        if not self.is_available:
            logger.warning("Langfuse not configured. LLM observability will be disabled.")
            self.client = None
            return
        
        try:
            # Langfuse requires both public_key and secret_key
            # For cloud.langfuse.com, use the same key for both
            # For self-hosted, use separate keys if available
            langfuse_secret_key = getattr(settings, "LANGFUSE_SECRET_KEY", None) or settings.LANGFUSE_KEY
            
            langfuse_host = getattr(settings, "LANGFUSE_HOST", "https://cloud.langfuse.com")
            
            self.client = Langfuse(
                public_key=settings.LANGFUSE_KEY,
                secret_key=langfuse_secret_key,
                host=langfuse_host,
            )
            logger.info("✅ Langfuse client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Langfuse client: {e}")
            self.client = None
            self.is_available = False
    
    def trace(
        self,
        name: str,
        user_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Any:
        """
        Create a new trace.
        
        Args:
            name: Trace name
            user_id: Optional user ID
            metadata: Optional trace metadata
            
        Returns:
            Trace object or None if not available
        """
        if not self.is_available or not self.client:
            return None
        
        try:
            return self.client.trace(
                name=name,
                user_id=user_id,
                metadata=metadata or {},
            )
        except Exception as e:
            logger.error(f"Failed to create Langfuse trace: {e}")
            return None
    
    def span(
        self,
        trace_id: str,
        name: str,
        metadata: dict[str, Any] | None = None,
    ) -> Any:
        """
        Create a span within a trace.
        
        Args:
            trace_id: Parent trace ID
            name: Span name
            metadata: Optional span metadata
            
        Returns:
            Span object or None if not available
        """
        if not self.is_available or not self.client:
            return None
        
        try:
            return self.client.span(
                trace_id=trace_id,
                name=name,
                metadata=metadata or {},
            )
        except Exception as e:
            logger.error(f"Failed to create Langfuse span: {e}")
            return None
    
    def generation(
        self,
        trace_id: str,
        name: str,
        model: str,
        input_data: Any,
        output_data: Any,
        metadata: dict[str, Any] | None = None,
    ) -> Any:
        """
        Log an LLM generation.
        
        Args:
            trace_id: Parent trace ID
            name: Generation name
            model: Model name
            input_data: Input data
            output_data: Output data
            metadata: Optional metadata
            
        Returns:
            Generation object or None if not available
        """
        if not self.is_available or not self.client:
            return None
        
        try:
            return self.client.generation(
                trace_id=trace_id,
                name=name,
                model=model,
                input=input_data,
                output=output_data,
                metadata=metadata or {},
            )
        except Exception as e:
            logger.error(f"Failed to log Langfuse generation: {e}")
            return None
    
    def score(
        self,
        trace_id: str,
        name: str,
        value: float,
        comment: str | None = None,
    ) -> Any:
        """
        Add a score to a trace.
        
        Args:
            trace_id: Trace ID
            name: Score name
            value: Score value
            comment: Optional comment
            
        Returns:
            Score object or None if not available
        """
        if not self.is_available or not self.client:
            return None
        
        try:
            return self.client.score(
                trace_id=trace_id,
                name=name,
                value=value,
                comment=comment,
            )
        except Exception as e:
            logger.error(f"Failed to add Langfuse score: {e}")
            return None
    
    def flush(self) -> None:
        """Flush pending events."""
        if self.client:
            try:
                self.client.flush()
            except Exception:
                pass


# Default Langfuse client instance
default_langfuse_client = LangfuseClient()

