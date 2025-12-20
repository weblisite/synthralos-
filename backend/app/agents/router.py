"""
Agent Router Service

Routes agent tasks to appropriate frameworks based on task requirements.
Handles framework selection, task execution, and context caching.
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Any

from sqlmodel import Session, select

logger = logging.getLogger(__name__)

from app.agents.frameworks import (
    AgentGPTFramework,
    ArchonFramework,
    AutoGenFramework,
    AutoGPTFramework,
    BaseAgentFramework,
    CamelAIFramework,
    CrewAIFramework,
    KUSHAIFramework,
    KyroFramework,
    MetaGPTFramework,
    RionaFramework,
    SwarmFramework,
)
from app.models import (
    AgentContextCache,
    AgentFrameworkConfig,
    AgentTask,
    AgentTaskLog,
)


class AgentRouterError(Exception):
    """Base exception for agent router errors."""

    pass


class FrameworkNotFoundError(AgentRouterError):
    """Agent framework not found."""

    pass


class TaskExecutionError(AgentRouterError):
    """Task execution failed."""

    pass


class AgentRouter:
    """
    Agent router service.

    Routes agent tasks to appropriate frameworks based on:
    - Task type
    - Framework capabilities
    - User preferences
    - Framework availability
    """

    def __init__(self):
        """Initialize agent router."""
        self._framework_handlers: dict[str, BaseAgentFramework] = {}
        self._context_cache: dict[str, dict[str, Any]] = {}
        self._initialize_frameworks()

    def select_framework(
        self,
        session: Session,
        task_type: str,
        task_requirements: dict[str, Any] | None = None,
    ) -> str:
        """
        Select appropriate agent framework for a task.

        Routing Logic:
        - agent_type = simple → AgentGPT
        - recursive_planning = true → AutoGPT/BabyAGI
        - agent_roles > 1 → MetaGPT/CrewAI
        - agent_self_fix = true → Archon
        - user_prefers_copilot_ui = true → ag-ui interface

        Args:
            session: Database session
            task_type: Type of task
            task_requirements: Optional task requirements dictionary

        Returns:
            Framework name (e.g., "agentgpt", "autogpt", "metagpt")
        """
        if not task_requirements:
            task_requirements = {}

        # Check for explicit framework preference
        preferred_framework = task_requirements.get("framework")
        if preferred_framework:
            # Verify framework is enabled
            config = session.exec(
                select(AgentFrameworkConfig).where(
                    AgentFrameworkConfig.framework == preferred_framework
                )
            ).first()
            if config and config.is_enabled:
                return preferred_framework

        # Routing logic based on task requirements
        agent_type = task_requirements.get("agent_type", "simple")
        recursive_planning = task_requirements.get("recursive_planning", False)
        agent_roles = task_requirements.get("agent_roles", 1)
        agent_self_fix = task_requirements.get("agent_self_fix", False)
        user_prefers_copilot_ui = task_requirements.get(
            "user_prefers_copilot_ui", False
        )

        # Multi-role agents
        if agent_roles > 1:
            # Check if MetaGPT or CrewAI is available
            metagpt_config = session.exec(
                select(AgentFrameworkConfig).where(
                    AgentFrameworkConfig.framework == "metagpt",
                    AgentFrameworkConfig.is_enabled == True,
                )
            ).first()
            if metagpt_config:
                return "metagpt"

            crewai_config = session.exec(
                select(AgentFrameworkConfig).where(
                    AgentFrameworkConfig.framework == "crewai",
                    AgentFrameworkConfig.is_enabled == True,
                )
            ).first()
            if crewai_config:
                return "crewai"

        # Self-healing agents
        if agent_self_fix:
            archon_config = session.exec(
                select(AgentFrameworkConfig).where(
                    AgentFrameworkConfig.framework == "archon",
                    AgentFrameworkConfig.is_enabled == True,
                )
            ).first()
            if archon_config:
                return "archon"

        # Recursive planning agents
        if recursive_planning:
            autogpt_config = session.exec(
                select(AgentFrameworkConfig).where(
                    AgentFrameworkConfig.framework == "autogpt",
                    AgentFrameworkConfig.is_enabled == True,
                )
            ).first()
            if autogpt_config:
                return "autogpt"

            babyagi_config = session.exec(
                select(AgentFrameworkConfig).where(
                    AgentFrameworkConfig.framework == "babyagi",
                    AgentFrameworkConfig.is_enabled == True,
                )
            ).first()
            if babyagi_config:
                return "babyagi"

        # Copilot UI preference
        if user_prefers_copilot_ui:
            # Use ag-ui compatible framework
            # For now, default to agentgpt
            agentgpt_config = session.exec(
                select(AgentFrameworkConfig).where(
                    AgentFrameworkConfig.framework == "agentgpt",
                    AgentFrameworkConfig.is_enabled == True,
                )
            ).first()
            if agentgpt_config:
                return "agentgpt"

        # Default to simple agent framework
        agentgpt_config = session.exec(
            select(AgentFrameworkConfig).where(
                AgentFrameworkConfig.framework == "agentgpt",
                AgentFrameworkConfig.is_enabled == True,
            )
        ).first()
        if agentgpt_config:
            return "agentgpt"

        # Fallback: return first enabled framework
        fallback_config = session.exec(
            select(AgentFrameworkConfig).where(
                AgentFrameworkConfig.is_enabled == True,
            )
        ).first()
        if fallback_config:
            return fallback_config.framework

        raise FrameworkNotFoundError("No enabled agent framework found")

    def execute_task(
        self,
        session: Session,
        framework: str,
        task_type: str,
        input_data: dict[str, Any],
        agent_id: str | None = None,
    ) -> AgentTask:
        """
        Execute an agent task using the specified framework.

        Args:
            session: Database session
            framework: Agent framework name
            task_type: Type of task
            input_data: Task input data
            agent_id: Optional agent ID for context caching

        Returns:
            AgentTask instance

        Raises:
            FrameworkNotFoundError: If framework not found or disabled
            TaskExecutionError: If task execution fails
        """
        # Verify framework is enabled
        framework_config = session.exec(
            select(AgentFrameworkConfig).where(
                AgentFrameworkConfig.framework == framework,
                AgentFrameworkConfig.is_enabled == True,
            )
        ).first()

        if not framework_config:
            raise FrameworkNotFoundError(
                f"Framework '{framework}' not found or disabled"
            )

        # Create task record
        task = AgentTask(
            agent_framework=framework,
            task_type=task_type,
            status="running",
            input_data=input_data,
            started_at=datetime.utcnow(),
        )
        session.add(task)
        session.commit()
        session.refresh(task)

        # Get cached context if agent_id provided
        cached_context = None
        if agent_id:
            cached_context = self.get_cached_context(session, agent_id)

        try:
            # Import Langfuse for tracing
            from app.observability.langfuse import default_langfuse_client

            # Create Langfuse trace for agent task execution
            user_id = str(agent_id) if agent_id else None
            trace = default_langfuse_client.trace(
                name=f"agent_task_{task_type}",
                user_id=user_id,
                metadata={
                    "framework": framework,
                    "task_type": task_type,
                    "task_id": str(task.id),
                },
            )

            # Get framework handler
            handler = self._get_framework_handler(framework)

            # Prepare execution context
            execution_context = {
                "task_id": str(task.id),
                "framework": framework,
                "task_type": task_type,
                "input_data": input_data,
                "cached_context": cached_context,
                "framework_config": framework_config.config,
            }

            # Execute task using framework handler
            result = self._execute_with_framework(handler, execution_context)

            # Log span for framework execution
            if trace:
                trace_id = getattr(trace, "id", None) or str(trace)
                default_langfuse_client.span(
                    trace_id=trace_id,
                    name=f"framework_execution_{framework}",
                    metadata={
                        "framework": framework,
                        "status": result.get("status", "unknown"),
                    },
                )

            # Update task with result
            # Framework returns dict with status, result, context, logs
            if isinstance(result, dict):
                # Extract status from framework result
                framework_status = result.get("status", "completed")
                if framework_status == "failed":
                    task.status = "failed"
                    task.error_message = result.get("error", "Task execution failed")
                else:
                    task.status = "completed"

                # Store full result in output_data
                task.output_data = result.get("result", result)
            else:
                # Fallback for unexpected result format
                task.status = "completed"
                task.output_data = result

            task.completed_at = datetime.utcnow()

            # Cache context if agent_id provided
            if agent_id and result.get("context"):
                self.cache_context(
                    session,
                    agent_id=agent_id,
                    context_key="latest",
                    context_data=result.get("context"),
                )

            session.add(task)
            session.commit()
            session.refresh(task)

            # Log success
            self._log_task_event(
                session,
                task.id,
                "info",
                f"Task completed successfully using framework '{framework}'",
            )

            return task

        except Exception as e:
            # Update task with error
            task.status = "failed"
            task.error_message = str(e)
            task.completed_at = datetime.utcnow()
            session.add(task)
            session.commit()
            session.refresh(task)

            # Log error
            self._log_task_event(
                session,
                task.id,
                "error",
                f"Task failed: {str(e)}",
            )

            raise TaskExecutionError(f"Task execution failed: {e}")

    def _initialize_frameworks(self) -> None:
        """Initialize framework handlers."""
        # Initialize all available frameworks
        framework_classes = {
            "agentgpt": AgentGPTFramework,
            "autogpt": AutoGPTFramework,
            "metagpt": MetaGPTFramework,
            "autogen": AutoGenFramework,
            "archon": ArchonFramework,
            "crewai": CrewAIFramework,
            "riona": RionaFramework,
            "kyro": KyroFramework,
            "kush": KUSHAIFramework,
            "camel": CamelAIFramework,
            "swarm": SwarmFramework,
        }

        for framework_name, framework_class in framework_classes.items():
            try:
                handler = framework_class()
                if handler.is_available:
                    self._framework_handlers[framework_name] = handler
                    logger.info(f"Initialized {framework_name} framework")
            except Exception as e:
                # Framework initialization failed, skip it
                logger.warning(f"Failed to initialize {framework_name}: {e}")
                pass

    def _get_framework_handler(self, framework: str) -> BaseAgentFramework:
        """
        Get handler for a specific framework.

        Args:
            framework: Framework name

        Returns:
            Framework handler instance

        Raises:
            FrameworkNotFoundError: If framework not found
        """
        if framework not in self._framework_handlers:
            raise FrameworkNotFoundError(
                f"Framework '{framework}' not found or not available"
            )

        return self._framework_handlers[framework]

    def _execute_with_framework(
        self,
        handler: BaseAgentFramework,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Execute task using framework handler.

        Args:
            handler: Framework handler instance
            context: Execution context

        Returns:
            Execution result
        """
        return handler.execute_task(
            task_type=context.get("task_type", "unknown"),
            input_data=context.get("input_data", {}),
            context=context.get("cached_context"),
        )

    def cache_context(
        self,
        session: Session,
        agent_id: str,
        context_key: str,
        context_data: dict[str, Any],
        expires_in_seconds: int | None = None,
    ) -> AgentContextCache:
        """
        Cache agent context for later retrieval.

        Args:
            session: Database session
            agent_id: Agent ID
            context_key: Context key
            context_data: Context data to cache
            expires_in_seconds: Optional expiration time

        Returns:
            AgentContextCache instance
        """
        expires_at = None
        if expires_in_seconds:
            expires_at = datetime.utcnow() + timedelta(seconds=expires_in_seconds)

        # Check if context already exists
        existing = session.exec(
            select(AgentContextCache).where(
                AgentContextCache.agent_id == agent_id,
                AgentContextCache.context_key == context_key,
            )
        ).first()

        if existing:
            # Update existing context
            existing.context_data = context_data
            existing.expires_at = expires_at
            session.add(existing)
            session.commit()
            session.refresh(existing)
            return existing

        # Create new context cache
        context_cache = AgentContextCache(
            agent_id=agent_id,
            context_key=context_key,
            context_data=context_data,
            expires_at=expires_at,
        )
        session.add(context_cache)
        session.commit()
        session.refresh(context_cache)

        return context_cache

    def get_cached_context(
        self,
        session: Session,
        agent_id: str,
        context_key: str = "latest",
    ) -> dict[str, Any] | None:
        """
        Retrieve cached agent context.

        Args:
            session: Database session
            agent_id: Agent ID
            context_key: Context key (defaults to "latest")

        Returns:
            Cached context data or None if not found/expired
        """
        context_cache = session.exec(
            select(AgentContextCache).where(
                AgentContextCache.agent_id == agent_id,
                AgentContextCache.context_key == context_key,
            )
        ).first()

        if not context_cache:
            return None

        # Check expiration
        if context_cache.expires_at and context_cache.expires_at < datetime.utcnow():
            # Expired, delete and return None
            session.delete(context_cache)
            session.commit()
            return None

        return context_cache.context_data

    def clear_context_cache(
        self,
        session: Session,
        agent_id: str,
        context_key: str | None = None,
    ) -> None:
        """
        Clear cached context for an agent.

        Args:
            session: Database session
            agent_id: Agent ID
            context_key: Optional context key (clears all if None)
        """
        if context_key:
            context_cache = session.exec(
                select(AgentContextCache).where(
                    AgentContextCache.agent_id == agent_id,
                    AgentContextCache.context_key == context_key,
                )
            ).first()
            if context_cache:
                session.delete(context_cache)
                session.commit()
        else:
            # Clear all contexts for agent
            contexts = session.exec(
                select(AgentContextCache).where(
                    AgentContextCache.agent_id == agent_id,
                )
            ).all()
            for context in contexts:
                session.delete(context)
            session.commit()

    def _log_task_event(
        self,
        session: Session,
        task_id: uuid.UUID,
        level: str,
        message: str,
    ) -> AgentTaskLog:
        """
        Log an event for an agent task.

        Args:
            session: Database session
            task_id: Task ID
            level: Log level (info, error, debug, warning)
            message: Log message

        Returns:
            AgentTaskLog instance
        """
        log = AgentTaskLog(
            task_id=task_id,
            level=level,
            message=message,
            timestamp=datetime.utcnow(),
        )
        session.add(log)
        session.commit()
        session.refresh(log)
        return log

    def get_task_status(
        self,
        session: Session,
        task_id: uuid.UUID,
    ) -> dict[str, Any]:
        """
        Get status and details of an agent task.

        Args:
            session: Database session
            task_id: Task ID

        Returns:
            Task status dictionary
        """
        task = session.get(AgentTask, task_id)
        if not task:
            raise TaskExecutionError(f"Task {task_id} not found")

        # Get logs
        logs = session.exec(
            select(AgentTaskLog)
            .where(AgentTaskLog.task_id == task_id)
            .order_by(AgentTaskLog.timestamp.asc())
        ).all()

        duration_ms = None
        if task.completed_at:
            duration_ms = int(
                (task.completed_at - task.started_at).total_seconds() * 1000
            )

        return {
            "id": str(task.id),
            "agent_framework": task.agent_framework,
            "task_type": task.task_type,
            "status": task.status,
            "started_at": task.started_at.isoformat(),
            "completed_at": task.completed_at.isoformat()
            if task.completed_at
            else None,
            "duration_ms": duration_ms,
            "error_message": task.error_message,
            "input_data": task.input_data,
            "output_data": task.output_data,
            "logs": [
                {
                    "level": log.level,
                    "message": log.message,
                    "timestamp": log.timestamp.isoformat(),
                }
                for log in logs
            ],
        }

    def register_framework_handler(
        self,
        framework: str,
        handler: Any,
    ) -> None:
        """
        Register a framework handler.

        Args:
            framework: Framework name
            handler: Handler object or function
        """
        self._framework_handlers[framework] = handler


# Default agent router instance
default_agent_router = AgentRouter()
