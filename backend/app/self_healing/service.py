"""
Self-Healing Service

Main service for self-healing capabilities across workflows, agents, and automation.
"""

import logging
from typing import Any

from app.self_healing.archon_repair import ArchonRepairLoop
from app.self_healing.selector_fix import SelectorAutoFix

logger = logging.getLogger(__name__)


class SelfHealingService:
    """
    Self-healing service for autonomous error recovery.
    
    Provides:
    - Archon-powered repair loops
    - Selector auto-fix
    - Intelligent retry chains
    - Error analysis and categorization
    """
    
    def __init__(self):
        """Initialize self-healing service."""
        self.archon_repair = ArchonRepairLoop()
        self.selector_fix = SelectorAutoFix()
        self.max_retry_attempts = 3
    
    def heal_task(
        self,
        error: Exception,
        task: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Attempt to heal a failed task.
        
        Args:
            error: The exception that occurred
            task: The task that failed
            context: Optional context about the task
            
        Returns:
            Healing result dictionary
        """
        # Analyze the error
        error_analysis = self.archon_repair.analyze_error(error, context or {})
        
        repair_strategy = error_analysis.get("repair_strategy")
        
        # Route to appropriate repair mechanism
        if repair_strategy == "selector_auto_fix":
            return self._heal_selector_error(error, task, error_analysis)
        elif repair_strategy == "retry_with_backoff":
            return self._heal_timeout_error(error, task, error_analysis)
        elif repair_strategy == "retry_with_fallback":
            return self._heal_network_error(error, task, error_analysis)
        elif repair_strategy == "validate_and_correct":
            return self._heal_validation_error(error, task, error_analysis)
        elif repair_strategy == "archon_autonomous_repair":
            return self._heal_with_archon(error, task, error_analysis)
        else:
            return {
                "success": False,
                "reason": f"Unknown repair strategy: {repair_strategy}",
            }
    
    def _heal_selector_error(
        self,
        error: Exception,
        task: dict[str, Any],
        error_analysis: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Heal a selector-related error.
        
        Args:
            error: The error
            task: The task
            error_analysis: Error analysis
            
        Returns:
            Healing result
        """
        # Extract selector from task
        selector = task.get("selector") or task.get("xpath") or task.get("css_selector")
        selector_type = "xpath" if "xpath" in task else "css"
        
        if not selector:
            return {
                "success": False,
                "reason": "No selector found in task",
            }
        
        # Fix the selector
        fix_result = self.selector_fix.fix_selector(
            selector=selector,
            selector_type=selector_type,
            context=task,
        )
        
        if fix_result.get("success"):
            # Update task with fixed selector
            healed_task = task.copy()
            if selector_type == "xpath":
                healed_task["xpath"] = fix_result["fixed_selector"]
            else:
                healed_task["selector"] = fix_result["fixed_selector"]
            
            return {
                "success": True,
                "healed_task": healed_task,
                "fix_type": "selector_auto_fix",
                "alternatives": fix_result.get("alternatives", []),
            }
        
        return {
            "success": False,
            "reason": fix_result.get("reason", "Selector fix failed"),
        }
    
    def _heal_timeout_error(
        self,
        error: Exception,
        task: dict[str, Any],
        error_analysis: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Heal a timeout error with retry and backoff.
        
        Args:
            error: The error
            task: The task
            error_analysis: Error analysis
            
        Returns:
            Healing result
        """
        # Increase timeout and add retry logic
        healed_task = task.copy()
        
        # Increase timeout by 2x
        current_timeout = task.get("timeout", 30)
        healed_task["timeout"] = current_timeout * 2
        
        # Add retry configuration
        healed_task["retry_config"] = {
            "max_retries": 2,
            "backoff_multiplier": 2.0,
            "initial_delay": 1.0,
        }
        
        return {
            "success": True,
            "healed_task": healed_task,
            "fix_type": "retry_with_backoff",
        }
    
    def _heal_network_error(
        self,
        error: Exception,
        task: dict[str, Any],
        error_analysis: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Heal a network error with fallback strategies.
        
        Args:
            error: The error
            task: The task
            error_analysis: Error analysis
            
        Returns:
            Healing result
        """
        healed_task = task.copy()
        
        # Add fallback URL or endpoint
        if "url" in task:
            # Try alternative URL patterns
            original_url = task["url"]
            # Could implement URL fallback logic here
            healed_task["fallback_urls"] = [original_url]
        
        # Add retry configuration
        healed_task["retry_config"] = {
            "max_retries": 3,
            "backoff_multiplier": 1.5,
            "initial_delay": 2.0,
        }
        
        return {
            "success": True,
            "healed_task": healed_task,
            "fix_type": "retry_with_fallback",
        }
    
    def _heal_validation_error(
        self,
        error: Exception,
        task: dict[str, Any],
        error_analysis: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Heal a validation error by correcting input data.
        
        Args:
            error: The error
            task: The task
            error_analysis: Error analysis
            
        Returns:
            Healing result
        """
        # Use guardrails to validate and correct
        from app.guardrails.service import default_guardrails_service
        
        guardrails = default_guardrails_service
        
        # Sanitize and validate task data
        sanitized_data = guardrails.sanitize_input(task)
        
        # Try to fix validation issues
        healed_task = sanitized_data.copy()
        
        # Add validation bypass for non-critical fields (if needed)
        healed_task["validation_mode"] = "lenient"
        
        return {
            "success": True,
            "healed_task": healed_task,
            "fix_type": "validate_and_correct",
        }
    
    def _heal_with_archon(
        self,
        error: Exception,
        task: dict[str, Any],
        error_analysis: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Heal using Archon autonomous repair.
        
        Args:
            error: The error
            task: The task
            error_analysis: Error analysis
            
        Returns:
            Healing result
        """
        if not self.archon_repair.can_repair():
            return {
                "success": False,
                "reason": "Archon framework not available",
            }
        
        # Execute Archon repair loop
        repair_result = self.archon_repair.execute_repair(
            error_analysis=error_analysis,
            original_task=task,
            attempt=1,
        )
        
        if repair_result.get("success"):
            healed_task = repair_result.get("repaired_task", task)
            
            # Verify the repair
            is_fixed, reason = self.archon_repair.verify_repair(healed_task, error)
            
            if is_fixed:
                return {
                    "success": True,
                    "healed_task": healed_task,
                    "fix_type": "archon_autonomous_repair",
                }
            else:
                return {
                    "success": False,
                    "reason": f"Repair verification failed: {reason}",
                }
        
        return {
            "success": False,
            "reason": repair_result.get("reason", "Archon repair failed"),
        }
    
    def create_retry_chain(
        self,
        task: dict[str, Any],
        error: Exception,
        max_attempts: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Create an intelligent retry chain for a failed task.
        
        Args:
            task: The task to retry
            error: The error that occurred
            max_attempts: Maximum retry attempts (defaults to self.max_retry_attempts)
            
        Returns:
            List of retry task configurations
        """
        if max_attempts is None:
            max_attempts = self.max_retry_attempts
        
        retry_chain = []
        
        # Analyze error to determine retry strategy
        error_analysis = self.archon_repair.analyze_error(error, {})
        repair_strategy = error_analysis.get("repair_strategy")
        
        for attempt in range(1, max_attempts + 1):
            retry_task = task.copy()
            
            # Apply strategy-specific modifications
            if repair_strategy == "retry_with_backoff":
                # Exponential backoff
                delay = 2 ** (attempt - 1)
                retry_task["delay_seconds"] = delay
                retry_task["timeout"] = task.get("timeout", 30) * (attempt + 1)
            
            elif repair_strategy == "retry_with_fallback":
                # Try alternative approaches
                retry_task["fallback_enabled"] = True
                retry_task["attempt"] = attempt
            
            elif repair_strategy == "selector_auto_fix":
                # Try fixed selector
                selector = task.get("selector") or task.get("xpath")
                if selector:
                    fix_result = self.selector_fix.fix_selector(selector)
                    if fix_result.get("success"):
                        if attempt == 1:
                            retry_task["selector"] = fix_result["fixed_selector"]
                        elif attempt == 2 and fix_result.get("alternatives"):
                            retry_task["selector"] = fix_result["alternatives"][0]
            
            retry_task["retry_attempt"] = attempt
            retry_task["max_attempts"] = max_attempts
            
            retry_chain.append(retry_task)
        
        return retry_chain


# Default instance
default_self_healing_service = SelfHealingService()

