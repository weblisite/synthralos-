"""
User Connector Connection Model

Stores user's OAuth connections to connectors via Nango.
Each user can have multiple connections to the same connector
(e.g., multiple Gmail accounts, multiple Slack workspaces).
"""

from sqlmodel import SQLModel, Field, Relationship, Column, JSONB
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import DateTime


class UserConnectorConnection(SQLModel, table=True):
    """
    Stores user's OAuth connections to connectors via Nango.
    """
    __tablename__ = "user_connector_connection"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    connector_id: UUID = Field(foreign_key="connector.id", index=True)
    
    # Nango connection identifier
    # Format: "{user_id}_{connector_id}_{instance_id}" or "{user_id}_{connector_id}"
    nango_connection_id: str = Field(index=True, unique=True)
    
    # Connection metadata
    status: str = Field(default="pending")  # pending, connected, disconnected, error
    connected_at: Optional[datetime] = None
    disconnected_at: Optional[datetime] = None
    last_synced_at: Optional[datetime] = None
    
    # Connector-specific config (e.g., which Gmail account, which Slack workspace)
    # Example: {"gmail_account": "work@gmail.com", "slack_workspace": "acme-corp"}
    config: Optional[dict] = Field(default=None, sa_column=Column(JSONB))
    
    # Error tracking
    last_error: Optional[str] = None
    error_count: int = Field(default=0)
    
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True))
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), onupdate=datetime.utcnow)
    )
    
    # Relationships (optional, if you have User and Connector models)
    # user: Optional["User"] = Relationship()
    # connector: Optional["Connector"] = Relationship()


