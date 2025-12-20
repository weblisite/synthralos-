"""
MetaGPT Framework Wrapper

Multi-role agent framework.
"""

import logging
from typing import Any

from app.agents.frameworks.base import BaseAgentFramework
from app.core.config import settings

logger = logging.getLogger(__name__)


class MetaGPTFramework(BaseAgentFramework):
    """
    MetaGPT framework wrapper.

    Multi-role framework suitable for:
    - Team-based agent collaboration
    - Role-based task distribution
    - Complex workflows requiring multiple agents
    """

    def _check_availability(self) -> None:
        """Check if MetaGPT is available."""
        try:
            if settings.OPENAI_API_KEY:
                import openai

                self.is_available = True
                logger.info("MetaGPT framework is available (using OpenAI)")
            else:
                self.is_available = False
                logger.warning("MetaGPT requires OPENAI_API_KEY to be configured")
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
        Execute task using MetaGPT (multi-role collaboration with OpenAI).

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
                    "MetaGPT framework not available. Please configure OPENAI_API_KEY."
                ],
                "error": "Framework not available",
            }

        try:
            import openai

            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

            # Get roles and task
            roles = input_data.get("roles", ["ProductManager", "Architect", "Engineer"])
            task = (
                input_data.get("task")
                or input_data.get("prompt")
                or f"Execute {task_type}"
            )

            logs = [f"Starting MetaGPT multi-role execution with {len(roles)} roles"]
            logs.append(f"Roles: {', '.join(roles)}")
            logs.append(f"Task: {task}")

            # Role definitions
            role_descriptions = {
                "ProductManager": "You are a Product Manager. Your role is to understand requirements, prioritize features, and coordinate the team.",
                "Architect": "You are a Software Architect. Your role is to design system architecture, make technical decisions, and ensure scalability.",
                "Engineer": "You are a Software Engineer. Your role is to implement solutions, write code, and ensure quality.",
                "Designer": "You are a UX Designer. Your role is to design user interfaces and ensure good user experience.",
                "QA": "You are a QA Engineer. Your role is to test solutions and ensure quality.",
            }

            # Sequential role-based execution
            collaboration_context = context or {}
            collaboration_context["task"] = task
            collaboration_context["roles"] = roles
            collaboration_context["role_outputs"] = {}

            previous_output = task

            for i, role in enumerate(roles):
                role_desc = role_descriptions.get(
                    role, f"You are a {role}. Your role is to contribute to the task."
                )

                role_prompt = f"""{role_desc}

Task: {task}

Previous Role Outputs:
{previous_output}

Your Task: As the {role}, analyze the task and previous outputs. Provide your contribution to complete the task.

Respond with:
1. Your analysis
2. Your contribution
3. Any recommendations for next steps"""

                response = client.chat.completions.create(
                    model=input_data.get("model", "gpt-4o-mini"),
                    messages=[
                        {
                            "role": "system",
                            "content": f"You are a {role} working in a team. Collaborate effectively with other roles.",
                        },
                        {"role": "user", "content": role_prompt},
                    ],
                    temperature=0.7,
                    max_tokens=1000,
                )

                role_output = response.choices[0].message.content
                collaboration_context["role_outputs"][role] = role_output
                previous_output = role_output

                logs.append(f"Step {i + 1}: {role} completed")
                logs.append(f"{role} output: {role_output[:200]}...")

            # Final synthesis
            synthesis_prompt = f"""Synthesize the outputs from all roles to create a final solution.

Task: {task}

Role Outputs:
{chr(10).join([f"{role}: {output[:500]}" for role, output in collaboration_context["role_outputs"].items()])}

Provide a comprehensive final solution that integrates all role contributions."""

            final_response = client.chat.completions.create(
                model=input_data.get("model", "gpt-4o-mini"),
                messages=[
                    {
                        "role": "system",
                        "content": "You are a synthesis agent that combines multi-role outputs into a final solution.",
                    },
                    {"role": "user", "content": synthesis_prompt},
                ],
                temperature=0.7,
                max_tokens=1500,
            )

            final_output = final_response.choices[0].message.content

            logs.append("Final synthesis completed")
            logs.append("Task completed successfully")

            return {
                "status": "completed",
                "result": {
                    "output": final_output,
                    "roles_used": roles,
                    "role_outputs": collaboration_context["role_outputs"],
                    "collaboration_steps": len(roles),
                },
                "context": collaboration_context,
                "logs": logs,
            }

        except Exception as e:
            logger.error(f"MetaGPT task execution failed: {e}", exc_info=True)
            return {
                "status": "failed",
                "result": None,
                "context": context or {},
                "logs": [f"MetaGPT execution error: {str(e)}"],
                "error": str(e),
            }

    def get_capabilities(self) -> dict[str, Any]:
        """Get MetaGPT capabilities."""
        return {
            "supports_recursive_planning": True,
            "supports_multi_role": True,
            "supports_self_healing": False,
            "supports_tool_calling": True,
            "max_roles": None,  # No limit
            "framework_name": "metagpt",
            "description": "Multi-role agent framework for team-based collaboration",
        }
