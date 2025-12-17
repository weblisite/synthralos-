"""
Archon-Powered Repair Loop

Self-healing mechanism using Archon framework for autonomous error recovery.
"""

import logging
from typing import Any

from app.agents.frameworks.archon import ArchonFramework

logger = logging.getLogger(__name__)


class ArchonRepairLoop:
    """
    Archon-powered repair loop for self-healing.
    
    Uses Archon framework to:
    - Analyze errors
    - Generate repair strategies
    - Execute repairs
    - Verify fixes
    """
    
    def __init__(self):
        """Initialize Archon repair loop."""
        self.archon = ArchonFramework()
        self.max_repair_attempts = 3
    
    def can_repair(self) -> bool:
        """Check if Archon is available for repair."""
        return self.archon.is_available
    
    def analyze_error(
        self,
        error: Exception,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Analyze an error to determine repair strategy.
        
        Args:
            error: The exception that occurred
            context: Context about the error (task, node, etc.)
            
        Returns:
            Analysis dictionary with repair strategy
        """
        error_type = type(error).__name__
        error_message = str(error)
        
        # Categorize error types
        if "selector" in error_message.lower() or "element" in error_message.lower():
            error_category = "selector_error"
        elif "timeout" in error_message.lower():
            error_category = "timeout_error"
        elif "connection" in error_message.lower() or "network" in error_message.lower():
            error_category = "network_error"
        elif "validation" in error_message.lower() or "invalid" in error_message.lower():
            error_category = "validation_error"
        else:
            error_category = "unknown_error"
        
        return {
            "error_type": error_type,
            "error_message": error_message,
            "error_category": error_category,
            "context": context,
            "repair_strategy": self._get_repair_strategy(error_category),
        }
    
    def _get_repair_strategy(self, error_category: str) -> str:
        """
        Get repair strategy for error category.
        
        Args:
            error_category: Category of error
            
        Returns:
            Repair strategy name
        """
        strategies = {
            "selector_error": "selector_auto_fix",
            "timeout_error": "retry_with_backoff",
            "network_error": "retry_with_fallback",
            "validation_error": "validate_and_correct",
            "unknown_error": "archon_autonomous_repair",
        }
        return strategies.get(error_category, "archon_autonomous_repair")
    
    def execute_repair(
        self,
        error_analysis: dict[str, Any],
        original_task: dict[str, Any],
        attempt: int = 1,
    ) -> dict[str, Any]:
        """
        Execute repair using Archon framework.
        
        Args:
            error_analysis: Error analysis from analyze_error()
            original_task: Original task that failed
            attempt: Current repair attempt number
            
        Returns:
            Repair result dictionary
        """
        if not self.can_repair():
            return {
                "success": False,
                "reason": "Archon framework not available",
            }
        
        if attempt > self.max_repair_attempts:
            return {
                "success": False,
                "reason": f"Max repair attempts ({self.max_repair_attempts}) exceeded",
            }
        
        try:
            repair_strategy = error_analysis.get("repair_strategy")
            
            # Prepare repair task for Archon
            repair_task = {
                "task": f"Repair failed task: {error_analysis['error_message']}",
                "error_analysis": error_analysis,
                "original_task": original_task,
                "attempt": attempt,
                "strategy": repair_strategy,
            }
            
            # Execute repair using Archon
            result = self.archon.execute_task(
                task_type="repair",
                input_data=repair_task,
                context=error_analysis.get("context", {}),
            )
            
            if result.get("status") == "completed":
                return {
                    "success": True,
                    "repaired_task": result.get("result", {}),
                    "attempt": attempt,
                }
            else:
                return {
                    "success": False,
                    "reason": result.get("error", "Repair failed"),
                    "attempt": attempt,
                }
                
        except Exception as e:
            logger.error(f"Repair execution failed: {e}")
            return {
                "success": False,
                "reason": str(e),
                "attempt": attempt,
            }
    
    def verify_repair(
        self,
        repaired_task: dict[str, Any],
        original_error: Exception,
    ) -> tuple[bool, str | None]:
        """
        Verify that a repair actually fixes the original error.
        
        Args:
            repaired_task: Repaired task data
            original_error: Original error that occurred
            
        Returns:
            Tuple of (is_fixed, reason)
        """
        # Basic verification - check if repaired task has required fields
        if not repaired_task:
            return False, "Repaired task is empty"
        
        # Check if error-prone fields have been modified
        error_message = str(original_error).lower()
        
        if "selector" in error_message:
            # Verify selector fields exist and are valid
            if "selector" in repaired_task and repaired_task["selector"]:
                return True, None
            return False, "Selector not properly repaired"
        
        # Default: assume repair is valid if task structure is intact
        return True, None

