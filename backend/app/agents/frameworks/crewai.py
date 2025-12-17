"""
CrewAI Framework Integration

CrewAI is a multi-agent framework for orchestrating role-playing, autonomous agents.
"""

import logging
from typing import Any

from app.agents.frameworks.base import BaseAgentFramework

logger = logging.getLogger(__name__)


class CrewAIFramework(BaseAgentFramework):
    """
    CrewAI framework wrapper.
    
    CrewAI specializes in:
    - Multi-agent collaboration
    - Role-based agent teams
    - Sequential and hierarchical task execution
    - Agent specialization
    """
    
    def __init__(self):
        """Initialize CrewAI framework."""
        super().__init__()
    
    def _check_availability(self) -> None:
        """Check if CrewAI is available."""
        try:
            import crewai
            self.is_available = True
            logger.info("CrewAI framework is available")
        except ImportError:
            logger.warning("CrewAI is not installed. Install with: pip install crewai")
            self.is_available = False
    
    def execute_task(
        self,
        task_type: str,
        input_data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute a task using CrewAI.
        
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
                "logs": ["CrewAI framework not available. Please install crewai package."],
                "error": "Framework not available",
            }
        
        try:
            from crewai import Agent, Crew, Task
            
            # Extract task configuration
            agents_config = input_data.get("agents", [])
            tasks_config = input_data.get("tasks", [])
            
            # Create agents
            agents = []
            for agent_config in agents_config:
                agent = Agent(
                    role=agent_config.get("role", "Agent"),
                    goal=agent_config.get("goal", ""),
                    backstory=agent_config.get("backstory", ""),
                    verbose=agent_config.get("verbose", True),
                    allow_delegation=agent_config.get("allow_delegation", False),
                )
                agents.append(agent)
            
            # Create tasks
            tasks = []
            for task_config in tasks_config:
                task = Task(
                    description=task_config.get("description", ""),
                    agent=agents[task_config.get("agent_index", 0)] if agents else None,
                    expected_output=task_config.get("expected_output", ""),
                )
                tasks.append(task)
            
            # Create crew and execute
            crew = Crew(
                agents=agents,
                tasks=tasks,
                verbose=input_data.get("verbose", True),
            )
            
            result = crew.kickoff()
            
            return {
                "status": "completed",
                "result": {
                    "output": str(result),
                    "agents_used": len(agents),
                    "tasks_completed": len(tasks),
                },
                "context": context or {},
                "logs": [
                    f"CrewAI execution started with {len(agents)} agents and {len(tasks)} tasks",
                    "Task execution completed successfully",
                ],
            }
            
        except Exception as e:
            logger.error(f"CrewAI task execution failed: {e}")
            return {
                "status": "failed",
                "result": None,
                "context": context or {},
                "logs": [f"CrewAI execution error: {str(e)}"],
                "error": str(e),
            }
    
    def get_capabilities(self) -> dict[str, Any]:
        """Get CrewAI capabilities."""
        return {
            "supports_recursive_planning": False,
            "supports_multi_role": True,
            "supports_self_healing": False,
            "supports_tool_calling": True,
            "max_roles": None,  # No limit
            "framework_name": "crewai",
            "description": "Multi-agent framework for role-based agent teams",
        }

