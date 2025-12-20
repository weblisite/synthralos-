"""
Swarm Framework Integration

Swarm is a framework for building and orchestrating swarms of AI agents.
"""

import logging
from typing import Any

from app.agents.frameworks.base import BaseAgentFramework

logger = logging.getLogger(__name__)


class SwarmFramework(BaseAgentFramework):
    """
    Swarm framework wrapper.

    Swarm specializes in:
    - Swarm intelligence
    - Distributed agent coordination
    - Collective decision-making
    - Emergent behavior
    """

    def __init__(self):
        """Initialize Swarm framework."""
        super().__init__()

    def _check_availability(self) -> None:
        """Check if Swarm is available."""
        try:
            from app.core.config import settings

            if settings.OPENAI_API_KEY:
                import openai

                self.is_available = True
                logger.info(
                    "Swarm framework is available (using OpenAI for swarm intelligence)"
                )
            else:
                self.is_available = False
                logger.warning("Swarm requires OPENAI_API_KEY to be configured")
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
        Execute a task using Swarm (distributed agent coordination).

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
                    "Swarm framework not available. Please configure OPENAI_API_KEY."
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
            swarm_config = input_data.get("swarm_config", {})
            agents_count = swarm_config.get("agents_count", 3)

            logs = [f"Swarm execution started with {agents_count} agents"]
            logs.append(f"Task: {task}")

            # Distribute task to multiple agents (swarm)
            swarm_context = context or {}
            swarm_context["task"] = task
            swarm_context["agents_count"] = agents_count
            swarm_context["agent_outputs"] = {}

            # Each agent works on the task independently
            agent_outputs = []
            for i in range(agents_count):
                agent_prompt = f"""You are agent {i + 1} in a swarm of {agents_count} agents working on a collective task.

Task: {task}

Your Role: Work on this task independently. Provide your perspective and solution.
Agent ID: {i + 1}/{agents_count}

Provide your independent analysis and solution to the task."""

                response = client.chat.completions.create(
                    model=input_data.get("model", "gpt-4o-mini"),
                    messages=[
                        {
                            "role": "system",
                            "content": f"You are agent {i + 1} in a swarm. Work independently but consider collective goals.",
                        },
                        {"role": "user", "content": agent_prompt},
                    ],
                    temperature=0.7 + (i * 0.1),  # Vary temperature for diversity
                    max_tokens=600,
                )

                agent_output = response.choices[0].message.content
                agent_outputs.append(
                    {
                        "agent_id": i + 1,
                        "output": agent_output,
                    }
                )
                swarm_context["agent_outputs"][f"agent_{i + 1}"] = agent_output

                logs.append(f"Agent {i + 1}/{agents_count} completed")

            # Collective decision-making (swarm intelligence)
            synthesis_prompt = f"""You are a swarm coordinator synthesizing outputs from multiple agents.

Task: {task}

Agent Outputs:
{chr(10).join([f"Agent {ao['agent_id']}: {ao['output'][:400]}" for ao in agent_outputs])}

Synthesize the collective intelligence from all agents. Identify:
1. Common themes and agreements
2. Unique perspectives
3. Best solution combining all insights
4. Collective decision

Provide a comprehensive final solution that leverages swarm intelligence."""

            synthesis_response = client.chat.completions.create(
                model=input_data.get("model", "gpt-4o-mini"),
                messages=[
                    {
                        "role": "system",
                        "content": "You are a swarm coordinator that synthesizes multiple agent outputs into a collective decision.",
                    },
                    {"role": "user", "content": synthesis_prompt},
                ],
                temperature=0.7,
                max_tokens=1200,
            )

            final_output = synthesis_response.choices[0].message.content

            logs.append("Swarm synthesis completed")
            logs.append("Task completed successfully")

            return {
                "status": "completed",
                "result": {
                    "output": final_output,
                    "agents_count": agents_count,
                    "agent_outputs": agent_outputs,
                    "swarm_decision": final_output,
                },
                "context": swarm_context,
                "logs": logs,
            }

        except Exception as e:
            logger.error(f"Swarm task execution failed: {e}", exc_info=True)
            return {
                "status": "failed",
                "result": None,
                "context": context or {},
                "logs": [f"Swarm execution error: {str(e)}"],
                "error": str(e),
            }

    def get_capabilities(self) -> dict[str, Any]:
        """Get Swarm capabilities."""
        return {
            "supports_recursive_planning": False,
            "supports_multi_role": True,
            "supports_self_healing": False,
            "supports_tool_calling": False,
            "max_roles": None,  # No limit
            "framework_name": "swarm",
            "description": "Swarm intelligence framework for distributed agent coordination",
        }
