"""
KUSH AI Framework Integration

KUSH AI is a framework for building autonomous AI agents with advanced capabilities.
"""

import logging
from typing import Any

from app.agents.frameworks.base import BaseAgentFramework

logger = logging.getLogger(__name__)


class KUSHAIFramework(BaseAgentFramework):
    """
    KUSH AI framework wrapper.

    KUSH AI specializes in:
    - Autonomous agent execution
    - Advanced reasoning
    - Tool integration
    - Long-term memory
    """

    def __init__(self):
        """Initialize KUSH AI framework."""
        super().__init__()

    def _check_availability(self) -> None:
        """Check if KUSH AI is available."""
        try:
            from app.core.config import settings

            if settings.OPENAI_API_KEY:
                import openai

                self.is_available = True
                logger.info("KUSH AI framework is available (using OpenAI with memory)")
            else:
                self.is_available = False
                logger.warning("KUSH AI requires OPENAI_API_KEY to be configured")
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
        Execute a task using KUSH AI (autonomous agent with memory and tools).

        Args:
            task_type: Type of task
            input_data: Task input data
            context: Optional context data (used as memory)

        Returns:
            Task execution result
        """
        if not self.is_available:
            return {
                "status": "failed",
                "result": None,
                "context": context or {},
                "logs": [
                    "KUSH AI framework not available. Please configure OPENAI_API_KEY."
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
            tools = input_data.get("tools", [])
            memory_config = input_data.get("memory", {})

            # Build memory context
            memory_context = context or {}
            if memory_config.get("enabled", True) and memory_context:
                memory_summary = "\n".join(
                    [
                        f"Memory: {k} = {str(v)[:200]}"
                        for k, v in list(memory_context.items())[:10]
                    ]
                )
            else:
                memory_summary = "No previous memory"

            # Build tool descriptions
            tool_descriptions = ""
            if tools:
                tool_descriptions = "\nAvailable Tools:\n" + "\n".join(
                    [
                        f"- {tool.get('name', 'unknown')}: {tool.get('description', '')}"
                        for tool in tools[:10]
                    ]
                )

            # Enhanced prompt with memory and tools
            enhanced_prompt = f"""You are an autonomous AI agent with long-term memory and tool access.

Task: {task}

{memory_summary}

{tool_descriptions}

Execute the task using available tools and memory. Provide a comprehensive result."""

            # Define functions for tool calling if tools are provided
            functions = []
            if tools:
                for tool in tools[:5]:  # Limit to 5 tools for efficiency
                    tool_name = tool.get("name", "unknown_tool")
                    functions.append(
                        {
                            "type": "function",
                            "function": {
                                "name": tool_name,
                                "description": tool.get(
                                    "description", f"Tool: {tool_name}"
                                ),
                                "parameters": {
                                    "type": "object",
                                    "properties": tool.get("parameters", {}),
                                    "required": tool.get("required", []),
                                },
                            },
                        }
                    )

            response = client.chat.completions.create(
                model=input_data.get("model", "gpt-4o-mini"),
                messages=[
                    {
                        "role": "system",
                        "content": "You are an autonomous AI agent with memory and tool access. Use tools when needed and remember important information.",
                    },
                    {"role": "user", "content": enhanced_prompt},
                ],
                tools=functions if functions else None,
                tool_choice="auto" if functions else None,
                temperature=0.7,
                max_tokens=1500,
            )

            result = response.choices[0].message.content
            tool_calls = []
            if response.choices[0].message.tool_calls:
                tool_calls = [
                    {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    }
                    for tc in response.choices[0].message.tool_calls
                ]

            # Update memory
            updated_context = memory_context.copy()
            updated_context["last_task"] = task_type
            updated_context["last_result"] = result[:300]
            updated_context["tools_used"] = [tc["name"] for tc in tool_calls]

            return {
                "status": "completed",
                "result": {
                    "output": result,
                    "tools_used": len(tool_calls),
                    "tool_calls": tool_calls,
                    "memory_enabled": bool(memory_config.get("enabled", True)),
                },
                "context": updated_context,
                "logs": [
                    f"KUSH AI execution started: {task}",
                    f"Using {len(tools)} available tools",
                    f"Memory: {'enabled' if memory_config.get('enabled', True) else 'disabled'}",
                    f"Tools called: {len(tool_calls)}",
                    "Task completed successfully",
                ],
            }

        except Exception as e:
            logger.error(f"KUSH AI task execution failed: {e}", exc_info=True)
            return {
                "status": "failed",
                "result": None,
                "context": context or {},
                "logs": [f"KUSH AI execution error: {str(e)}"],
                "error": str(e),
            }

    def get_capabilities(self) -> dict[str, Any]:
        """Get KUSH AI capabilities."""
        return {
            "supports_recursive_planning": True,
            "supports_multi_role": False,
            "supports_self_healing": False,
            "supports_tool_calling": True,
            "max_roles": 1,
            "framework_name": "kush_ai",
            "description": "Autonomous agent framework with advanced reasoning and tool integration",
        }
