# Sub-Workflow System - Architecture & Implementation Plan

**Date:** December 20, 2025
**Status:** Design Phase
**Priority:** High
**Estimated Effort:** 2-3 days

---

## 📋 Overview

The sub-workflow system enables workflows to call other workflows as nodes, creating nested workflow execution. This allows for:
- **Workflow Reusability**: Create reusable workflow components
- **Modularity**: Break complex workflows into smaller, manageable pieces
- **Composition**: Build complex automations by combining simpler workflows
- **Maintainability**: Update shared logic in one place

---

## 🎯 Requirements

### Functional Requirements

1. **Sub-Workflow Node Type**
   - New node type: `sub_workflow`
   - Can be added to any workflow via NodePalette
   - Configurable to select target workflow

2. **Workflow Selection**
   - UI to browse and select available workflows
   - Filter by name, owner, status
   - Show workflow details (name, description, version)

3. **Input/Output Mapping**
   - Map parent workflow data to child workflow inputs
   - Map child workflow outputs back to parent workflow
   - Support for field mapping (e.g., `parent.output.email` → `child.input.email`)

4. **Execution Management**
   - Execute child workflow asynchronously
   - Track child execution status
   - Handle child workflow failures
   - Support timeout configuration

5. **Context Passing**
   - Pass execution context (user_id, execution_id, etc.)
   - Support for nested execution tracking (parent → child → grandchild)
   - Maximum nesting depth limit (e.g., 5 levels)

6. **Error Handling**
   - Handle child workflow failures gracefully
   - Retry logic for failed sub-workflows
   - Error propagation to parent workflow

### Non-Functional Requirements

1. **Performance**
   - Sub-workflow execution should not block parent workflow
   - Support for parallel sub-workflow execution
   - Efficient state management

2. **Security**
   - Users can only select workflows they have access to
   - Respect workflow ownership and permissions
   - Audit logging for sub-workflow calls

3. **Observability**
   - Track sub-workflow execution in parent execution logs
   - Show nested execution tree in UI
   - Support for execution history queries

---

## 🏗️ Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────────┐
│                    Parent Workflow                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐        │
│  │ Trigger  │→ │   Node   │→ │  Sub-Workflow    │        │
│  │          │  │          │  │     Node         │        │
│  └──────────┘  └──────────┘  │  ┌────────────┐  │        │
│                                │  │ Workflow   │  │        │
│                                │  │ Selection  │  │        │
│                                │  │ Input Map  │  │        │
│                                │  │ Output Map │  │        │
│                                │  └────────────┘  │        │
│                                └────────┬─────────┘        │
│                                         │                   │
└─────────────────────────────────────────┼───────────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Child Workflow                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │ Trigger  │→ │   Node   │→ │   Node   │                 │
│  │          │  │          │  │          │                 │
│  └──────────┘  └──────────┘  └──────────┘                 │
│                                                              │
│  Execution Context:                                          │
│  - parent_execution_id                                       │
│  - parent_node_id                                           │
│  - nesting_depth                                            │
└──────────────────────────────────────────────────────────────┘
```

### Component Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                         Frontend                              │
├──────────────────────────────────────────────────────────────┤
│  SubWorkflowNode.tsx          NodeConfigPanel.tsx            │
│  - Visual node                - Workflow selector             │
│  - Icon/logo                  - Input/output mapping UI      │
│                               - Execution status display      │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                         Backend API                          │
├──────────────────────────────────────────────────────────────┤
│  /api/v1/workflows/{id}/run                                  │
│  - Execute workflow                                          │
│  - Support parent_execution_id parameter                     │
│                                                              │
│  /api/v1/workflows/list                                      │
│  - List available workflows                                  │
│  - Filter by user access                                     │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                    Workflow Engine                            │
├──────────────────────────────────────────────────────────────┤
│  WorkflowEngine                                              │
│  - create_execution()                                        │
│  - execute_node()                                            │
│  - handle_sub_workflow_node()  ← NEW                        │
│                                                              │
│  SubWorkflowExecutor          ← NEW                          │
│  - execute_sub_workflow()                                   │
│  - map_inputs()                                             │
│  - map_outputs()                                             │
│  - track_execution()                                         │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                      Database Schema                         │
├──────────────────────────────────────────────────────────────┤
│  WorkflowExecution                                           │
│  - parent_execution_id (FK)    ← NEW                         │
│  - parent_node_id              ← NEW                         │
│  - nesting_depth               ← NEW                         │
│                                                              │
│  SubWorkflowCall              ← NEW                          │
│  - parent_execution_id                                        │
│  - child_execution_id                                         │
│  - parent_node_id                                             │
│  - input_mapping                                              │
│  - output_mapping                                             │
│  - status                                                     │
│  - started_at                                                 │
│  - completed_at                                               │
└──────────────────────────────────────────────────────────────┘
```

---

## 📊 Database Schema Changes

### 1. Update `WorkflowExecution` Table

```sql
ALTER TABLE workflowexecution
ADD COLUMN parent_execution_id UUID REFERENCES workflowexecution(id) ON DELETE SET NULL,
ADD COLUMN parent_node_id VARCHAR(255),
ADD COLUMN nesting_depth INTEGER DEFAULT 0;

CREATE INDEX idx_workflowexecution_parent ON workflowexecution(parent_execution_id);
CREATE INDEX idx_workflowexecution_nesting ON workflowexecution(nesting_depth);
```

### 2. Create `SubWorkflowCall` Table

```sql
CREATE TABLE subworkflowcall (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_execution_id UUID NOT NULL REFERENCES workflowexecution(id) ON DELETE CASCADE,
    child_execution_id UUID NOT NULL REFERENCES workflowexecution(id) ON DELETE CASCADE,
    parent_node_id VARCHAR(255) NOT NULL,
    input_mapping JSONB NOT NULL DEFAULT '{}',
    output_mapping JSONB NOT NULL DEFAULT '{}',
    status VARCHAR(50) NOT NULL DEFAULT 'pending', -- pending, running, completed, failed
    started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_subworkflowcall_parent ON subworkflowcall(parent_execution_id);
CREATE INDEX idx_subworkflowcall_child ON subworkflowcall(child_execution_id);
CREATE INDEX idx_subworkflowcall_status ON subworkflowcall(status);
```

---

## 🔧 Implementation Plan

### Phase 1: Database & Models (Day 1 - Morning)

#### 1.1 Create Alembic Migration

**File:** `backend/app/alembic/versions/XXXX_add_sub_workflow_support.py`

```python
"""Add sub-workflow support

Revision ID: add_sub_workflow_support
Revises: <previous_revision>
Create Date: 2025-12-20

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'add_sub_workflow_support'
down_revision = '<previous_revision>'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add columns to WorkflowExecution
    op.add_column('workflowexecution',
        sa.Column('parent_execution_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('workflowexecution',
        sa.Column('parent_node_id', sa.String(255), nullable=True))
    op.add_column('workflowexecution',
        sa.Column('nesting_depth', sa.Integer(), nullable=False, server_default='0'))

    # Create foreign key
    op.create_foreign_key(
        'fk_workflowexecution_parent',
        'workflowexecution', 'workflowexecution',
        ['parent_execution_id'], ['id'],
        ondelete='SET NULL'
    )

    # Create indexes
    op.create_index('ix_workflowexecution_parent', 'workflowexecution', ['parent_execution_id'])
    op.create_index('ix_workflowexecution_nesting', 'workflowexecution', ['nesting_depth'])

    # Create SubWorkflowCall table
    op.create_table(
        'subworkflowcall',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('parent_execution_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('child_execution_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('parent_node_id', sa.String(255), nullable=False),
        sa.Column('input_mapping', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('output_mapping', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # Create foreign keys
    op.create_foreign_key(
        'fk_subworkflowcall_parent',
        'subworkflowcall', 'workflowexecution',
        ['parent_execution_id'], ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'fk_subworkflowcall_child',
        'subworkflowcall', 'workflowexecution',
        ['child_execution_id'], ['id'],
        ondelete='CASCADE'
    )

    # Create indexes
    op.create_index('ix_subworkflowcall_parent', 'subworkflowcall', ['parent_execution_id'])
    op.create_index('ix_subworkflowcall_child', 'subworkflowcall', ['child_execution_id'])
    op.create_index('ix_subworkflowcall_status', 'subworkflowcall', ['status'])

def downgrade() -> None:
    op.drop_table('subworkflowcall')
    op.drop_index('ix_workflowexecution_nesting', 'workflowexecution')
    op.drop_index('ix_workflowexecution_parent', 'workflowexecution')
    op.drop_constraint('fk_workflowexecution_parent', 'workflowexecution', type_='foreignkey')
    op.drop_column('workflowexecution', 'nesting_depth')
    op.drop_column('workflowexecution', 'parent_node_id')
    op.drop_column('workflowexecution', 'parent_execution_id')
```

#### 1.2 Update Models

**File:** `backend/app/models.py`

```python
# Add to WorkflowExecution class
class WorkflowExecution(SQLModel, table=True):
    # ... existing fields ...

    # Sub-workflow support
    parent_execution_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="workflowexecution.id",
        nullable=True,
        ondelete="SET NULL"
    )
    parent_node_id: str | None = Field(default=None, max_length=255)
    nesting_depth: int = Field(default=0)

    # Relationships
    parent_execution: "WorkflowExecution" | None = Relationship(
        back_populates="child_executions",
        sa_relationship_kwargs={
            "remote_side": "WorkflowExecution.id",
            "foreign_keys": "WorkflowExecution.parent_execution_id"
        }
    )
    child_executions: list["WorkflowExecution"] = Relationship(
        back_populates="parent_execution"
    )
    sub_workflow_calls: list["SubWorkflowCall"] = Relationship(
        back_populates="parent_execution",
        cascade_delete=True
    )

# New model
class SubWorkflowCall(SQLModel, table=True):
    """Tracks sub-workflow calls from parent workflows."""
    __tablename__ = "subworkflowcall"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    parent_execution_id: uuid.UUID = Field(
        foreign_key="workflowexecution.id",
        nullable=False,
        ondelete="CASCADE"
    )
    child_execution_id: uuid.UUID = Field(
        foreign_key="workflowexecution.id",
        nullable=False,
        ondelete="CASCADE"
    )
    parent_node_id: str = Field(max_length=255, nullable=False)
    input_mapping: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB)
    )
    output_mapping: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSONB)
    )
    status: str = Field(
        max_length=50,
        default="pending"
    )  # pending, running, completed, failed
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
    error_message: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), onupdate=datetime.utcnow)
    )

    # Relationships
    parent_execution: WorkflowExecution | None = Relationship(
        back_populates="sub_workflow_calls",
        sa_relationship_kwargs={
            "foreign_keys": "SubWorkflowCall.parent_execution_id"
        }
    )
    child_execution: WorkflowExecution | None = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "SubWorkflowCall.child_execution_id"
        }
    )
```

---

### Phase 2: Backend - Sub-Workflow Executor (Day 1 - Afternoon)

#### 2.1 Create SubWorkflowExecutor Service

**File:** `backend/app/workflows/sub_workflow_executor.py` (NEW)

```python
"""
Sub-Workflow Executor

Handles execution of sub-workflows from parent workflows.
"""

import logging
import uuid
from datetime import datetime
from typing import Any

from sqlmodel import Session, select

from app.models import (
    ExecutionLog,
    SubWorkflowCall,
    Workflow,
    WorkflowExecution,
)
from app.workflows.engine import WorkflowEngine, WorkflowNotFoundError

logger = logging.getLogger(__name__)

# Maximum nesting depth to prevent infinite recursion
MAX_NESTING_DEPTH = 5


class SubWorkflowExecutorError(Exception):
    """Base exception for sub-workflow executor errors."""
    pass


class MaxNestingDepthExceededError(SubWorkflowExecutorError):
    """Maximum nesting depth exceeded."""
    pass


class SubWorkflowExecutor:
    """Executes sub-workflows from parent workflows."""

    def __init__(self, workflow_engine: WorkflowEngine):
        """
        Initialize sub-workflow executor.

        Args:
            workflow_engine: WorkflowEngine instance
        """
        self.workflow_engine = workflow_engine

    def execute_sub_workflow(
        self,
        session: Session,
        parent_execution: WorkflowExecution,
        parent_node_id: str,
        child_workflow_id: uuid.UUID,
        input_mapping: dict[str, Any],
        timeout_seconds: int = 300,
    ) -> SubWorkflowCall:
        """
        Execute a sub-workflow from a parent workflow.

        Args:
            session: Database session
            parent_execution: Parent workflow execution
            parent_node_id: ID of the parent node calling the sub-workflow
            child_workflow_id: ID of the child workflow to execute
            input_mapping: Mapping of parent data to child inputs
            timeout_seconds: Timeout for sub-workflow execution

        Returns:
            SubWorkflowCall instance

        Raises:
            MaxNestingDepthExceededError: If nesting depth exceeds maximum
            WorkflowNotFoundError: If child workflow not found
        """
        # Check nesting depth
        if parent_execution.nesting_depth >= MAX_NESTING_DEPTH:
            raise MaxNestingDepthExceededError(
                f"Maximum nesting depth ({MAX_NESTING_DEPTH}) exceeded"
            )

        # Get child workflow
        child_workflow = session.get(Workflow, child_workflow_id)
        if not child_workflow:
            raise WorkflowNotFoundError(f"Child workflow {child_workflow_id} not found")

        # Map inputs from parent execution state
        parent_state = self.workflow_engine.get_execution_state(
            session, parent_execution.id
        )
        child_inputs = self._map_inputs(parent_state, input_mapping)

        # Create child execution
        child_execution = self.workflow_engine.create_execution(
            session,
            child_workflow_id,
            trigger_data=child_inputs,
        )

        # Set parent relationship
        child_execution.parent_execution_id = parent_execution.id
        child_execution.parent_node_id = parent_node_id
        child_execution.nesting_depth = parent_execution.nesting_depth + 1

        session.add(child_execution)
        session.commit()
        session.refresh(child_execution)

        # Create SubWorkflowCall record
        sub_workflow_call = SubWorkflowCall(
            parent_execution_id=parent_execution.id,
            child_execution_id=child_execution.id,
            parent_node_id=parent_node_id,
            input_mapping=input_mapping,
            output_mapping={},  # Will be populated when child completes
            status="running",
            started_at=datetime.utcnow(),
        )

        session.add(sub_workflow_call)
        session.commit()
        session.refresh(sub_workflow_call)

        # Log sub-workflow call
        self._log_sub_workflow_call(
            session,
            parent_execution.id,
            parent_node_id,
            child_workflow.name,
            child_execution.execution_id,
        )

        # Execute child workflow asynchronously
        # In production, this would be queued to a worker
        # For now, we'll execute synchronously
        try:
            # Trigger child workflow execution
            # This would typically be done via a worker/queue
            # For now, we'll mark it as running and let the worker handle it
            logger.info(
                f"Sub-workflow call created: "
                f"parent={parent_execution.execution_id}, "
                f"child={child_execution.execution_id}, "
                f"workflow={child_workflow.name}"
            )

        except Exception as e:
            # Mark sub-workflow call as failed
            sub_workflow_call.status = "failed"
            sub_workflow_call.error_message = str(e)
            sub_workflow_call.completed_at = datetime.utcnow()
            session.add(sub_workflow_call)
            session.commit()

            logger.error(
                f"Failed to execute sub-workflow: {e}",
                exc_info=True
            )
            raise

        return sub_workflow_call

    def _map_inputs(
        self,
        parent_state: Any,  # ExecutionState
        input_mapping: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Map parent execution state to child workflow inputs.

        Args:
            parent_state: Parent execution state
            input_mapping: Mapping configuration
                Example: {
                    "email": "{{node1.output.email}}",
                    "name": "{{trigger.payload.name}}"
                }

        Returns:
            Mapped inputs for child workflow
        """
        child_inputs = {}

        for child_key, parent_path in input_mapping.items():
            # Parse path like "{{node1.output.email}}"
            if isinstance(parent_path, str) and parent_path.startswith("{{") and parent_path.endswith("}}"):
                # Extract path
                path = parent_path[2:-2].strip()  # Remove {{ }}

                # Resolve path from parent state
                value = self._resolve_path(parent_state, path)
                child_inputs[child_key] = value
            else:
                # Direct value
                child_inputs[child_key] = parent_path

        return child_inputs

    def _resolve_path(self, state: Any, path: str) -> Any:
        """
        Resolve a path from execution state.

        Args:
            state: ExecutionState instance
            path: Path like "node1.output.email" or "trigger.payload.name"

        Returns:
            Resolved value
        """
        parts = path.split(".")

        # Start from execution state
        current = state

        for part in parts:
            if hasattr(current, part):
                current = getattr(current, part)
            elif isinstance(current, dict):
                current = current.get(part)
            else:
                return None

        return current

    def _log_sub_workflow_call(
        self,
        session: Session,
        parent_execution_id: uuid.UUID,
        parent_node_id: str,
        child_workflow_name: str,
        child_execution_id: str,
    ) -> None:
        """Log sub-workflow call."""
        log = ExecutionLog(
            execution_id=parent_execution_id,
            node_id=parent_node_id,
            level="info",
            message=f"Calling sub-workflow: {child_workflow_name} (execution: {child_execution_id})",
        )
        session.add(log)
        session.commit()

    def update_sub_workflow_status(
        self,
        session: Session,
        child_execution_id: uuid.UUID,
        status: str,
        output_mapping: dict[str, Any] | None = None,
        error_message: str | None = None,
    ) -> None:
        """
        Update sub-workflow call status when child execution completes.

        Args:
            session: Database session
            child_execution_id: Child execution ID
            status: New status (completed, failed)
            output_mapping: Output mapping if completed
            error_message: Error message if failed
        """
        # Find sub-workflow call
        statement = select(SubWorkflowCall).where(
            SubWorkflowCall.child_execution_id == child_execution_id
        )
        sub_workflow_call = session.exec(statement).first()

        if not sub_workflow_call:
            logger.warning(f"Sub-workflow call not found for child execution: {child_execution_id}")
            return

        # Update status
        sub_workflow_call.status = status
        sub_workflow_call.completed_at = datetime.utcnow()

        if output_mapping:
            sub_workflow_call.output_mapping = output_mapping

        if error_message:
            sub_workflow_call.error_message = error_message

        session.add(sub_workflow_call)
        session.commit()

        # Map outputs back to parent execution state
        if status == "completed" and output_mapping:
            self._map_outputs_to_parent(
                session,
                sub_workflow_call.parent_execution_id,
                sub_workflow_call.parent_node_id,
                output_mapping,
            )

    def _map_outputs_to_parent(
        self,
        session: Session,
        parent_execution_id: uuid.UUID,
        parent_node_id: str,
        output_mapping: dict[str, Any],
    ) -> None:
        """
        Map child workflow outputs back to parent execution state.

        Args:
            session: Database session
            parent_execution_id: Parent execution ID
            parent_node_id: Parent node ID
            output_mapping: Output mapping configuration
        """
        parent_execution = session.get(WorkflowExecution, parent_execution_id)
        if not parent_execution:
            return

        # Get child execution
        statement = select(SubWorkflowCall).where(
            SubWorkflowCall.parent_execution_id == parent_execution_id,
            SubWorkflowCall.parent_node_id == parent_node_id,
        )
        sub_workflow_call = session.exec(statement).first()

        if not sub_workflow_call:
            return

        child_execution = session.get(WorkflowExecution, sub_workflow_call.child_execution_id)
        if not child_execution:
            return

        # Get child execution state
        child_state = self.workflow_engine.get_execution_state(
            session, child_execution.id
        )

        # Map outputs
        parent_outputs = {}
        for parent_path, child_path in output_mapping.items():
            # Resolve child path
            value = self._resolve_path(child_state, child_path)

            # Store in parent node results
            parent_outputs[parent_path] = value

        # Update parent execution state with sub-workflow outputs
        parent_state = self.workflow_engine.get_execution_state(
            session, parent_execution_id
        )

        # Store outputs in node_results for the parent node
        if not hasattr(parent_state, 'node_results'):
            parent_state.node_results = {}

        if parent_node_id not in parent_state.node_results:
            parent_state.node_results[parent_node_id] = {}

        parent_state.node_results[parent_node_id]['output'] = parent_outputs

        # Persist updated state
        parent_execution.execution_state = parent_state.to_dict()
        session.add(parent_execution)
        session.commit()
```

---

### Phase 3: Backend - Workflow Engine Integration (Day 2 - Morning)

#### 3.1 Update WorkflowEngine to Handle Sub-Workflow Nodes

**File:** `backend/app/workflows/engine.py`

Add to `WorkflowEngine` class:

```python
from app.workflows.sub_workflow_executor import SubWorkflowExecutor, MaxNestingDepthExceededError

class WorkflowEngine:
    def __init__(self, ...):
        # ... existing initialization ...
        self.sub_workflow_executor = SubWorkflowExecutor(self)

    def execute_node(
        self,
        session: Session,
        execution: WorkflowExecution,
        node: WorkflowNode,
        state: ExecutionState,
    ) -> NodeExecutionResult:
        """
        Execute a workflow node.

        Handles sub-workflow nodes specially.
        """
        # Check if this is a sub-workflow node
        if node.node_type == "sub_workflow":
            return self._execute_sub_workflow_node(
                session, execution, node, state
            )

        # ... existing node execution logic ...

    def _execute_sub_workflow_node(
        self,
        session: Session,
        execution: WorkflowExecution,
        node: WorkflowNode,
        state: ExecutionState,
    ) -> NodeExecutionResult:
        """
        Execute a sub-workflow node.

        Args:
            session: Database session
            execution: Current execution
            node: Sub-workflow node
            state: Current execution state

        Returns:
            NodeExecutionResult
        """
        config = node.config or {}
        child_workflow_id = config.get("workflow_id")
        input_mapping = config.get("input_mapping", {})
        output_mapping = config.get("output_mapping", {})
        timeout_seconds = config.get("timeout_seconds", 300)

        if not child_workflow_id:
            return NodeExecutionResult(
                success=False,
                output={"error": "Child workflow ID not specified"},
                error_message="Child workflow ID not specified",
            )

        try:
            # Execute sub-workflow
            sub_workflow_call = self.sub_workflow_executor.execute_sub_workflow(
                session=session,
                parent_execution=execution,
                parent_node_id=node.node_id,
                child_workflow_id=uuid.UUID(child_workflow_id),
                input_mapping=input_mapping,
                timeout_seconds=timeout_seconds,
            )

            # For now, wait for completion (in production, this would be async)
            # In a real implementation, we'd:
            # 1. Queue the sub-workflow for execution
            # 2. Return immediately with status "waiting"
            # 3. Resume parent workflow when child completes

            # For MVP, we'll wait synchronously
            child_execution = session.get(
                WorkflowExecution, sub_workflow_call.child_execution_id
            )

            # Wait for child to complete (with timeout)
            import time
            start_time = time.time()
            while child_execution.status == "running":
                if time.time() - start_time > timeout_seconds:
                    raise TimeoutError(f"Sub-workflow execution timed out after {timeout_seconds}s")

                session.refresh(child_execution)
                time.sleep(0.5)  # Poll every 500ms

            # Update sub-workflow call status
            if child_execution.status == "completed":
                self.sub_workflow_executor.update_sub_workflow_status(
                    session,
                    child_execution.id,
                    "completed",
                    output_mapping=output_mapping,
                )

                # Get mapped outputs
                parent_state = self.get_execution_state(session, execution.id)
                node_outputs = parent_state.node_results.get(node.node_id, {}).get("output", {})

                return NodeExecutionResult(
                    success=True,
                    output=node_outputs,
                )
            else:
                # Child failed
                self.sub_workflow_executor.update_sub_workflow_status(
                    session,
                    child_execution.id,
                    "failed",
                    error_message=child_execution.error_message,
                )

                return NodeExecutionResult(
                    success=False,
                    output={},
                    error_message=f"Sub-workflow failed: {child_execution.error_message}",
                )

        except MaxNestingDepthExceededError as e:
            return NodeExecutionResult(
                success=False,
                output={},
                error_message=str(e),
            )
        except Exception as e:
            logger.error(f"Failed to execute sub-workflow node: {e}", exc_info=True)
            return NodeExecutionResult(
                success=False,
                output={},
                error_message=str(e),
            )
```

---

### Phase 4: Backend - API Endpoints (Day 2 - Afternoon)

#### 4.1 Add Workflow List Endpoint

**File:** `backend/app/api/routes/workflows.py`

```python
@router.get("/list", response_model=list[WorkflowPublic])
def list_workflows_for_selection(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
) -> Any:
    """
    List workflows available for sub-workflow selection.

    Returns workflows that the user has access to (owned by user or public).
    """
    statement = select(Workflow).where(
        Workflow.owner_id == current_user.id,
        Workflow.is_active == True,
    )

    if search:
        statement = statement.where(
            Workflow.name.ilike(f"%{search}%")
        )

    statement = statement.offset(skip).limit(limit)

    workflows = session.exec(statement).all()

    return [
        WorkflowPublic(
            id=w.id,
            name=w.name,
            description=w.description,
            is_active=w.is_active,
            version=w.version,
            trigger_config=w.trigger_config,
            graph_config=w.graph_config,
            owner_id=w.owner_id,
            created_at=w.created_at,
            updated_at=w.updated_at,
        )
        for w in workflows
    ]
```

#### 4.2 Update Run Workflow Endpoint

**File:** `backend/app/api/routes/workflows.py`

Update `run_workflow` to support `parent_execution_id`:

```python
@router.post("/{workflow_id}/run", status_code=201)
def run_workflow(
    workflow_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
    trigger_data: dict[str, Any] | None = Body(default=None),
    parent_execution_id: uuid.UUID | None = None,  # NEW
    parent_node_id: str | None = None,  # NEW
) -> Any:
    """
    Run a workflow execution.

    Supports sub-workflow execution when parent_execution_id is provided.
    """
    # ... existing validation ...

    # Create execution
    execution = workflow_engine.create_execution(
        session=session,
        workflow_id=workflow_id,
        trigger_data=trigger_data,
    )

    # Set parent relationship if provided
    if parent_execution_id:
        parent_execution = session.get(WorkflowExecution, parent_execution_id)
        if parent_execution:
            execution.parent_execution_id = parent_execution_id
            execution.parent_node_id = parent_node_id
            execution.nesting_depth = parent_execution.nesting_depth + 1

    session.add(execution)
    session.commit()

    # ... rest of execution logic ...
```

---

### Phase 5: Frontend - Sub-Workflow Node Component (Day 3 - Morning)

#### 5.1 Create SubWorkflowNode Component

**File:** `frontend/src/components/Workflow/nodes/SubWorkflowNode.tsx` (NEW)

```typescript
import { Handle, type NodeProps, Position } from "@xyflow/react"
import { Workflow } from "lucide-react"

interface SubWorkflowNodeData extends Record<string, unknown> {
  label?: string
  config?: {
    workflow_id?: string
    workflow_name?: string
    [key: string]: any
  }
}

export function SubWorkflowNode(props: NodeProps) {
  const { data, selected } = props
  const nodeData = data as SubWorkflowNodeData
  const workflowName = nodeData.config?.workflow_name || "Select Workflow"
  const label = nodeData.label || "Sub-Workflow"

  return (
    <div
      className={`px-4 py-2 shadow-lg rounded-lg bg-gradient-to-br from-purple-50 to-indigo-50 border-2 min-w-[150px] ${
        selected ? "border-primary" : "border-purple-300"
      }`}
    >
      <div className="flex items-center gap-2">
        <Workflow className="h-4 w-4 text-purple-600 flex-shrink-0" />
        <div className="font-semibold text-sm truncate">{label}</div>
      </div>
      {workflowName !== "Select Workflow" && (
        <div className="text-xs text-muted-foreground mt-1 truncate">
          {workflowName}
        </div>
      )}
      <Handle type="target" position={Position.Left} className="w-3 h-3" />
      <Handle type="source" position={Position.Right} className="w-3 h-3" />
    </div>
  )
}
```

#### 5.2 Register SubWorkflowNode

**File:** `frontend/src/components/Workflow/WorkflowCanvas.tsx`

```typescript
import { SubWorkflowNode } from "./nodes/SubWorkflowNode"

const nodeTypes: NodeTypes = {
  // ... existing node types ...
  sub_workflow: SubWorkflowNode,
}
```

#### 5.3 Add to NodePalette

**File:** `frontend/src/components/Workflow/NodePalette.tsx`

```typescript
const baseNodeTypes: NodeType[] = [
  // ... existing types ...
  {
    type: "sub_workflow",
    label: "Sub-Workflow",
    icon: Workflow,
    category: "Core",
    description: "Execute another workflow",
  },
]
```

---

### Phase 6: Frontend - Node Configuration Panel (Day 3 - Afternoon)

#### 6.1 Add Sub-Workflow Configuration UI

**File:** `frontend/src/components/Workflow/NodeConfigPanel.tsx`

Add to the component:

```typescript
// State for workflow selection
const [availableWorkflows, setAvailableWorkflows] = useState<Array<{
  id: string
  name: string
  description: string | null
}>>([])
const [isLoadingWorkflows, setIsLoadingWorkflows] = useState(false)
const [selectedWorkflowId, setSelectedWorkflowId] = useState<string>(
  config.workflow_id || ""
)

// Fetch available workflows
useEffect(() => {
  if (node?.type === "sub_workflow") {
    setIsLoadingWorkflows(true)
    apiClient
      .request<Array<{ id: string; name: string; description: string | null }>>(
        "/api/v1/workflows/list?limit=100"
      )
      .then((workflows) => {
        setAvailableWorkflows(workflows)
        if (config.workflow_id) {
          const selected = workflows.find((w) => w.id === config.workflow_id)
          if (selected) {
            setSelectedWorkflowId(selected.id)
          }
        }
      })
      .catch((error) => {
        console.error("Failed to fetch workflows:", error)
      })
      .finally(() => {
        setIsLoadingWorkflows(false)
      })
  }
}, [node?.type, config.workflow_id])

// In the render section, add sub-workflow configuration:
{node.type === "sub_workflow" && (
  <>
    <div className="space-y-2">
      <Label>Select Workflow</Label>
      <Select
        value={selectedWorkflowId}
        onValueChange={(value) => {
          setSelectedWorkflowId(value)
          const selected = availableWorkflows.find((w) => w.id === value)
          handleConfigUpdate("workflow_id", value)
          handleConfigUpdate("workflow_name", selected?.name || "")
        }}
        disabled={isLoadingWorkflows}
      >
        <SelectTrigger>
          <SelectValue placeholder="Select a workflow">
            {isLoadingWorkflows
              ? "Loading..."
              : selectedWorkflowId
              ? availableWorkflows.find((w) => w.id === selectedWorkflowId)?.name
              : "Select a workflow"}
          </SelectValue>
        </SelectTrigger>
        <SelectContent>
          {availableWorkflows.map((workflow) => (
            <SelectItem key={workflow.id} value={workflow.id}>
              <div>
                <div className="font-medium">{workflow.name}</div>
                {workflow.description && (
                  <div className="text-xs text-muted-foreground">
                    {workflow.description}
                  </div>
                )}
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>

    {/* Input Mapping */}
    <div className="space-y-2">
      <Label>Input Mapping</Label>
      <Textarea
        placeholder='{"email": "{{node1.output.email}}", "name": "{{trigger.payload.name}}"}'
        value={JSON.stringify(config.input_mapping || {}, null, 2)}
        onChange={(e) => {
          try {
            const parsed = JSON.parse(e.target.value)
            handleConfigUpdate("input_mapping", parsed)
          } catch {
            // Invalid JSON, ignore
          }
        }}
        className="font-mono text-xs"
        rows={4}
      />
      <p className="text-xs text-muted-foreground">
        Map parent workflow data to child workflow inputs using JSON
      </p>
    </div>

    {/* Output Mapping */}
    <div className="space-y-2">
      <Label>Output Mapping</Label>
      <Textarea
        placeholder='{"result": "output.result", "status": "output.status"}'
        value={JSON.stringify(config.output_mapping || {}, null, 2)}
        onChange={(e) => {
          try {
            const parsed = JSON.parse(e.target.value)
            handleConfigUpdate("output_mapping", parsed)
          } catch {
            // Invalid JSON, ignore
          }
        }}
        className="font-mono text-xs"
        rows={4}
      />
      <p className="text-xs text-muted-foreground">
        Map child workflow outputs back to parent workflow
      </p>
    </div>

    {/* Timeout */}
    <div className="space-y-2">
      <Label>Timeout (seconds)</Label>
      <Input
        type="number"
        value={config.timeout_seconds || 300}
        onChange={(e) => {
          handleConfigUpdate("timeout_seconds", parseInt(e.target.value) || 300)
        }}
        min={1}
        max={3600}
      />
    </div>
  </>
)}
```

---

## 🧪 Testing Plan

### Unit Tests

1. **SubWorkflowExecutor Tests**
   - Test input mapping
   - Test output mapping
   - Test nesting depth limit
   - Test error handling

2. **WorkflowEngine Tests**
   - Test sub-workflow node execution
   - Test state persistence
   - Test error propagation

### Integration Tests

1. **End-to-End Sub-Workflow Execution**
   - Create parent workflow with sub-workflow node
   - Create child workflow
   - Execute parent workflow
   - Verify child workflow executes
   - Verify outputs are mapped back

2. **Nested Execution**
   - Test 3-level nesting (parent → child → grandchild)
   - Test maximum nesting depth enforcement

3. **Error Scenarios**
   - Child workflow fails
   - Child workflow times out
   - Child workflow not found

---

## 📊 Performance Considerations

1. **Async Execution**
   - Sub-workflows should execute asynchronously
   - Use worker queue (Celery/RQ) for execution
   - Parent workflow should pause and resume when child completes

2. **State Management**
   - Efficient state serialization/deserialization
   - Minimize database queries during execution

3. **Caching**
   - Cache workflow definitions
   - Cache execution state snapshots

---

## 🔒 Security Considerations

1. **Access Control**
   - Users can only select workflows they own
   - Respect workflow permissions
   - Audit sub-workflow calls

2. **Input Validation**
   - Validate input mapping paths
   - Sanitize user-provided mappings
   - Prevent path traversal attacks

3. **Resource Limits**
   - Enforce nesting depth limit
   - Enforce timeout limits
   - Monitor resource usage

---

## 📈 Future Enhancements

1. **Parallel Execution**
   - Support multiple sub-workflows executing in parallel
   - Wait for all to complete before proceeding

2. **Conditional Sub-Workflows**
   - Execute sub-workflow based on condition
   - Support for loops/iterations

3. **Sub-Workflow Templates**
   - Pre-configured sub-workflow mappings
   - Reusable workflow components

4. **Visual Execution Tree**
   - Show nested execution tree in UI
   - Display execution status at each level

---

## ✅ Implementation Checklist

### Backend
- [ ] Create Alembic migration
- [ ] Update WorkflowExecution model
- [ ] Create SubWorkflowCall model
- [ ] Implement SubWorkflowExecutor
- [ ] Integrate with WorkflowEngine
- [ ] Add API endpoints
- [ ] Add unit tests
- [ ] Add integration tests

### Frontend
- [ ] Create SubWorkflowNode component
- [ ] Add to NodePalette
- [ ] Add configuration UI in NodeConfigPanel
- [ ] Add workflow selection dropdown
- [ ] Add input/output mapping UI
- [ ] Add execution status display
- [ ] Add nested execution tree view

### Documentation
- [ ] Update API documentation
- [ ] Create user guide
- [ ] Add examples

---

## 🎯 Success Criteria

1. ✅ Users can add sub-workflow nodes to workflows
2. ✅ Users can select child workflows from a list
3. ✅ Users can configure input/output mappings
4. ✅ Sub-workflows execute correctly
5. ✅ Outputs are mapped back to parent workflow
6. ✅ Nesting depth limit is enforced
7. ✅ Error handling works correctly
8. ✅ Execution status is tracked
9. ✅ UI shows nested execution tree

---

## 📝 Notes

- **MVP Approach**: Start with synchronous execution, then move to async
- **Worker Integration**: Sub-workflow execution should eventually use worker queue
- **State Management**: Consider using Redis for execution state in production
- **Monitoring**: Add metrics for sub-workflow execution times and success rates

---

**Estimated Total Effort:** 2-3 days
**Priority:** High
**Dependencies:** None
**Blocks:** None
