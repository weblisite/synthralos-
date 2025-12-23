# Workflow Execution Engine - Status & Architecture

## Overview

The workflow execution engine is a **custom-built orchestration system** that replicates Temporal-like functionality. It's designed to handle workflow execution lifecycle, state management, retries, scheduling, and signals.

## Architecture

### Core Components

1. **WorkflowEngine** (`backend/app/workflows/engine.py`)
   - Core execution engine
   - Manages execution lifecycle
   - Handles state persistence
   - Supports pause/resume/terminate

2. **WorkflowWorker** (`backend/app/workflows/worker.py`)
   - Background worker that polls for work
   - Processes scheduled, retry, signal, and running executions
   - Executes workflow steps sequentially

3. **Activity Handlers** (`backend/app/workflows/activities.py`)
   - Node execution handlers for different node types
   - Currently supports: trigger, http_request, code, rag_switch, ocr_switch

4. **State Management** (`backend/app/workflows/state.py`)
   - ExecutionState: Tracks current execution point, node results, execution data
   - WorkflowState: Represents workflow structure (nodes, edges, entry point)
   - NodeExecutionResult: Result of individual node execution

5. **Retry Manager** (`backend/app/workflows/retry.py`)
   - Configurable retry policies with exponential backoff
   - Max retries, initial delay, backoff multiplier

6. **Scheduler** (`backend/app/workflows/scheduler.py`)
   - CRON-based scheduling
   - Calculates next run times
   - Triggers scheduled executions

7. **Signal Handler** (`backend/app/workflows/signals.py`)
   - Handles workflow signals (human-in-the-loop, external events)
   - Supports waiting for signals and resuming execution

8. **LangGraph Engine** (`backend/app/workflows/langgraph_engine.py`)
   - **Partially implemented** - Builds LangGraph graphs from workflows
   - Not yet fully integrated with main execution flow

## Current Implementation Status

### ✅ Fully Implemented

1. **Execution Lifecycle**
   - ✅ Create execution
   - ✅ Execute nodes sequentially
   - ✅ Persist state to database
   - ✅ Pause/resume/terminate executions
   - ✅ Complete/fail executions

2. **State Management**
   - ✅ Execution state persistence (PostgreSQL JSONB)
   - ✅ Node execution history
   - ✅ Execution data passing between nodes
   - ✅ Current node tracking

3. **Retry Logic**
   - ✅ Configurable retry policies
   - ✅ Exponential backoff
   - ✅ Max retries limit
   - ✅ Retry scheduling

4. **Scheduling**
   - ✅ CRON expression parsing
   - ✅ Next run calculation
   - ✅ Scheduled execution triggering
   - ✅ Schedule management

5. **Signals**
   - ✅ Signal emission
   - ✅ Waiting for signals
   - ✅ Signal processing
   - ✅ Resume after signal

6. **Activity Handlers**
   - ✅ Trigger nodes (pass-through)
   - ✅ HTTP request nodes
   - ✅ Code execution nodes
   - ✅ RAG switch nodes
   - ✅ OCR switch nodes

7. **Worker**
   - ✅ Polling for work
   - ✅ Processing scheduled executions
   - ✅ Processing retry executions
   - ✅ Processing signal-waiting executions
   - ✅ Processing running executions

8. **Self-Healing**
   - ✅ Integration with SelfHealingService
   - ✅ Automatic error recovery attempts

### ⚠️ Partially Implemented

1. **Node Execution**
   - ⚠️ **Basic node execution works** but is simplified
   - ⚠️ Currently executes nodes sequentially (one at a time)
   - ⚠️ No parallel execution support
   - ⚠️ No conditional branching logic (only simple linear flow)
   - ⚠️ Limited node type support (only 5 types implemented)

2. **LangGraph Integration**
   - ⚠️ LangGraph engine exists but **not integrated** with main execution flow
   - ⚠️ Can build graphs but doesn't execute them
   - ⚠️ Main worker still uses simplified sequential execution

3. **Connector Integration**
   - ⚠️ Connector nodes exist but **no activity handler** for them
   - ⚠️ Connector actions not executed during workflow runs

4. **Conditional Logic**
   - ⚠️ No conditional/if-else node execution
   - ⚠️ No branching based on node outputs

5. **Sub-workflows**
   - ⚠️ Sub-workflow nodes exist in UI but **not executed** by engine

### ❌ Not Implemented

1. **Parallel Execution**
   - ❌ Cannot execute multiple nodes in parallel
   - ❌ No fan-out/fan-in patterns

2. **Advanced Branching**
   - ❌ No conditional branching based on node outputs
   - ❌ No switch/case logic
   - ❌ No loop/iteration support

3. **Connector Node Execution**
   - ❌ Connector nodes don't execute actual connector actions
   - ❌ No integration with connector service

4. **Agent Node Execution**
   - ❌ Agent nodes not executed
   - ❌ No integration with agent framework

5. **WebSocket Real-time Updates**
   - ❌ No WebSocket events for execution progress
   - ❌ Frontend polls for status instead

6. **Execution Replay**
   - ❌ Replay endpoint exists but doesn't actually replay
   - ❌ No state snapshot/restore

7. **Workflow Versioning**
   - ❌ Version tracking exists but not enforced
   - ❌ No version rollback

## How It Currently Works

### Execution Flow

1. **User triggers workflow** via API (`POST /api/v1/workflows/{id}/run`)
2. **WorkflowEngine.create_execution()** creates execution record
3. **WorkflowWorker** polls database for running executions
4. **Worker._execute_workflow_step()** executes one node at a time:
   - Gets current execution state
   - Gets workflow state (nodes, edges)
   - Determines next node to execute
   - Executes node via `WorkflowEngine.execute_node()`
   - Updates state with node result
   - Determines next node from edges
   - Repeats until workflow completes or fails

### Node Execution

1. **WorkflowEngine.execute_node()** is called with:
   - Execution ID
   - Node ID
   - Node config
   - Input data

2. **Activity handler** is selected based on node type:
   - `get_activity_handler(node_type)` returns handler
   - Handler executes node logic
   - Returns `NodeExecutionResult`

3. **Result is stored** in execution state:
   - Node marked as completed
   - Output stored in execution_data
   - Next node determined from edges

### State Persistence

- **ExecutionState** stored in `WorkflowExecution.execution_state` (JSONB)
- Contains: current_node_id, completed_node_ids, node_results, execution_data
- Persisted after each node execution
- Allows pause/resume/replay

### Retry Logic

- When node fails, `fail_execution()` is called
- Checks if retry count < max_retries
- If yes, schedules retry with exponential backoff
- Worker picks up retry when `next_retry_at` is reached

### Scheduling

- Scheduler polls for due schedules (`next_run_at <= now`)
- Triggers execution via `create_execution()`
- Updates schedule's `next_run_at` to next CRON time

## Limitations & Gaps

### Critical Gaps

1. **Connector Nodes Don't Execute**
   - Connector nodes exist in UI but have no activity handler
   - Need to integrate with connector service to execute actions

2. **No Conditional Branching**
   - Can only execute linear workflows
   - Cannot branch based on node outputs
   - No if/else/switch logic

3. **No Parallel Execution**
   - All nodes execute sequentially
   - Cannot run multiple nodes simultaneously

4. **LangGraph Not Integrated**
   - LangGraph engine exists but worker doesn't use it
   - Need to integrate LangGraph for advanced workflows

5. **Limited Node Types**
   - Only 5 node types supported (trigger, http_request, code, rag_switch, ocr_switch)
   - Missing: connector, agent, condition, loop, sub-workflow

### Performance Limitations

1. **Sequential Execution**
   - One node at a time = slow for complex workflows
   - No parallelization

2. **Polling-Based Worker**
   - Worker polls database every 1 second
   - Not event-driven
   - Higher latency

3. **No Caching**
   - Workflow state loaded from DB on every step
   - No in-memory caching

## What Needs to Be Built

### Priority 1: Core Functionality

1. **Connector Node Execution**
   - Create `ConnectorActivityHandler`
   - Integrate with connector service
   - Execute connector actions based on node config

2. **Conditional Branching**
   - Add `ConditionActivityHandler`
   - Evaluate conditions based on execution_data
   - Route to different next nodes based on result

3. **Agent Node Execution**
   - Create `AgentActivityHandler`
   - Integrate with agent framework
   - Execute agent tasks

### Priority 2: Advanced Features

1. **LangGraph Integration**
   - Integrate LangGraph engine with worker
   - Use LangGraph for complex workflows
   - Keep simple engine for basic workflows

2. **Parallel Execution**
   - Support fan-out patterns
   - Execute multiple nodes simultaneously
   - Wait for all to complete before continuing

3. **Sub-workflow Execution**
   - Create `SubWorkflowActivityHandler`
   - Execute child workflows
   - Pass data between parent and child

### Priority 3: Enhancements

1. **WebSocket Real-time Updates**
   - Emit events on node completion
   - Real-time progress updates to frontend

2. **Execution Replay**
   - Implement actual replay logic
   - Restore state from snapshots

3. **Workflow Versioning**
   - Enforce versioning
   - Support version rollback

## Conclusion

The execution engine is **partially built** with a solid foundation:

✅ **What Works:**
- Basic sequential workflow execution
- State persistence
- Retry logic
- Scheduling
- Signals
- Some node types (HTTP, code, RAG, OCR)

⚠️ **What's Missing:**
- Connector node execution
- Conditional branching
- Parallel execution
- LangGraph integration
- Agent node execution
- Sub-workflow execution

The engine can handle **simple linear workflows** but cannot execute **complex workflows** with connectors, conditions, or parallel steps. To make it production-ready, connector execution and conditional branching are critical.
