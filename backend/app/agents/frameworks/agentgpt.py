"""
AgentGPT Framework Wrapper

Simple agent framework for straightforward tasks.
"""

import logging
from typing import Any

from app.agents.frameworks.base import BaseAgentFramework
from app.core.config import settings

logger = logging.getLogger(__name__)


class AgentGPTFramework(BaseAgentFramework):
    """
    AgentGPT framework wrapper.

    Simple agent framework suitable for:
    - Straightforward tasks
    - Single-step operations
    - Basic reasoning
    """

    def _check_availability(self) -> None:
        """Check if AgentGPT is available."""
        try:
            # Check if OpenAI API key is configured
            if settings.OPENAI_API_KEY:
                import openai

                self.is_available = True
                logger.info("AgentGPT framework is available (using OpenAI)")
            else:
                self.is_available = False
                logger.warning("AgentGPT requires OPENAI_API_KEY to be configured")
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
        Execute task using AgentGPT (OpenAI-based simple agent).

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
                    "AgentGPT framework not available. Please configure OPENAI_API_KEY."
                ],
                "error": "Framework not available",
            }

        try:
            import openai

            from app.observability.langfuse import default_langfuse_client

            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

            # Build prompt from input data
            prompt = (
                input_data.get("prompt")
                or input_data.get("task")
                or input_data.get("message", "")
            )
            if not prompt:
                prompt = f"Execute task: {task_type}"

            # Add context if available
            if context:
                context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
                prompt = f"Context:\n{context_str}\n\nTask: {prompt}"

            # Create Langfuse trace
            user_id = input_data.get("user_id")
            trace = default_langfuse_client.trace(
                name=f"agentgpt_{task_type}",
                user_id=str(user_id) if user_id else None,
                metadata={"task_type": task_type, "framework": "agentgpt"},
            )

            model = input_data.get("model", "gpt-4o-mini")
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful AI agent that executes tasks efficiently and accurately. Provide clear, actionable responses.",
                },
                {"role": "user", "content": prompt},
            ]

            # Call OpenAI API
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=input_data.get("temperature", 0.7),
                max_tokens=input_data.get("max_tokens", 1000),
            )

            result_text = response.choices[0].message.content

            # Log generation to Langfuse
            if trace:
                trace_id = getattr(trace, "id", None) or str(trace)
                default_langfuse_client.generation(
                    trace_id=trace_id,
                    name="agentgpt_completion",
                    model=model,
                    input_data={"messages": messages, "task_type": task_type},
                    output_data={"content": result_text},
                    metadata={
                        "temperature": input_data.get("temperature", 0.7),
                        "max_tokens": input_data.get("max_tokens", 1000),
                        "usage": {
                            "prompt_tokens": response.usage.prompt_tokens
                            if response.usage
                            else None,
                            "completion_tokens": response.usage.completion_tokens
                            if response.usage
                            else None,
                            "total_tokens": response.usage.total_tokens
                            if response.usage
                            else None,
                        },
                    },
                )

            # Update context with result
            updated_context = context or {}
            updated_context["last_task"] = task_type
            updated_context["last_result"] = result_text[:200]  # Store summary

            return {
                "status": "completed",
                "result": {
                    "output": result_text,
                    "task_type": task_type,
                    "model": input_data.get("model", "gpt-4o-mini"),
                    "tokens_used": response.usage.total_tokens
                    if response.usage
                    else None,
                },
                "context": updated_context,
                "logs": [
                    f"Starting AgentGPT task: {task_type}",
                    f"Using model: {input_data.get('model', 'gpt-4o-mini')}",
                    "Task completed successfully",
                ],
            }

        except Exception as e:
            logger.error(f"AgentGPT task execution failed: {e}", exc_info=True)
            return {
                "status": "failed",
                "result": None,
                "context": context or {},
                "logs": [f"AgentGPT execution error: {str(e)}"],
                "error": str(e),
            }

    def get_capabilities(self) -> dict[str, Any]:
        """Get AgentGPT capabilities."""
        return {
            "supports_recursive_planning": False,
            "supports_multi_role": False,
            "supports_self_healing": False,
            "supports_tool_calling": True,
            "max_roles": 1,
            "framework_name": "agentgpt",
            "description": "Simple agent framework for straightforward tasks",
        }
