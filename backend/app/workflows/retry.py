"""
Workflow Retry Logic

Implements configurable retry policies with exponential backoff.
"""

from datetime import datetime, timedelta
from typing import Any

from app.core.config import settings


class RetryPolicy:
    """
    Retry policy configuration.
    
    Defines how retries should be handled for workflow executions.
    """
    
    def __init__(
        self,
        max_retries: int | None = None,
        initial_delay_seconds: float = 1.0,
        backoff_multiplier: float | None = None,
        max_delay_seconds: float = 3600.0,  # 1 hour max
    ):
        """
        Initialize retry policy.
        
        Args:
            max_retries: Maximum number of retries (defaults to WORKFLOW_MAX_RETRIES)
            initial_delay_seconds: Initial delay before first retry
            backoff_multiplier: Multiplier for exponential backoff (defaults to WORKFLOW_RETRY_BACKOFF_MULTIPLIER)
            max_delay_seconds: Maximum delay between retries
        """
        self.max_retries = max_retries or settings.WORKFLOW_MAX_RETRIES
        self.initial_delay_seconds = initial_delay_seconds
        self.backoff_multiplier = backoff_multiplier or settings.WORKFLOW_RETRY_BACKOFF_MULTIPLIER
        self.max_delay_seconds = max_delay_seconds
    
    def calculate_next_retry_at(
        self,
        retry_count: int,
        base_time: datetime | None = None,
    ) -> datetime:
        """
        Calculate when the next retry should occur.
        
        Uses exponential backoff: delay = initial_delay * (backoff_multiplier ^ retry_count)
        
        Args:
            retry_count: Current retry count (0-indexed)
            base_time: Base time to calculate from (defaults to now)
            
        Returns:
            Datetime when next retry should occur
        """
        if base_time is None:
            base_time = datetime.utcnow()
        
        # Calculate delay using exponential backoff
        delay_seconds = self.initial_delay_seconds * (self.backoff_multiplier ** retry_count)
        
        # Cap at max delay
        delay_seconds = min(delay_seconds, self.max_delay_seconds)
        
        return base_time + timedelta(seconds=delay_seconds)
    
    def should_retry(self, retry_count: int) -> bool:
        """
        Check if execution should be retried.
        
        Args:
            retry_count: Current retry count
            
        Returns:
            True if should retry, False otherwise
        """
        return retry_count < self.max_retries
    
    def get_retry_delay_seconds(self, retry_count: int) -> float:
        """
        Get delay in seconds for a specific retry count.
        
        Args:
            retry_count: Current retry count
            
        Returns:
            Delay in seconds
        """
        delay_seconds = self.initial_delay_seconds * (self.backoff_multiplier ** retry_count)
        return min(delay_seconds, self.max_delay_seconds)


class RetryManager:
    """
    Manages retry logic for workflow executions.
    """
    
    def __init__(self, policy: RetryPolicy | None = None):
        """
        Initialize retry manager.
        
        Args:
            policy: Retry policy to use (defaults to default policy)
        """
        self.policy = policy or RetryPolicy()
    
    def should_retry_execution(
        self,
        retry_count: int,
        error_type: str | None = None,
    ) -> bool:
        """
        Determine if an execution should be retried.
        
        Args:
            retry_count: Current retry count
            error_type: Type of error (for future use in error-specific policies)
            
        Returns:
            True if should retry, False otherwise
        """
        return self.policy.should_retry(retry_count)
    
    def schedule_retry(
        self,
        retry_count: int,
        base_time: datetime | None = None,
    ) -> datetime:
        """
        Schedule the next retry attempt.
        
        Args:
            retry_count: Current retry count
            base_time: Base time to calculate from
            
        Returns:
            Datetime when next retry should occur
        """
        return self.policy.calculate_next_retry_at(retry_count, base_time)
    
    def get_retry_info(self, retry_count: int) -> dict[str, Any]:
        """
        Get retry information for logging/monitoring.
        
        Args:
            retry_count: Current retry count
            
        Returns:
            Dictionary with retry information
        """
        return {
            "retry_count": retry_count,
            "max_retries": self.policy.max_retries,
            "next_retry_delay_seconds": self.policy.get_retry_delay_seconds(retry_count),
            "can_retry": self.policy.should_retry(retry_count),
        }


# Default retry manager instance
default_retry_manager = RetryManager()

