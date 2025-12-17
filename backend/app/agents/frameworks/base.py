"""
Base Agent Framework Interface

Defines the interface that all agent framework wrappers must implement.
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseAgentFramework(ABC):
    """
    Base class for agent framework wrappers.
    
    All framework implementations must inherit from this class
    and implement the required methods.
    """
    
    def __init__(self, config: dict[str, Any] | None = None):
        """
        Initialize the framework.
        
        Args:
            config: Framework-specific configuration dictionary
        """
        self.config = config or {}
        self.is_available = False
        self._check_availability()
    
    @abstractmethod
    def _check_availability(self) -> None:
        """
        Check if the framework is available (installed and configured).
        Sets self.is_available to True if ready to use.
        """
        pass
    
    @abstractmethod
    def execute_task(
        self,
        task_type: str,
        input_data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute an agent task.
        
        Args:
            task_type: Type of task to execute
            input_data: Task input data
            context: Optional cached context from previous executions
            
        Returns:
            Execution result dictionary with:
            - status: "completed" or "failed"
            - result: Task output data
            - context: Updated context (for caching)
            - logs: List of log messages
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> dict[str, Any]:
        """
        Get framework capabilities.
        
        Returns:
            Dictionary describing framework capabilities:
            - supports_recursive_planning: bool
            - supports_multi_role: bool
            - supports_self_healing: bool
            - supports_tool_calling: bool
            - max_roles: int | None
            - etc.
        """
        pass
    
    def validate_input(self, input_data: dict[str, Any]) -> tuple[bool, str | None]:
        """
        Validate task input data.
        
        Args:
            input_data: Input data to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Default implementation - override if needed
        return True, None

