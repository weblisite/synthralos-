"""
Unit tests for Agent Router

Tests agent routing functionality including:
- Framework selection logic
- Task execution
- Context caching
- Framework availability checking
"""

import uuid
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.agents.router import (
    AgentRouter,
    FrameworkNotFoundError,
    TaskExecutionError,
)
from app.models import AgentFrameworkConfig, AgentTask


@pytest.fixture
def db_session():
    """Create an in-memory database session for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def agent_router():
    """Create an AgentRouter instance for testing."""
    return AgentRouter()


@pytest.fixture
def sample_framework_config(db_session):
    """Create a sample agent framework configuration."""
    config = AgentFrameworkConfig(
        id=uuid.uuid4(),
        framework="agentgpt",
        is_enabled=True,
        config={"api_key": "test-key"},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db_session.add(config)
    db_session.commit()
    db_session.refresh(config)
    return config


class TestAgentRouter:
    """Test suite for AgentRouter."""

    def test_select_framework_simple_agent(
        self, agent_router, db_session, sample_framework_config
    ):
        """Test framework selection for simple agent."""
        framework = agent_router.select_framework(
            db_session,
            task_type="simple_task",
            task_requirements={"agent_type": "simple"},
        )

        assert framework == "agentgpt"

    def test_select_framework_multi_role(
        self, agent_router, db_session, sample_framework_config
    ):
        """Test framework selection for multi-role agent."""
        # Add CrewAI config
        crewai_config = AgentFrameworkConfig(
            id=uuid.uuid4(),
            framework="crewai",
            is_enabled=True,
            config={},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db_session.add(crewai_config)
        db_session.commit()

        framework = agent_router.select_framework(
            db_session,
            task_type="multi_role_task",
            task_requirements={"agent_roles": 3},
        )

        assert framework == "crewai"

    def test_select_framework_self_healing(
        self, agent_router, db_session, sample_framework_config
    ):
        """Test framework selection for self-healing agent."""
        # Add Archon config
        archon_config = AgentFrameworkConfig(
            id=uuid.uuid4(),
            framework="archon",
            is_enabled=True,
            config={},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db_session.add(archon_config)
        db_session.commit()

        framework = agent_router.select_framework(
            db_session,
            task_type="self_healing_task",
            task_requirements={"agent_self_fix": True},
        )

        assert framework == "archon"

    def test_select_framework_not_found(self, agent_router, db_session):
        """Test framework selection when no frameworks are enabled."""
        with pytest.raises(FrameworkNotFoundError):
            agent_router.select_framework(
                db_session,
                task_type="test_task",
                task_requirements={},
            )

    def test_execute_task_success(
        self, agent_router, db_session, sample_framework_config
    ):
        """Test successful task execution."""
        with patch.object(
            agent_router,
            "_get_framework_handler",
            return_value=MagicMock(
                execute_task=MagicMock(
                    return_value={
                        "response": "Task completed",
                        "tool_calls": [],
                    }
                ),
                is_available=True,
            ),
        ):
            task = agent_router.execute_task(
                db_session,
                framework="agentgpt",
                task_type="test_task",
                input_data={"prompt": "Test"},
            )

            assert task is not None
            assert isinstance(task, AgentTask)
            assert task.status == "completed"
            assert task.agent_framework == "agentgpt"

    def test_execute_task_framework_not_found(self, agent_router, db_session):
        """Test task execution with non-existent framework."""
        with pytest.raises(FrameworkNotFoundError):
            agent_router.execute_task(
                db_session,
                framework="nonexistent",
                task_type="test_task",
                input_data={},
            )

    def test_execute_task_execution_error(
        self, agent_router, db_session, sample_framework_config
    ):
        """Test task execution failure."""
        with patch.object(
            agent_router,
            "_get_framework_handler",
            return_value=MagicMock(
                execute_task=MagicMock(side_effect=Exception("Execution error")),
                is_available=True,
            ),
        ):
            with pytest.raises(TaskExecutionError):
                agent_router.execute_task(
                    db_session,
                    framework="agentgpt",
                    task_type="test_task",
                    input_data={},
                )

    def test_cache_context(self, agent_router, db_session):
        """Test caching agent context."""
        agent_id = str(uuid.uuid4())
        context_data = {"key": "value", "timestamp": datetime.utcnow().isoformat()}

        cache = agent_router.cache_context(
            db_session,
            agent_id=agent_id,
            context_key="test_key",
            context_data=context_data,
        )

        assert cache is not None
        assert cache.agent_id == agent_id
        assert cache.context_key == "test_key"
        assert cache.context_data == context_data

    def test_get_cached_context(self, agent_router, db_session):
        """Test retrieving cached context."""
        agent_id = str(uuid.uuid4())
        context_data = {"key": "value"}

        # Cache context
        agent_router.cache_context(
            db_session,
            agent_id=agent_id,
            context_key="test_key",
            context_data=context_data,
        )

        # Retrieve cached context
        cached = agent_router.get_cached_context(
            db_session, agent_id=agent_id, context_key="test_key"
        )

        assert cached is not None
        assert cached == context_data

    def test_get_cached_context_expired(self, agent_router, db_session):
        """Test retrieving expired cached context."""
        agent_id = str(uuid.uuid4())
        context_data = {"key": "value"}

        # Cache context with expiration
        agent_router.cache_context(
            db_session,
            agent_id=agent_id,
            context_key="test_key",
            context_data=context_data,
            expires_in_seconds=-1,  # Already expired
        )

        # Retrieve cached context (should return None)
        cached = agent_router.get_cached_context(
            db_session, agent_id=agent_id, context_key="test_key"
        )

        assert cached is None

    def test_clear_context_cache(self, agent_router, db_session):
        """Test clearing cached context."""
        agent_id = str(uuid.uuid4())
        context_data = {"key": "value"}

        # Cache context
        agent_router.cache_context(
            db_session,
            agent_id=agent_id,
            context_key="test_key",
            context_data=context_data,
        )

        # Clear cache
        agent_router.clear_context_cache(db_session, agent_id=agent_id)

        # Verify cache is cleared
        cached = agent_router.get_cached_context(
            db_session, agent_id=agent_id, context_key="test_key"
        )

        assert cached is None
