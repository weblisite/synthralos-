"""
Kyro Framework Integration

Kyro is a framework for building AI agents with focus on efficiency and performance.
"""

import logging
from typing import Any

from app.agents.frameworks.base import BaseAgentFramework

logger = logging.getLogger(__name__)


class KyroFramework(BaseAgentFramework):
    """
    Kyro framework wrapper.

    Kyro specializes in:
    - High-performance agent execution
    - Efficient resource utilization
    - Fast task completion
    - Optimized workflows
    """

    def __init__(self):
        """Initialize Kyro framework."""
        super().__init__()

    def _check_availability(self) -> None:
        """Check if Kyro is available."""
        try:
            from app.core.config import settings

            if settings.OPENAI_API_KEY:
                import openai

                self.is_available = True
                logger.info(
                    "Kyro framework is available (using OpenAI with optimization)"
                )
            else:
                self.is_available = False
                logger.warning("Kyro requires OPENAI_API_KEY to be configured")
        except ImportError:
            self.is_available = False
            logger.warning(
                "OpenAI library not installed. Install with: pip install openai"
            )

    def execute_task(
        self,
        task_type: str,
        input_data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute a task using Kyro (high-performance optimized agent).

        Args:
            task_type: Type of task
            input_data: Task input data
            context: Optional context data

        Returns:
            Task execution result
        """
        if not self.is_available:
            return {
                "status": "failed",
                "result": None,
                "context": context or {},
                "logs": [
                    "Kyro framework not available. Please configure OPENAI_API_KEY."
                ],
                "error": "Framework not available",
            }

        try:
            import openai

            from app.core.config import settings

            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

            task = (
                input_data.get("task")
                or input_data.get("prompt")
                or f"Execute {task_type}"
            )
            optimization_level = input_data.get("optimization_level", "standard")

            # Optimize prompt based on optimization level
            if optimization_level == "high":
                system_prompt = "You are a high-performance AI agent. Execute tasks efficiently with minimal token usage. Be concise and direct."
                temperature = 0.3
                max_tokens = 500
            elif optimization_level == "balanced":
                system_prompt = "You are an efficient AI agent. Execute tasks effectively while maintaining quality."
                temperature = 0.5
                max_tokens = 750
            else:  # standard
                system_prompt = "You are a helpful AI agent. Execute tasks accurately and efficiently."
                temperature = 0.7
                max_tokens = 1000

            # Add context for optimization
            if context:
                context_summary = "\n".join(
                    [f"{k}: {str(v)[:100]}" for k, v in list(context.items())[:5]]
                )
                task = f"Context:\n{context_summary}\n\nTask: {task}"

            response = client.chat.completions.create(
                model=input_data.get("model", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": task},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )

            result = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else None

            updated_context = context or {}
            updated_context["last_task"] = task_type
            updated_context["optimization_level"] = optimization_level

            return {
                "status": "completed",
                "result": {
                    "output": result,
                    "optimization_level": optimization_level,
                    "tokens_used": tokens_used,
                    "efficiency_score": (1000 - tokens_used) / 10
                    if tokens_used
                    else None,  # Higher is better
                },
                "context": updated_context,
                "logs": [
                    f"Kyro execution started with {optimization_level} optimization",
                    f"Tokens used: {tokens_used}",
                    "Task completed successfully",
                ],
            }

        except Exception as e:
            logger.error(f"Kyro task execution failed: {e}", exc_info=True)
            return {
                "status": "failed",
                "result": None,
                "context": context or {},
                "logs": [f"Kyro execution error: {str(e)}"],
                "error": str(e),
            }

    def get_capabilities(self) -> dict[str, Any]:
        """Get Kyro capabilities."""
        return {
            "supports_recursive_planning": False,
            "supports_multi_role": False,
            "supports_self_healing": False,
            "supports_tool_calling": True,
            "max_roles": 1,
            "framework_name": "kyro",
            "description": "High-performance agent framework for efficient execution",
        }
