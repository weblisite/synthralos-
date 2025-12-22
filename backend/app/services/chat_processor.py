"""
Chat Processor Service

Processes chat messages in 4 modes:
- automation: Create workflows from natural language
- agent: Run agent tasks
- agent_flow: Multi-step agent workflows
- code: Execute code
"""

import uuid
from datetime import datetime
from typing import Any

from sqlmodel import Session

from app.agents.router import default_agent_router
from app.core.config import settings
from app.workflows.engine import WorkflowEngine

workflow_engine = WorkflowEngine()


class ChatProcessor:
    """Processes chat messages and routes to appropriate handlers."""

    def __init__(self):
        self.agent_router = default_agent_router

    async def process_message(
        self,
        session: Session,
        user_id: str,
        content: str,
        mode: str,
    ) -> dict[str, Any]:
        """
        Process a chat message based on mode.

        Args:
            session: Database session
            user_id: User ID
            content: Message content
            mode: Chat mode (automation, agent, agent_flow, code)

        Returns:
            Response dictionary with content and tool_calls
        """
        if mode == "automation":
            return await self._process_automation_mode(session, user_id, content)
        elif mode == "agent":
            return await self._process_agent_mode(session, user_id, content)
        elif mode == "agent_flow":
            return await self._process_agent_flow_mode(session, user_id, content)
        elif mode == "code":
            return await self._process_code_mode(session, user_id, content)
        else:
            return {
                "content": f"Unknown mode: {mode}. Supported modes: automation, agent, agent_flow, code",
                "tool_calls": [],
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def _process_automation_mode(
        self,
        session: Session,
        user_id: str,
        content: str,
    ) -> dict[str, Any]:
        """
        Process automation mode: Create workflow from natural language.

        This will use LLM to parse natural language and create workflow nodes.
        """
        # Use OpenAI API if available
        if settings.OPENAI_API_KEY:
            try:
                return await self._process_with_openai("automation", content, user_id)
            except Exception as e:
                # Fallback to basic response if OpenAI fails
                return {
                    "content": f'I\'ll help you create an automation workflow for: "{content}"\n\n'
                    f"However, I encountered an error processing your request: {str(e)}\n\n"
                    f"You can manually create workflows using the Workflow Builder UI.",
                    "tool_calls": [],
                    "timestamp": datetime.utcnow().isoformat(),
                }
        else:
            # Fallback response when OpenAI is not configured
            return {
                "content": f'I\'ll help you create an automation workflow for: "{content}"\n\n'
                "To enable AI-powered workflow creation, please configure OPENAI_API_KEY in your environment.\n\n"
                "For now, you can manually create workflows using the Workflow Builder UI.",
                "tool_calls": [],
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def _process_with_openai(
        self, mode: str, content: str, user_id: str
    ) -> dict[str, Any]:
        """Process chat message using OpenAI API."""
        # Import Langfuse client
        from app.observability.langfuse import default_langfuse_client

        try:
            import openai

            # Get user's API key or fallback to platform default
            from app.services.api_keys import default_api_key_service

            api_key = default_api_key_service.get_user_api_key_without_session(
                user_id, "openai"
            )

            if not api_key:
                raise ValueError("OpenAI API key not configured")

            client = openai.OpenAI(api_key=api_key)

            # Build system prompt based on mode
            system_prompts = {
                "automation": """You are an AI assistant that helps users create automation workflows from natural language.
                When a user describes an automation task, analyze it and provide:
                1. A clear explanation of what the workflow will do
                2. The steps/components needed
                3. Suggestions for triggers, connectors, and logic nodes

                Be helpful and provide actionable guidance.""",
                "agent": """You are an AI assistant that helps users execute agent tasks.
                Provide clear, actionable responses to user queries.""",
                "agent_flow": """You are an AI assistant that helps users create multi-step agent workflows.
                Analyze the user's request and suggest a sequence of agent tasks.""",
                "code": """You are an AI assistant that helps users execute code.
                Provide code examples and explanations.""",
            }

            system_prompt = system_prompts.get(mode, "You are a helpful AI assistant.")

            # Create Langfuse trace for this LLM call
            trace = default_langfuse_client.trace(
                name=f"chat_{mode}",
                user_id=user_id,
                metadata={"mode": mode, "content_length": len(content)},
            )

            # Call OpenAI API
            model = "gpt-4o-mini"
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content},
            ]

            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
            )

            ai_response = response.choices[0].message.content

            # Log generation to Langfuse
            if trace:
                trace_id = getattr(trace, "id", None) or str(trace)
                default_langfuse_client.generation(
                    trace_id=trace_id,
                    name="openai_chat_completion",
                    model=model,
                    input_data={"messages": messages, "mode": mode},
                    output_data={"content": ai_response},
                    metadata={
                        "temperature": 0.7,
                        "max_tokens": 1000,
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

            return {
                "content": ai_response,
                "tool_calls": [],
                "timestamp": datetime.utcnow().isoformat(),
            }
        except ImportError:
            return {
                "content": "OpenAI library not installed. Install with: pip install openai",
                "tool_calls": [],
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            raise Exception(f"OpenAI API call failed: {str(e)}")

    async def _process_agent_mode(
        self,
        session: Session,
        user_id: str,
        content: str,
    ) -> dict[str, Any]:
        """
        Process agent mode: Run agent task.

        Uses the agent router to execute agent tasks.
        """
        try:
            # Create agent task request
            task_data = {
                "task_type": "general",
                "input_data": {
                    "prompt": content,
                    "user_id": user_id,
                },
            }

            # Route to appropriate agent framework
            # Use the agent router's execute_task method
            agent_result = self.agent_router.execute_task(
                session=session,
                task_type="general",
                input_data=task_data["input_data"],
                framework=None,  # Auto-select
                agent_id=None,
                task_requirements=None,
            )

            # Parse result - agent_result is a dict from execute_task
            if isinstance(agent_result, dict):
                if agent_result.get("status") == "success":
                    framework = agent_result.get("framework", "unknown")
                    output = agent_result.get("output", {})

                    response_content = f"""**Agent Task Completed**

**Framework Used:** {framework}
**Task:** {content}

**Result:**
{output.get('result', 'Task completed successfully')}

**Metadata:**
- Duration: {output.get('duration_ms', 0)}ms
- Tokens Used: {output.get('tokens_used', 'N/A')}
"""

                    tool_calls = []
                    if output.get("tool_calls"):
                        tool_calls = [
                            {
                                "id": str(uuid.uuid4()),
                                "name": tool_call.get("name", "unknown"),
                                "arguments": tool_call.get("arguments", {}),
                                "status": "completed",
                                "result": tool_call.get("result"),
                            }
                            for tool_call in output.get("tool_calls", [])
                        ]

                    return {
                        "content": response_content,
                        "tool_calls": tool_calls,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                else:
                    return {
                        "content": f"Agent task failed: {agent_result.get('error', 'Unknown error')}",
                        "tool_calls": [],
                        "timestamp": datetime.utcnow().isoformat(),
                    }
            else:
                # Fallback if result format is unexpected
                return {
                    "content": f"Agent task completed. Result: {str(agent_result)[:200]}",
                    "tool_calls": [],
                    "timestamp": datetime.utcnow().isoformat(),
                }

        except Exception as e:
            return {
                "content": f"Error executing agent task: {str(e)}",
                "tool_calls": [],
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def _process_agent_flow_mode(
        self,
        session: Session,
        user_id: str,
        content: str,
    ) -> dict[str, Any]:
        """
        Process agent_flow mode: Multi-step agent workflow.

        Creates a workflow that chains multiple agent tasks together.
        """
        # TODO: Implement multi-step agent workflow creation
        # This should:
        # 1. Parse the request to identify multiple steps
        # 2. Create a workflow with multiple agent nodes
        # 3. Chain them together

        response_content = f"""**Agent Flow Mode**

I'll create a multi-step agent workflow for: "{content}"

**Agent Flow Creation (Placeholder)**

This will be enhanced to:
1. Parse multi-step requirements
2. Create workflow with multiple agent nodes
3. Chain agent outputs as inputs to next agents
4. Execute the workflow

**Example Flow:**
1. Agent 1: Research topic
2. Agent 2: Generate content based on research
3. Agent 3: Review and refine content

For now, use the Workflow Builder to manually create agent flows."""

        return {
            "content": response_content,
            "tool_calls": [],
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def _process_code_mode(
        self,
        session: Session,
        user_id: str,
        content: str,
    ) -> dict[str, Any]:
        """
        Process code mode: Execute code.

        Uses code execution service to run user code in secure sandbox.
        """
        # Integrate with code execution service
        from app.code.service import default_code_execution_service

        try:
            # Try to extract code from message (basic implementation)
            # In production, use LLM to parse code blocks
            code = content
            language = "python"  # Default to Python, could be detected from code blocks

            # Execute code
            result = default_code_execution_service.execute_code(
                session=session,
                code=code,
                language=language,
                input_data={},
                runtime="subprocess",
            )

            if result.get("exit_code") == 0:
                stdout = result.get("stdout", "")
                response_content = (
                    f"✅ Code executed successfully!\n\n**Output:**\n```\n{stdout}\n```"
                )
                if result.get("memory_mb"):
                    response_content += (
                        f"\n**Memory Usage:** {result.get('memory_mb')} MB"
                    )
            else:
                stderr = result.get("stderr", "")
                response_content = f"❌ Code execution failed (exit code: {result.get('exit_code')}).\n\n**Error:**\n```\n{stderr}\n```"

            return {
                "content": response_content,
                "tool_calls": [],
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            return {
                "content": f"Code execution error: {str(e)}\n\nPlease ensure your code is valid and the required runtime is installed.",
                "tool_calls": [],
                "timestamp": datetime.utcnow().isoformat(),
            }


# Default chat processor instance
default_chat_processor = ChatProcessor()
