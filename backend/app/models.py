from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import EmailStr
from sqlalchemy import JSON, Column, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str = Field(default="")  # Empty for Supabase auth users
    workflows: list[Workflow] = Relationship(
        back_populates="owner", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    rag_indexes: list[RAGIndex] = Relationship(
        back_populates="owner", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    code_tools: list[CodeToolRegistry] = Relationship(
        back_populates="owner", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    code_sandboxes: list[CodeSandbox] = Relationship(
        back_populates="owner", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    api_keys: list[UserAPIKey] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    owned_teams: list[Team] = Relationship(back_populates="owner")
    team_memberships: list[TeamMember] = Relationship()
    sent_invitations: list[TeamInvitation] = Relationship()
    preferences: UserPreferences | None = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"uselist": False, "cascade": "all, delete-orphan"},
    )
    sessions: list[UserSession] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    login_history: list[LoginHistory] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


# ============================================================================
# USER PREFERENCES MODEL
# ============================================================================


class UserPreferences(SQLModel, table=True):
    """User preferences and settings"""

    __tablename__ = "user_preferences"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="user.id",
        nullable=False,
        unique=True,
        ondelete="CASCADE",
        index=True,
    )
    theme: str = Field(default="system", max_length=50)  # light, dark, system
    ui_density: str = Field(
        default="comfortable", max_length=50
    )  # comfortable, compact
    timezone: str = Field(default="UTC", max_length=100)
    language: str = Field(default="en", max_length=10)
    date_format: str = Field(default="YYYY-MM-DD", max_length=50)
    time_format: str = Field(default="24h", max_length=10)  # 12h, 24h
    bio: str | None = Field(default=None, max_length=500)
    company: str | None = Field(default=None, max_length=255)
    avatar_url: str | None = Field(default=None, max_length=1000)
    email_workflow_events: bool = Field(default=True)
    email_system_alerts: bool = Field(default=True)
    email_team_invitations: bool = Field(default=True)
    email_marketing: bool = Field(default=False)
    notification_frequency: str = Field(
        default="realtime", max_length=50
    )  # realtime, daily, weekly
    quiet_hours_start: str | None = Field(default=None, max_length=10)  # HH:MM format
    quiet_hours_end: str | None = Field(default=None, max_length=10)  # HH:MM format
    in_app_notifications: bool = Field(default=True)
    default_timeout: int = Field(default=300)  # seconds
    default_retry_policy: dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSONB)
    )
    auto_save_interval: int = Field(default=30)  # seconds
    auto_retry_on_failure: bool = Field(default=True)
    failure_notification_threshold: int = Field(default=1)
    analytics_enabled: bool = Field(default=True)
    error_reporting_enabled: bool = Field(default=True)
    two_factor_enabled: bool = Field(default=False)
    two_factor_secret: str | None = Field(default=None, max_length=255)
    two_factor_backup_codes: list[str] = Field(
        default_factory=list, sa_column=Column(JSONB)
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True))
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), onupdate=datetime.utcnow),
    )

    user: User | None = Relationship(back_populates="preferences")


class UserPreferencesUpdate(SQLModel):
    """Update user preferences request"""

    theme: str | None = None
    ui_density: str | None = None
    timezone: str | None = None
    language: str | None = None
    date_format: str | None = None
    time_format: str | None = None
    bio: str | None = None
    company: str | None = None
    avatar_url: str | None = None
    email_workflow_events: bool | None = None
    email_system_alerts: bool | None = None
    email_team_invitations: bool | None = None
    email_marketing: bool | None = None
    notification_frequency: str | None = None
    quiet_hours_start: str | None = None
    quiet_hours_end: str | None = None
    in_app_notifications: bool | None = None
    default_timeout: int | None = None
    default_retry_policy: dict[str, Any] | None = None
    auto_save_interval: int | None = None
    auto_retry_on_failure: bool | None = None
    failure_notification_threshold: int | None = None
    analytics_enabled: bool | None = None
    error_reporting_enabled: bool | None = None
    two_factor_enabled: bool | None = None
    two_factor_secret: str | None = None
    two_factor_backup_codes: list[str] | None = None


# ============================================================================
# USER SESSION AND LOGIN HISTORY MODELS
# ============================================================================


class UserSession(SQLModel, table=True):
    """User session tracking model"""

    __tablename__ = "user_session"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE", index=True
    )
    session_token: str = Field(unique=True, index=True, max_length=255)
    device_info: str | None = Field(default=None, max_length=255)
    ip_address: str | None = Field(default=None, max_length=255)
    user_agent: str | None = Field(default=None, max_length=500)
    location: str | None = Field(default=None, max_length=255)
    last_active_at: datetime = Field(
        default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True))
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True))
    )
    expires_at: datetime = Field(sa_column=Column(DateTime(timezone=True)))

    user: User | None = Relationship(back_populates="sessions")


class LoginHistory(SQLModel, table=True):
    """Login history tracking model"""

    __tablename__ = "login_history"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE", index=True
    )
    ip_address: str = Field(max_length=255)
    user_agent: str = Field(max_length=500)
    location: str | None = Field(default=None, max_length=255)
    success: bool = Field(default=True)
    failure_reason: str | None = Field(default=None, max_length=500)
    created_at: datetime = Field(
        default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True))
    )

    user: User | None = Relationship(back_populates="login_history")


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


# ============================================================================
# WORKFLOW MODELS
# ============================================================================


class WorkflowBase(SQLModel):
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    is_active: bool = True
    version: int = Field(default=1)
    trigger_config: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    graph_config: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))


class WorkflowCreate(WorkflowBase):
    pass


class WorkflowUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    is_active: bool | None = None
    trigger_config: dict[str, Any] | None = None
    graph_config: dict[str, Any] | None = None


class Workflow(WorkflowBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    owner: User | None = Relationship(back_populates="workflows")
    nodes: list[WorkflowNode] = Relationship(
        back_populates="workflow",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    executions: list[WorkflowExecution] = Relationship(
        back_populates="workflow",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    schedules: list[WorkflowSchedule] = Relationship(
        back_populates="workflow",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    webhook_subscriptions: list[WorkflowWebhookSubscription] = Relationship(
        back_populates="workflow",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class WorkflowPublic(WorkflowBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class WorkflowNode(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    workflow_id: uuid.UUID = Field(
        foreign_key="workflow.id", nullable=False, ondelete="CASCADE"
    )
    node_type: str = Field(
        max_length=100
    )  # trigger, ai_prompt, http_request, code, etc.
    node_id: str = Field(max_length=255)  # LangGraph node ID
    position_x: float = Field(default=0.0)
    position_y: float = Field(default=0.0)
    config: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))

    workflow: Workflow | None = Relationship(back_populates="nodes")


class WorkflowExecution(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    workflow_id: uuid.UUID = Field(
        foreign_key="workflow.id", nullable=False, ondelete="CASCADE"
    )
    workflow_version: int = Field(default=1)
    execution_id: str = Field(
        unique=True, index=True, max_length=255
    )  # Custom execution ID
    status: str = Field(
        max_length=50
    )  # running, completed, failed, paused, waiting_for_signal
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
    error_message: str | None = None
    current_node_id: str | None = Field(default=None, max_length=255)
    execution_state: dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSON)
    )
    retry_count: int = Field(default=0)
    next_retry_at: datetime | None = None

    workflow: Workflow | None = Relationship(back_populates="executions")
    logs: list[ExecutionLog] = Relationship(
        back_populates="execution",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    signals: list[WorkflowSignal] = Relationship(
        back_populates="execution",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class ExecutionLog(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    execution_id: uuid.UUID = Field(
        foreign_key="workflowexecution.id", nullable=False, ondelete="CASCADE"
    )
    node_id: str = Field(max_length=255)
    level: str = Field(max_length=20)  # info, error, debug, warning
    message: str = Field(max_length=5000)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    execution: WorkflowExecution | None = Relationship(back_populates="logs")


class WorkflowSchedule(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    workflow_id: uuid.UUID = Field(
        foreign_key="workflow.id", nullable=False, ondelete="CASCADE"
    )
    cron_expression: str = Field(max_length=100)
    is_active: bool = Field(default=True)
    next_run_at: datetime | None = None
    last_run_at: datetime | None = None

    workflow: Workflow | None = Relationship(back_populates="schedules")


class WorkflowSignal(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    execution_id: uuid.UUID = Field(
        foreign_key="workflowexecution.id", nullable=False, ondelete="CASCADE"
    )
    signal_type: str = Field(
        max_length=100
    )  # connector_ready, human_input, webhook, etc.
    signal_data: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    received_at: datetime = Field(default_factory=datetime.utcnow)
    processed: bool = Field(default=False)

    execution: WorkflowExecution | None = Relationship(back_populates="signals")


class WorkflowWebhookSubscription(SQLModel, table=True):
    """Webhook subscription for workflows (separate from connector webhooks)."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    workflow_id: uuid.UUID = Field(
        foreign_key="workflow.id", nullable=False, ondelete="CASCADE"
    )
    webhook_path: str = Field(max_length=500, index=True)
    secret: str | None = Field(default=None, max_length=255)
    headers: dict[str, str] = Field(default_factory=dict, sa_column=Column(JSONB))
    filters: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB))
    is_active: bool = Field(default=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    workflow: Workflow | None = Relationship(back_populates="webhook_subscriptions")


# ============================================================================
# CONNECTOR MODELS
# ============================================================================


class Connector(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    slug: str = Field(unique=True, index=True, max_length=100)
    name: str = Field(max_length=255)
    status: str = Field(max_length=50)  # draft, beta, stable, deprecated
    latest_version_id: uuid.UUID | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    # RBAC fields: owner_id=None means platform connector, owner_id=UUID means user-owned
    owner_id: uuid.UUID | None = Field(
        default=None, foreign_key="user.id", nullable=True, ondelete="CASCADE"
    )
    is_platform: bool = Field(
        default=True
    )  # True = available to all users, False = user-specific
    created_by: uuid.UUID | None = Field(
        default=None, foreign_key="user.id", nullable=True, ondelete="SET NULL"
    )

    versions: list[ConnectorVersion] = Relationship(
        back_populates="connector",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class ConnectorVersion(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    connector_id: uuid.UUID = Field(
        foreign_key="connector.id", nullable=False, ondelete="CASCADE"
    )
    version: str = Field(max_length=50)  # SemVer
    manifest: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB))
    wheel_url: str | None = Field(default=None, max_length=1000)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    connector: Connector | None = Relationship(back_populates="versions")
    webhook_subscriptions: list[WebhookSubscription] = Relationship(
        back_populates="connector_version",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class WebhookSubscription(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    connector_version_id: uuid.UUID = Field(
        foreign_key="connectorversion.id", nullable=False, ondelete="CASCADE"
    )
    trigger_id: str = Field(max_length=255)
    tenant_id: uuid.UUID = Field(nullable=False)
    endpoint_secret: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    connector_version: ConnectorVersion | None = Relationship(
        back_populates="webhook_subscriptions"
    )


# ============================================================================
# AGENT MODELS
# ============================================================================


class AgentTask(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    agent_framework: str = Field(max_length=100)  # AgentGPT, AutoGPT, MetaGPT, etc.
    task_type: str = Field(max_length=100)
    status: str = Field(max_length=50)  # running, completed, failed
    input_data: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    output_data: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
    error_message: str | None = None

    logs: list[AgentTaskLog] = Relationship(
        back_populates="task", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class AgentTaskLog(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    task_id: uuid.UUID = Field(
        foreign_key="agenttask.id", nullable=False, ondelete="CASCADE"
    )
    level: str = Field(max_length=20)  # info, error, debug, warning
    message: str = Field(max_length=5000)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    task: AgentTask | None = Relationship(back_populates="logs")


class AgentFrameworkConfig(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    framework: str = Field(unique=True, max_length=100)
    config: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    is_enabled: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AgentContextCache(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    agent_id: str = Field(index=True, max_length=255)
    context_key: str = Field(index=True, max_length=255)
    context_data: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    expires_at: datetime | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# RAG MODELS
# ============================================================================


class RAGIndex(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255)
    vector_db_type: str = Field(max_length=50)  # chromadb, milvus, weaviate, etc.
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)

    owner: User | None = Relationship(back_populates="rag_indexes")
    documents: list[RAGDocument] = Relationship(
        back_populates="index", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    queries: list[RAGQuery] = Relationship(
        back_populates="index", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class RAGDocument(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    index_id: uuid.UUID = Field(
        foreign_key="ragindex.id", nullable=False, ondelete="CASCADE"
    )
    content: str = Field(max_length=100000)
    document_metadata: dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSON)
    )
    embedding: list[float] | None = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    index: RAGIndex | None = Relationship(back_populates="documents")


class RAGQuery(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    index_id: uuid.UUID = Field(
        foreign_key="ragindex.id", nullable=False, ondelete="CASCADE"
    )
    query_text: str = Field(max_length=5000)
    results: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    latency_ms: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    index: RAGIndex | None = Relationship(back_populates="queries")


class RAGSwitchLog(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    query_id: uuid.UUID | None = Field(
        default=None, foreign_key="ragquery.id", ondelete="SET NULL"
    )
    routing_decision: str = Field(max_length=100)  # Which vector DB was chosen
    routing_reason: str = Field(max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class RAGFinetuneJob(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    index_id: uuid.UUID = Field(foreign_key="ragindex.id", nullable=False)
    status: str = Field(max_length=50)  # running, completed, failed
    config: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
    error_message: str | None = None


class RAGFinetuneDataset(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    job_id: uuid.UUID = Field(
        foreign_key="ragfinetunejob.id", nullable=False, ondelete="CASCADE"
    )
    dataset_url: str = Field(max_length=1000)
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# OCR MODELS
# ============================================================================


class OCRJob(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    document_url: str = Field(max_length=1000)
    engine: str = Field(max_length=100)  # DocTR, EasyOCR, PaddleOCR, etc.
    status: str = Field(max_length=50)  # running, completed, failed
    result: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
    error_message: str | None = None


class OCRDocument(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    job_id: uuid.UUID = Field(
        foreign_key="ocrjob.id", nullable=False, ondelete="CASCADE"
    )
    file_url: str = Field(max_length=1000)
    file_type: str = Field(max_length=50)  # pdf, image, etc.
    document_metadata: dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSON)
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)


class OCRResult(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    job_id: uuid.UUID = Field(
        foreign_key="ocrjob.id", nullable=False, ondelete="CASCADE"
    )
    extracted_text: str = Field(max_length=100000)
    structured_data: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))
    confidence_score: float | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# SCRAPING MODELS
# ============================================================================


class ScrapeJob(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    url: str = Field(max_length=2000)
    engine: str = Field(max_length=100)  # BeautifulSoup, Playwright, Scrapy, etc.
    proxy_id: str | None = Field(default=None, max_length=255)
    status: str = Field(max_length=50)  # running, completed, failed
    result: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
    error_message: str | None = None


class ScrapeResult(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    job_id: uuid.UUID = Field(
        foreign_key="scrapejob.id", nullable=False, ondelete="CASCADE"
    )
    content: str = Field(max_length=1000000)
    html: str | None = Field(default=None, max_length=10000000)
    result_metadata: dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSON)
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ProxyLog(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    ip_id: str = Field(index=True, max_length=255)
    agent_id: str | None = Field(default=None, max_length=255)
    domain_scraped: str = Field(index=True, max_length=255)
    status_code: int | None = None
    retry_count: int = Field(default=0)
    block_reason: str | None = Field(default=None, max_length=500)
    latency_ms: int = Field(default=0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class DomainProfile(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    domain: str = Field(unique=True, index=True, max_length=255)
    max_requests_per_hour: int = Field(default=60)
    requires_login: bool = Field(default=False)
    captcha_likelihood: str = Field(default="low", max_length=50)  # low, medium, high
    scroll_needed: bool = Field(default=False)
    idle_before_click: float = Field(default=2.0)
    config: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ContentChecksum(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    url: str = Field(index=True, max_length=2000)
    content_hash: str = Field(index=True, max_length=64)  # SHA256 hash
    last_scraped_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# BROWSER AUTOMATION MODELS
# ============================================================================


class BrowserSession(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    session_id: str = Field(unique=True, index=True, max_length=255)
    browser_tool: str = Field(
        max_length=100
    )  # Playwright, Puppeteer, Browserbase, etc.
    proxy_id: str | None = Field(default=None, max_length=255)
    status: str = Field(max_length=50)  # active, closed, error
    started_at: datetime = Field(default_factory=datetime.utcnow)
    closed_at: datetime | None = None

    actions: list[BrowserAction] = Relationship(
        back_populates="session",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class BrowserAction(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    session_id: uuid.UUID = Field(
        foreign_key="browsersession.id", nullable=False, ondelete="CASCADE"
    )
    action_type: str = Field(max_length=100)  # navigate, click, fill, screenshot, etc.
    action_data: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    result: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    session: BrowserSession | None = Relationship(back_populates="actions")


class ChangeDetection(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    url: str = Field(index=True, max_length=2000)
    diff_hash: str = Field(index=True, max_length=64)
    previous_content: str | None = Field(default=None, max_length=1000000)
    current_content: str | None = Field(default=None, max_length=1000000)
    detected_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# OSINT MODELS
# ============================================================================


class OSINTStream(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    platform: str = Field(max_length=100)  # Twitter, Reddit, Telegram, etc.
    keywords: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    engine: str = Field(max_length=100)  # Twint, Tweepy, Social-Listener, etc.
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    signals: list[OSINTSignal] = Relationship(
        back_populates="stream",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class OSINTAlert(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    stream_id: uuid.UUID | None = Field(
        default=None, foreign_key="osintstream.id", ondelete="SET NULL"
    )
    alert_type: str = Field(max_length=100)
    message: str = Field(max_length=5000)
    severity: str = Field(max_length=50)  # low, medium, high, critical
    is_read: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class OSINTSignal(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    stream_id: uuid.UUID = Field(
        foreign_key="osintstream.id", nullable=False, ondelete="CASCADE"
    )
    source: str = Field(max_length=100)
    author: str | None = Field(default=None, max_length=255)
    text: str = Field(max_length=10000)
    media: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    link: str | None = Field(default=None, max_length=2000)
    sentiment_score: float | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    stream: OSINTStream | None = Relationship(back_populates="signals")


# ============================================================================
# CUSTOM CODE MODELS
# ============================================================================


class CodeExecution(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    runtime: str = Field(max_length=100)  # E2B, WasmEdge, Bacalhau, etc.
    language: str = Field(max_length=50)  # python, javascript, typescript, bash
    code: str = Field(max_length=100000)
    input_data: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    output_data: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))
    status: str = Field(max_length=50)  # running, completed, failed
    exit_code: int | None = None
    duration_ms: int = Field(default=0)
    memory_mb: int | None = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
    error_message: str | None = None


class CodeToolRegistry(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tool_id: str = Field(unique=True, index=True, max_length=255)
    name: str = Field(max_length=255)
    version: str = Field(max_length=50)  # SemVer
    description: str | None = Field(default=None, max_length=1000)
    code: str = Field(max_length=100000)
    input_schema: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    output_schema: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    runtime: str = Field(max_length=100)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    usage_count: int = Field(default=0)
    is_deprecated: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    owner: User | None = Relationship(back_populates="code_tools")


class CodeSandbox(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255)
    runtime: str = Field(max_length=100)
    config: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)

    owner: User | None = Relationship(back_populates="code_sandboxes")


# ============================================================================
# TEAM MANAGEMENT MODELS
# ============================================================================


class Team(SQLModel, table=True):
    """Team/Organization model"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255, index=True)
    slug: str = Field(unique=True, index=True, max_length=100)
    description: str | None = Field(default=None, max_length=1000)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    settings: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB))

    owner: User | None = Relationship()
    members: list[TeamMember] = Relationship(
        back_populates="team", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    invitations: list[TeamInvitation] = Relationship(
        back_populates="team", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class TeamMember(SQLModel, table=True):
    """Team member with role"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    team_id: uuid.UUID = Field(
        foreign_key="team.id", nullable=False, ondelete="CASCADE"
    )
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    role: str = Field(default="member", max_length=50)  # owner, admin, member, viewer
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    invited_by: uuid.UUID | None = Field(
        default=None, foreign_key="user.id", nullable=True, ondelete="SET NULL"
    )

    team: Team | None = Relationship(back_populates="members")
    user: User | None = Relationship()


class TeamInvitation(SQLModel, table=True):
    """Team invitation"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    team_id: uuid.UUID = Field(
        foreign_key="team.id", nullable=False, ondelete="CASCADE"
    )
    email: EmailStr = Field(max_length=255, index=True)
    token: str = Field(unique=True, index=True, max_length=255)
    role: str = Field(default="member", max_length=50)  # admin, member, viewer
    invited_by: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    expires_at: datetime = Field(nullable=False)
    accepted_at: datetime | None = Field(default=None)
    revoked_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    team: Team | None = Relationship(back_populates="invitations")
    inviter: User | None = Relationship()


# ============================================================================
# EMAIL TEMPLATE MODELS
# ============================================================================


class EmailTemplate(SQLModel, table=True):
    """Email template for platform notifications"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(unique=True, index=True, max_length=255)
    slug: str = Field(unique=True, index=True, max_length=100)
    subject: str = Field(max_length=500)
    html_content: str = Field(sa_column=Column(JSON))  # Store as JSON for flexibility
    text_content: str | None = Field(default=None, sa_column=Column(JSON))
    category: str = Field(
        default="general", max_length=50
    )  # invitation, notification, workflow, system
    variables: dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSONB)
    )  # Available template variables
    is_active: bool = Field(default=True)
    is_system: bool = Field(default=False)  # System templates cannot be deleted
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: uuid.UUID | None = Field(
        default=None, foreign_key="user.id", nullable=True, ondelete="SET NULL"
    )


# ============================================================================
# TELEMETRY MODELS
# ============================================================================


class ModelCostLog(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    agent_id: uuid.UUID | None = Field(default=None, index=True)
    model: str = Field(index=True, max_length=100)  # gpt-4, claude-3, etc.
    tokens_input: int = Field(default=0)
    tokens_output: int = Field(default=0)
    usd_cost: float = Field(default=0.0)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)


class ToolUsageLog(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tool_id: str = Field(index=True, max_length=255)
    tool_type: str = Field(
        index=True, max_length=100
    )  # connector, ocr, scraping, browser, etc.
    status: str = Field(max_length=50)  # success, failed
    latency_ms: int = Field(default=0)
    error_message: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)


class EventLog(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    event_type: str = Field(
        index=True, max_length=100
    )  # workflow_started, agent_switch, etc.
    context: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    status: str = Field(max_length=50)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)


# ============================================================================
# NANGO OAUTH CONNECTION MODELS
# ============================================================================


class UserConnectorConnection(SQLModel, table=True):
    """
    Stores user's OAuth connections to connectors via Nango.
    Each user can have multiple connections to the same connector
    (e.g., multiple Gmail accounts, multiple Slack workspaces).
    """

    __tablename__ = "user_connector_connection"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    connector_id: uuid.UUID = Field(foreign_key="connector.id", index=True)

    # Nango connection identifier
    # Format: "{user_id}_{connector_id}_{instance_id}" or "{user_id}_{connector_id}"
    nango_connection_id: str = Field(index=True, unique=True, max_length=255)

    # Connection metadata
    status: str = Field(
        default="pending", max_length=50
    )  # pending, connected, disconnected, error
    connected_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )
    disconnected_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )
    last_synced_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )

    # Connector-specific config (e.g., which Gmail account, which Slack workspace)
    # Example: {"gmail_account": "work@gmail.com", "slack_workspace": "acme-corp"}
    config: dict[str, Any] | None = Field(default=None, sa_column=Column(JSONB))

    # Error tracking
    last_error: str | None = Field(default=None, max_length=1000)
    error_count: int = Field(default=0)

    created_at: datetime = Field(
        default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True))
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), onupdate=datetime.utcnow),
    )


# ============================================================================
# USER API KEYS MODELS
# ============================================================================


class UserAPIKeyBase(SQLModel):
    """Base model for user API keys."""

    service_name: str = Field(
        max_length=50, index=True
    )  # "openai", "anthropic", "twitter", etc.
    service_display_name: str = Field(
        max_length=100
    )  # "OpenAI", "Anthropic Claude", "Twitter"
    credential_type: str | None = Field(
        default=None, max_length=50
    )  # "api_key", "bearer_token", "oauth"
    is_active: bool = Field(default=True, index=True)
    last_used_at: datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=True))
    )


class UserAPIKeyCreate(SQLModel):
    """Create API key request."""

    service_name: str = Field(max_length=50)
    credential_type: str | None = Field(default=None, max_length=50)
    api_key: str = Field(min_length=1)  # Plain text key (will be encrypted)
    # For services with multiple credentials (e.g., Twitter)
    api_secret: str | None = Field(default=None)  # For Twitter API Key + Secret
    access_token: str | None = Field(default=None)  # For Twitter OAuth
    access_token_secret: str | None = Field(default=None)  # For Twitter OAuth


class UserAPIKeyUpdate(SQLModel):
    """Update API key request."""

    api_key: str | None = Field(default=None, min_length=1)
    api_secret: str | None = Field(default=None)
    access_token: str | None = Field(default=None)
    access_token_secret: str | None = Field(default=None)
    is_active: bool | None = Field(default=None)


class UserAPIKeyPublic(SQLModel):
    """Public API key response (masked)."""

    id: uuid.UUID
    service_name: str
    service_display_name: str
    credential_type: str | None
    masked_key: str  # Shows only last 4 characters
    is_active: bool
    last_used_at: datetime | None
    created_at: datetime
    updated_at: datetime


class UserAPIKey(UserAPIKeyBase, table=True):
    """User API keys for external services."""

    __tablename__ = "user_api_key"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)

    # Encrypted key storage (stored in Infisical, reference stored here)
    # Format: "infisical://users/{user_id}/api-keys/{service_name}/{credential_type}"
    infisical_path: str = Field(max_length=500)

    # Hash for verification (SHA256)
    key_hash: str = Field(max_length=64)

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow, sa_column=Column(DateTime(timezone=True))
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), onupdate=datetime.utcnow),
    )

    # Relationships
    user: User = Relationship(back_populates="api_keys")
