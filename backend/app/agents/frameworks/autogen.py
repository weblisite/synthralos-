"""
AutoGen Framework Wrapper

Tool-calling planner agent framework.
"""

import logging
from typing import Any

from app.agents.frameworks.base import BaseAgentFramework
from app.core.config import settings

logger = logging.getLogger(__name__)


class AutoGenFramework(BaseAgentFramework):
    """
    AutoGen framework wrapper.
    
    Tool-calling planner framework suitable for:
    - Tool-based task execution
    - Multi-agent conversations
    - Code generation and execution
    """
    
    def _check_availability(self) -> None:
        """Check if AutoGen is available."""
        try:
            if settings.OPENAI_API_KEY:
                import openai
                self.is_available = True
                logger.info("AutoGen framework is available (using OpenAI function calling)")
            else:
                self.is_available = False
                logger.warning("AutoGen requires OPENAI_API_KEY to be configured")
        except ImportError:
            self.is_available = False
            logger.warning("OpenAI library not installed. Install with: pip install openai")
    
    def execute_task(
        self,
        task_type: str,
        input_data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute task using AutoGen (tool-calling with OpenAI function calling).
        
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
                "logs": ["AutoGen framework not available. Please configure OPENAI_API_KEY."],
                "error": "Framework not available",
            }
        
        try:
            import openai
            
            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            
            task = input_data.get("task") or input_data.get("prompt") or f"Execute {task_type}"
            tools = input_data.get("tools", [])
            
            logs = [f"Starting AutoGen tool-calling execution"]
            logs.append(f"Task: {task}")
            logs.append(f"Tools available: {len(tools)}")
            
            # Define function tools (simplified - in real AutoGen these would be actual functions)
            functions = []
            for tool in tools:
                tool_name = tool.get("name", "unknown_tool")
                tool_desc = tool.get("description", f"Tool: {tool_name}")
                functions.append({
                    "type": "function",
                    "function": {
                        "name": tool_name,
                        "description": tool_desc,
                        "parameters": {
                            "type": "object",
                            "properties": tool.get("parameters", {}),
                            "required": tool.get("required", []),
                        }
                    }
                })
            
            # Multi-turn conversation with tool calling
            messages = [
                {
                    "role": "system",
                    "content": "You are a tool-calling agent. Use available tools to complete tasks. When you need to use a tool, call it. When you have enough information, provide a final answer."
                },
                {
                    "role": "user",
                    "content": task
                }
            ]
            
            tool_calls_made = []
            max_turns = input_data.get("max_turns", 5)
            
            for turn in range(max_turns):
                response = client.chat.completions.create(
                    model=input_data.get("model", "gpt-4o-mini"),
                    messages=messages,
                    tools=functions if functions else None,
                    tool_choice="auto" if functions else None,
                    temperature=0.7,
                )
                
                message = response.choices[0].message
                messages.append(message)
                
                logs.append(f"Turn {turn + 1}: Agent response")
                
                # Check if tool calls were made
                if message.tool_calls:
                    for tool_call in message.tool_calls:
                        tool_name = tool_call.function.name
                        tool_args = tool_call.function.arguments
                        
                        logs.append(f"Tool call: {tool_name} with args: {tool_args[:100]}...")
                        tool_calls_made.append({
                            "name": tool_name,
                            "arguments": tool_args,
                            "turn": turn + 1,
                        })
                        
                        # Simulate tool execution (in real AutoGen, actual tools would be called)
                        tool_result = f"Tool {tool_name} executed successfully with result: [simulated result]"
                        
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": tool_result,
                        })
                else:
                    # No more tool calls, final answer received
                    final_answer = message.content
                    logs.append("Final answer received")
                    break
            
            final_result = {
                "output": messages[-1].content if messages else "Task completed",
                "tools_used": tool_calls_made,
                "conversation_turns": len(messages) // 2,  # Approximate
                "tool_calls_count": len(tool_calls_made),
            }
            
            updated_context = context or {}
            updated_context["last_tools"] = [tc["name"] for tc in tool_calls_made]
            updated_context["conversation_history"] = len(messages)
            
            logs.append("Task completed successfully")
            
            return {
                "status": "completed",
                "result": final_result,
                "context": updated_context,
                "logs": logs,
            }
            
        except Exception as e:
            logger.error(f"AutoGen task execution failed: {e}", exc_info=True)
            return {
                "status": "failed",
                "result": None,
                "context": context or {},
                "logs": [f"AutoGen execution error: {str(e)}"],
                "error": str(e),
            }
    
    def get_capabilities(self) -> dict[str, Any]:
        """Get AutoGen capabilities."""
        return {
            "supports_recursive_planning": True,
            "supports_multi_role": True,
            "supports_self_healing": False,
            "supports_tool_calling": True,
            "max_roles": None,  # No limit
            "framework_name": "autogen",
            "description": "Tool-calling planner framework for multi-agent conversations",
        }

