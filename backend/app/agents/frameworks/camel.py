"""
Camel-AI Framework Integration

Camel-AI is a framework for building communicative agents for language instruction.
"""

import logging
from typing import Any

from app.agents.frameworks.base import BaseAgentFramework

logger = logging.getLogger(__name__)


class CamelAIFramework(BaseAgentFramework):
    """
    Camel-AI framework wrapper.

    Camel-AI specializes in:
    - Communicative agents
    - Role-playing scenarios
    - Multi-agent conversations
    - Language instruction
    """

    def __init__(self):
        """Initialize Camel-AI framework."""
        super().__init__()

    def _check_availability(self) -> None:
        """Check if Camel-AI is available."""
        try:
            from app.core.config import settings

            if settings.OPENAI_API_KEY:
                import openai

                self.is_available = True
                logger.info(
                    "Camel-AI framework is available (using OpenAI for role-playing)"
                )
            else:
                self.is_available = False
                logger.warning("Camel-AI requires OPENAI_API_KEY to be configured")
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
        Execute a task using Camel-AI (communicative role-playing agents).

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
                    "Camel-AI framework not available. Please configure OPENAI_API_KEY."
                ],
                "error": "Framework not available",
            }

        try:
            import openai

            from app.core.config import settings

            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

            scenario = input_data.get("scenario", "general conversation")
            roles = input_data.get("roles", ["User", "Assistant"])
            task = (
                input_data.get("task")
                or input_data.get("prompt")
                or f"Execute {task_type}"
            )

            logs = [f"Camel-AI execution started with scenario: {scenario}"]
            logs.append(f"Roles: {', '.join(roles)}")

            # Multi-agent conversation simulation
            conversation_context = context or {}
            conversation_context["scenario"] = scenario
            conversation_context["roles"] = roles
            conversation_context["conversation_history"] = []

            # Simulate conversation between roles
            conversation_turns = input_data.get("conversation_turns", 3)
            conversation_output = []

            current_message = task

            for turn in range(conversation_turns):
                # Alternate between roles
                role_index = turn % len(roles)
                current_role = roles[role_index]

                role_prompt = f"""You are participating in a role-playing scenario.

Scenario: {scenario}
Your Role: {current_role}
Other Roles: {', '.join([r for r in roles if r != current_role])}

Conversation History:
{chr(10).join(conversation_output[-3:]) if conversation_output else 'None'}

Current Message: {current_message}

Respond as {current_role} in this scenario. Be authentic to your role and contribute meaningfully to the conversation."""

                response = client.chat.completions.create(
                    model=input_data.get("model", "gpt-4o-mini"),
                    messages=[
                        {
                            "role": "system",
                            "content": f"You are {current_role} in a role-playing scenario. Stay in character and contribute authentically.",
                        },
                        {"role": "user", "content": role_prompt},
                    ],
                    temperature=0.8,  # Higher temperature for more creative role-playing
                    max_tokens=500,
                )

                role_response = response.choices[0].message.content
                conversation_output.append(f"{current_role}: {role_response}")
                conversation_context["conversation_history"].append(
                    {
                        "role": current_role,
                        "message": role_response,
                        "turn": turn + 1,
                    }
                )

                current_message = role_response
                logs.append(f"Turn {turn + 1}: {current_role} responded")

            # Final synthesis
            final_prompt = f"""Synthesize the conversation from this role-playing scenario.

Scenario: {scenario}
Roles: {', '.join(roles)}
Task: {task}

Conversation:
{chr(10).join(conversation_output)}

Provide a summary of the conversation and the final outcome."""

            final_response = client.chat.completions.create(
                model=input_data.get("model", "gpt-4o-mini"),
                messages=[
                    {
                        "role": "system",
                        "content": "You are a conversation synthesizer. Summarize role-playing conversations and extract key outcomes.",
                    },
                    {"role": "user", "content": final_prompt},
                ],
                temperature=0.7,
                max_tokens=800,
            )

            final_output = final_response.choices[0].message.content

            logs.append("Conversation synthesis completed")
            logs.append("Task completed successfully")

            return {
                "status": "completed",
                "result": {
                    "output": final_output,
                    "scenario": scenario,
                    "roles": roles,
                    "conversation": conversation_output,
                    "conversation_turns": conversation_turns,
                },
                "context": conversation_context,
                "logs": logs,
            }

        except Exception as e:
            logger.error(f"Camel-AI task execution failed: {e}", exc_info=True)
            return {
                "status": "failed",
                "result": None,
                "context": context or {},
                "logs": [f"Camel-AI execution error: {str(e)}"],
                "error": str(e),
            }

    def get_capabilities(self) -> dict[str, Any]:
        """Get Camel-AI capabilities."""
        return {
            "supports_recursive_planning": False,
            "supports_multi_role": True,
            "supports_self_healing": False,
            "supports_tool_calling": False,
            "max_roles": None,  # No limit
            "framework_name": "camel_ai",
            "description": "Communicative agent framework for role-playing scenarios",
        }
