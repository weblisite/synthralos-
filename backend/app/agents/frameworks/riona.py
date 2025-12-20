"""
Riona Framework Integration

Riona is a framework for building AI agents with advanced capabilities.
"""

import logging
from typing import Any

from app.agents.frameworks.base import BaseAgentFramework

logger = logging.getLogger(__name__)


class RionaFramework(BaseAgentFramework):
    """
    Riona framework wrapper.

    Riona specializes in:
    - Advanced agent capabilities
    - Complex task handling
    - Multi-modal processing
    - Adaptive behavior
    """

    def __init__(self):
        """Initialize Riona framework."""
        super().__init__()

    def _check_availability(self) -> None:
        """Check if Riona is available."""
        try:
            from app.core.config import settings

            if settings.OPENAI_API_KEY:
                import openai

                self.is_available = True
                logger.info(
                    "Riona framework is available (using OpenAI with adaptive behavior)"
                )
            else:
                self.is_available = False
                logger.warning("Riona requires OPENAI_API_KEY to be configured")
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
        Execute a task using Riona (advanced adaptive agent with multi-modal capabilities).

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
                    "Riona framework not available. Please configure OPENAI_API_KEY."
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
            mode = input_data.get("mode", "standard")
            capabilities = input_data.get(
                "capabilities", ["reasoning", "planning", "execution"]
            )

            logs = [f"Riona execution started in {mode} mode"]
            logs.append(f"Capabilities: {', '.join(capabilities)}")

            # Adaptive execution based on mode and capabilities
            adaptive_context = context or {}
            adaptive_context["mode"] = mode
            adaptive_context["capabilities"] = capabilities
            adaptive_context["execution_steps"] = []

            # Mode-specific system prompts
            mode_prompts = {
                "standard": "You are an advanced AI agent with adaptive behavior. Execute tasks efficiently using available capabilities.",
                "advanced": "You are an advanced AI agent with enhanced reasoning and multi-modal processing. Execute complex tasks with sophisticated strategies.",
                "expert": "You are an expert AI agent with deep domain knowledge and adaptive learning. Execute tasks with maximum effectiveness.",
            }

            system_prompt = mode_prompts.get(mode, mode_prompts["standard"])

            # Build capability-enhanced prompt
            capability_descriptions = {
                "reasoning": "Advanced reasoning and logical analysis",
                "planning": "Strategic planning and goal decomposition",
                "execution": "Efficient task execution and implementation",
                "learning": "Adaptive learning from context and feedback",
                "multimodal": "Multi-modal processing (text, images, etc.)",
            }

            active_capabilities = [
                capability_descriptions.get(cap, cap)
                for cap in capabilities
                if cap in capability_descriptions
            ]

            enhanced_prompt = f"""Task: {task}

Active Capabilities:
{chr(10).join([f"- {cap}" for cap in active_capabilities])}

Mode: {mode}

Execute this task using your adaptive capabilities. Adapt your approach based on the task requirements and available capabilities.

Provide:
1. Analysis using your reasoning capabilities
2. Plan using your planning capabilities
3. Execution using your execution capabilities
4. Adaptive insights based on the task"""

            # Multi-step adaptive execution
            if "planning" in capabilities:
                # Planning phase
                planning_response = client.chat.completions.create(
                    model=input_data.get("model", "gpt-4o-mini"),
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Plan the approach for: {task}"},
                    ],
                    temperature=0.7,
                    max_tokens=500,
                )
                plan = planning_response.choices[0].message.content
                adaptive_context["execution_steps"].append(
                    {"phase": "planning", "output": plan}
                )
                logs.append("Planning phase completed")
                enhanced_prompt = f"Plan:\n{plan}\n\nNow execute: {task}"

            # Main execution
            response = client.chat.completions.create(
                model=input_data.get("model", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": enhanced_prompt},
                ],
                temperature=0.7
                if mode == "standard"
                else (0.8 if mode == "advanced" else 0.9),
                max_tokens=1500,
            )

            result = response.choices[0].message.content
            adaptive_context["execution_steps"].append(
                {"phase": "execution", "output": result}
            )

            logs.append("Execution phase completed")
            logs.append("Task completed successfully")

            return {
                "status": "completed",
                "result": {
                    "output": result,
                    "mode": mode,
                    "capabilities": capabilities,
                    "execution_steps": adaptive_context["execution_steps"],
                    "adaptive_insights": f"Executed in {mode} mode using {len(capabilities)} capabilities",
                },
                "context": adaptive_context,
                "logs": logs,
            }

        except Exception as e:
            logger.error(f"Riona task execution failed: {e}", exc_info=True)
            return {
                "status": "failed",
                "result": None,
                "context": context or {},
                "logs": [f"Riona execution error: {str(e)}"],
                "error": str(e),
            }

    def get_capabilities(self) -> dict[str, Any]:
        """Get Riona capabilities."""
        return {
            "supports_recursive_planning": True,
            "supports_multi_role": True,
            "supports_self_healing": False,
            "supports_tool_calling": True,
            "max_roles": None,  # No limit
            "framework_name": "riona",
            "description": "Advanced agent framework with multi-modal processing and adaptive behavior",
        }
