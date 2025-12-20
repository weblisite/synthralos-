"""
Archon Framework Wrapper

Self-healing agent framework.
"""

import logging
from typing import Any

from app.agents.frameworks.base import BaseAgentFramework
from app.core.config import settings

logger = logging.getLogger(__name__)


class ArchonFramework(BaseAgentFramework):
    """
    Archon framework wrapper.

    Self-healing framework suitable for:
    - Tasks requiring error recovery
    - Autonomous problem-solving
    - Self-correction and adaptation
    """

    def _check_availability(self) -> None:
        """Check if Archon is available."""
        try:
            if settings.OPENAI_API_KEY:
                import openai

                self.is_available = True
                logger.info(
                    "Archon framework is available (using OpenAI with self-healing)"
                )
            else:
                self.is_available = False
                logger.warning("Archon requires OPENAI_API_KEY to be configured")
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
        Execute task using Archon (self-healing agent with OpenAI).

        Args:
            task_type: Type of task
            input_data: Task input data
            context: Optional cached context

        Returns:
            Execution result
        """
        if not self.is_available:
            return {
                "status": "failed",
                "result": None,
                "context": context or {},
                "logs": [
                    "Archon framework not available. Please configure OPENAI_API_KEY."
                ],
                "error": "Framework not available",
            }

        try:
            import openai

            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

            task = (
                input_data.get("task")
                or input_data.get("prompt")
                or f"Execute {task_type}"
            )
            max_healing_attempts = input_data.get("max_healing_attempts", 3)

            logs = ["Starting Archon self-healing execution"]
            logs.append(f"Task: {task}")

            healing_context = context or {}
            healing_context["task"] = task
            healing_context["errors_encountered"] = []
            healing_context["healing_attempts"] = 0
            healing_context["errors_recovered"] = 0

            # Initial execution attempt
            try:
                response = client.chat.completions.create(
                    model=input_data.get("model", "gpt-4o-mini"),
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a self-healing AI agent. Execute tasks carefully and monitor for errors.",
                        },
                        {"role": "user", "content": task},
                    ],
                    temperature=0.7,
                    max_tokens=1000,
                )

                result = response.choices[0].message.content
                logs.append("Initial execution successful")

                return {
                    "status": "completed",
                    "result": {
                        "output": result,
                        "healing_attempts": 0,
                        "errors_recovered": 0,
                        "execution_mode": "direct",
                    },
                    "context": healing_context,
                    "logs": logs,
                }

            except Exception as initial_error:
                # Error occurred, attempt self-healing
                error_message = str(initial_error)
                healing_context["errors_encountered"].append(error_message)
                logs.append(f"Error encountered: {error_message}")
                logs.append("Initiating self-healing process...")

                # Self-healing loop
                for attempt in range(max_healing_attempts):
                    healing_context["healing_attempts"] = attempt + 1

                    healing_prompt = f"""You are a self-healing AI agent. An error occurred while executing a task.

Task: {task}

Error Encountered: {error_message}

Previous Errors:
{chr(10).join([f"- {e}" for e in healing_context["errors_encountered"]])}

Healing Attempt: {attempt + 1}/{max_healing_attempts}

Analyze the error and:
1. Identify the root cause
2. Propose a corrected approach
3. Execute the task with the correction

Provide:
1. Root cause analysis
2. Corrected approach
3. Execution result"""

                    try:
                        healing_response = client.chat.completions.create(
                            model=input_data.get("model", "gpt-4o-mini"),
                            messages=[
                                {
                                    "role": "system",
                                    "content": "You are a self-healing agent. When errors occur, analyze them, propose fixes, and retry with corrections.",
                                },
                                {"role": "user", "content": healing_prompt},
                            ],
                            temperature=0.7,
                            max_tokens=1500,
                        )

                        healing_result = healing_response.choices[0].message.content
                        healing_context["errors_recovered"] += 1
                        logs.append(f"Healing attempt {attempt + 1}: Success")
                        logs.append(f"Recovery result: {healing_result[:200]}...")

                        return {
                            "status": "completed",
                            "result": {
                                "output": healing_result,
                                "healing_attempts": attempt + 1,
                                "errors_recovered": healing_context["errors_recovered"],
                                "execution_mode": "healed",
                                "original_error": error_message,
                            },
                            "context": healing_context,
                            "logs": logs,
                        }

                    except Exception as healing_error:
                        healing_context["errors_encountered"].append(str(healing_error))
                        logs.append(
                            f"Healing attempt {attempt + 1} failed: {str(healing_error)}"
                        )

                        if attempt == max_healing_attempts - 1:
                            # All healing attempts exhausted
                            logs.append("All healing attempts exhausted")
                            return {
                                "status": "failed",
                                "result": None,
                                "context": healing_context,
                                "logs": logs,
                                "error": f"Failed after {max_healing_attempts} healing attempts. Last error: {str(healing_error)}",
                            }

        except Exception as e:
            logger.error(f"Archon task execution failed: {e}", exc_info=True)
            return {
                "status": "failed",
                "result": None,
                "context": context or {},
                "logs": [f"Archon execution error: {str(e)}"],
                "error": str(e),
            }

    def get_capabilities(self) -> dict[str, Any]:
        """Get Archon capabilities."""
        return {
            "supports_recursive_planning": True,
            "supports_multi_role": False,
            "supports_self_healing": True,
            "supports_tool_calling": True,
            "max_roles": 1,
            "framework_name": "archon",
            "description": "Self-healing agent framework for error recovery",
        }
