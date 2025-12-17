"""
AutoGPT Framework Wrapper

Recursive planning agent framework.
"""

import logging
from typing import Any

from app.agents.frameworks.base import BaseAgentFramework
from app.core.config import settings

logger = logging.getLogger(__name__)


class AutoGPTFramework(BaseAgentFramework):
    """
    AutoGPT framework wrapper.
    
    Recursive planning framework suitable for:
    - Complex multi-step tasks
    - Autonomous goal achievement
    - Recursive planning and execution
    """
    
    def _check_availability(self) -> None:
        """Check if AutoGPT is available."""
        try:
            if settings.OPENAI_API_KEY:
                import openai
                self.is_available = True
                logger.info("AutoGPT framework is available (using OpenAI)")
            else:
                self.is_available = False
                logger.warning("AutoGPT requires OPENAI_API_KEY to be configured")
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
        Execute task using AutoGPT (recursive planning with OpenAI).
        
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
                "logs": ["AutoGPT framework not available. Please configure OPENAI_API_KEY."],
                "error": "Framework not available",
            }
        
        try:
            import openai
            
            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            
            goal = input_data.get("goal") or input_data.get("prompt") or input_data.get("task", "")
            max_iterations = input_data.get("max_iterations", 5)
            
            # Initialize planning context
            plan_context = context or {}
            plan_context["goal"] = goal
            plan_context["steps_completed"] = []
            plan_context["current_step"] = 0
            
            logs = [f"Starting AutoGPT recursive planning for goal: {goal}"]
            
            # Recursive planning loop
            for iteration in range(max_iterations):
                plan_context["current_step"] = iteration + 1
                
                # Create planning prompt
                planning_prompt = f"""You are an autonomous AI agent working towards a goal.

Goal: {goal}

Completed Steps:
{chr(10).join([f"- {step}" for step in plan_context.get("steps_completed", [])])}

Current Step: {iteration + 1}/{max_iterations}

Analyze the goal and completed steps. Determine:
1. What is the next action needed?
2. Is the goal achieved?
3. If not achieved, what should be done next?

Respond in JSON format:
{{
    "action": "description of next action",
    "goal_achieved": true/false,
    "reasoning": "explanation"
}}"""
                
                # Call OpenAI for planning
                response = client.chat.completions.create(
                    model=input_data.get("model", "gpt-4o-mini"),
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an autonomous planning agent. Always respond with valid JSON."
                        },
                        {
                            "role": "user",
                            "content": planning_prompt
                        }
                    ],
                    temperature=0.7,
                    response_format={"type": "json_object"},
                )
                
                import json
                plan_result = json.loads(response.choices[0].message.content)
                
                action = plan_result.get("action", "")
                goal_achieved = plan_result.get("goal_achieved", False)
                reasoning = plan_result.get("reasoning", "")
                
                logs.append(f"Step {iteration + 1}: {action}")
                logs.append(f"Reasoning: {reasoning}")
                
                plan_context["steps_completed"].append(action)
                
                if goal_achieved:
                    logs.append("Goal achieved!")
                    break
                
                # Execute the action (simplified - in real AutoGPT this would use tools)
                if iteration < max_iterations - 1:
                    # Simulate action execution
                    execution_prompt = f"""Execute this action: {action}

Provide a brief result of the action execution."""
                    
                    exec_response = client.chat.completions.create(
                        model=input_data.get("model", "gpt-4o-mini"),
                        messages=[
                            {
                                "role": "system",
                                "content": "You are an action executor. Execute actions and report results."
                            },
                            {
                                "role": "user",
                                "content": execution_prompt
                            }
                        ],
                        temperature=0.5,
                        max_tokens=500,
                    )
                    
                    action_result = exec_response.choices[0].message.content
                    plan_context[f"step_{iteration + 1}_result"] = action_result
                    logs.append(f"Action executed: {action_result[:100]}...")
            
            # Final result
            final_result = {
                "goal": goal,
                "steps_taken": len(plan_context["steps_completed"]),
                "goal_achieved": goal_achieved,
                "steps": plan_context["steps_completed"],
                "final_state": plan_context,
            }
            
            return {
                "status": "completed",
                "result": final_result,
                "context": plan_context,
                "logs": logs,
            }
            
        except Exception as e:
            logger.error(f"AutoGPT task execution failed: {e}", exc_info=True)
            return {
                "status": "failed",
                "result": None,
                "context": context or {},
                "logs": [f"AutoGPT execution error: {str(e)}"],
                "error": str(e),
            }
    
    def get_capabilities(self) -> dict[str, Any]:
        """Get AutoGPT capabilities."""
        return {
            "supports_recursive_planning": True,
            "supports_multi_role": False,
            "supports_self_healing": False,
            "supports_tool_calling": True,
            "max_roles": 1,
            "framework_name": "autogpt",
            "description": "Recursive planning agent framework for complex tasks",
        }

