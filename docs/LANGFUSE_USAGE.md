# Langfuse Usage in SynthralOS Platform

**Date:** December 18, 2025

## Overview

Langfuse is an **LLM observability platform** that provides tracing, monitoring, and debugging for AI/LLM applications. In SynthralOS, Langfuse is used to track and monitor all LLM interactions across the platform.

## What Langfuse Does

Langfuse provides:

1. **LLM Call Tracing** - Track every LLM API call (prompts, responses, tokens)
2. **Cost Tracking** - Monitor LLM usage costs per user/workflow
3. **Performance Monitoring** - Track latency, token usage, model performance
4. **Debugging Tools** - Inspect prompts, responses, and intermediate steps
5. **User Attribution** - Link LLM calls to specific users/workflows
6. **Analytics** - Understand LLM usage patterns

## How Langfuse is Used in SynthralOS

### 1. Agent Framework Execution

**Location:** `backend/app/agents/router.py` and framework implementations

**What's Tracked:**
- Agent task execution
- Framework selection logic
- LLM calls made by agents
- Agent reasoning steps
- Task completion status

**Example Usage:**
```python
from app.observability.langfuse import default_langfuse_client

# Create trace for agent task
trace = default_langfuse_client.trace(
    name=f"agent_task_{task_id}",
    user_id=str(user_id),
    metadata={
        "framework": "agentgpt",
        "task_type": "research",
        "workflow_id": str(workflow_id)
    }
)

# Log LLM generation
default_langfuse_client.generation(
    trace_id=trace.id,
    name="agent_reasoning",
    model="gpt-4",
    input_data=prompt,
    output_data=response,
    metadata={"step": "planning"}
)
```

### 2. Chat Interface (ag-ui)

**Location:** `backend/app/api/routes/chat.py`

**What's Tracked:**
- User chat messages
- AI responses
- Conversation context
- Token usage per conversation
- Response quality

**Example Usage:**
```python
# Create trace for chat session
trace = default_langfuse_client.trace(
    name=f"chat_session_{session_id}",
    user_id=str(user_id),
    metadata={
        "session_id": session_id,
        "conversation_type": "workflow_builder"
    }
)

# Log each message exchange
default_langfuse_client.generation(
    trace_id=trace.id,
    name="chat_response",
    model="gpt-4",
    input_data=user_message,
    output_data=ai_response,
    metadata={"turn": turn_number}
)
```

### 3. RAG (Retrieval-Augmented Generation)

**Location:** `backend/app/rag/service.py`

**What's Tracked:**
- RAG query processing
- Document retrieval
- LLM generation with context
- Retrieval quality metrics

**Example Usage:**
```python
# Create trace for RAG query
trace = default_langfuse_client.trace(
    name=f"rag_query_{query_id}",
    user_id=str(user_id),
    metadata={
        "index_id": str(index_id),
        "query": query_text,
        "retrieved_docs": len(documents)
    }
)

# Log retrieval step
default_langfuse_client.span(
    trace_id=trace.id,
    name="document_retrieval",
    metadata={"doc_count": len(documents)}
)

# Log LLM generation with context
default_langfuse_client.generation(
    trace_id=trace.id,
    name="rag_generation",
    model="gpt-4",
    input_data=f"Context: {context}\n\nQuery: {query}",
    output_data=response,
    metadata={"context_length": len(context)}
)
```

### 4. Workflow Execution

**Location:** `backend/app/workflows/execution.py`

**What's Tracked:**
- Workflow execution lifecycle
- LLM node executions
- Workflow-level LLM calls
- Error tracking

**Example Usage:**
```python
# Create trace for workflow execution
trace = default_langfuse_client.trace(
    name=f"workflow_{workflow_id}_execution_{execution_id}",
    user_id=str(user_id),
    metadata={
        "workflow_id": str(workflow_id),
        "execution_id": str(execution_id),
        "trigger_type": trigger_type
    }
)

# Log each LLM node execution
for node in llm_nodes:
    default_langfuse_client.span(
        trace_id=trace.id,
        name=f"node_{node.id}",
        metadata={
            "node_type": node.type,
            "node_id": str(node.id)
        }
    )
```

## Langfuse Client API

The `LangfuseClient` provides these methods:

### 1. `trace()` - Create a Trace

```python
trace = default_langfuse_client.trace(
    name="my_trace",
    user_id="user_123",
    metadata={"key": "value"}
)
```

**Use Cases:**
- Start tracking a new operation
- Group related LLM calls together
- Link to user/workflow

### 2. `span()` - Create a Span

```python
span = default_langfuse_client.span(
    trace_id=trace.id,
    name="retrieval_step",
    metadata={"doc_count": 5}
)
```

**Use Cases:**
- Track sub-operations within a trace
- Log intermediate steps
- Measure timing of specific operations

### 3. `generation()` - Log LLM Call

```python
default_langfuse_client.generation(
    trace_id=trace.id,
    name="agent_reasoning",
    model="gpt-4",
    input_data=prompt,
    output_data=response,
    metadata={"temperature": 0.7}
)
```

**Use Cases:**
- Track every LLM API call
- Monitor prompt/response pairs
- Track token usage and costs
- Debug LLM behavior

### 4. `score()` - Add Score/Evaluation

```python
default_langfuse_client.score(
    trace_id=trace.id,
    name="quality_score",
    value=0.85,
    comment="High quality response"
)
```

**Use Cases:**
- Rate response quality
- Track user feedback
- Monitor model performance

## Integration Points

### Current Integration Status

✅ **Implemented:**
- Langfuse client wrapper (`backend/app/observability/langfuse.py`)
- Client initialization in `main.py`
- Graceful fallback if not configured

⚠️ **To Be Integrated:**
- Agent framework execution tracking
- Chat interface LLM call tracking
- RAG query tracking
- Workflow execution tracking

### Where to Add Langfuse Tracking

1. **Agent Frameworks** (`backend/app/agents/frameworks/`)
   - Add trace creation in `execute()` methods
   - Log LLM calls in framework implementations

2. **Chat Service** (`backend/app/api/routes/chat.py`)
   - Create trace per chat session
   - Log each message exchange

3. **RAG Service** (`backend/app/rag/service.py`)
   - Create trace per query
   - Log retrieval and generation steps

4. **Workflow Execution** (`backend/app/workflows/`)
   - Create trace per execution
   - Log LLM node executions

## Benefits for SynthralOS

### 1. Cost Management

- Track LLM costs per user/workflow
- Identify expensive operations
- Optimize token usage
- Set usage limits

### 2. Debugging

- Inspect prompts and responses
- See intermediate reasoning steps
- Debug agent failures
- Understand workflow behavior

### 3. Performance Monitoring

- Track latency per model
- Monitor token usage
- Identify bottlenecks
- Optimize prompts

### 4. User Analytics

- Understand usage patterns
- Track feature adoption
- Monitor user satisfaction
- Improve AI features

## Example: Complete Agent Task Trace

```python
from app.observability.langfuse import default_langfuse_client

def execute_agent_task(task_id, user_id, prompt):
    # Create trace
    trace = default_langfuse_client.trace(
        name=f"agent_task_{task_id}",
        user_id=str(user_id),
        metadata={
            "task_id": str(task_id),
            "task_type": "research"
        }
    )
    
    # Planning step
    planning_span = default_langfuse_client.span(
        trace_id=trace.id,
        name="planning",
        metadata={"step": 1}
    )
    
    planning_response = llm_call("Plan the research...")
    
    default_langfuse_client.generation(
        trace_id=trace.id,
        name="planning_llm",
        model="gpt-4",
        input_data="Plan the research...",
        output_data=planning_response,
        metadata={"step": "planning"}
    )
    
    # Execution step
    execution_span = default_langfuse_client.span(
        trace_id=trace.id,
        name="execution",
        metadata={"step": 2}
    )
    
    execution_response = llm_call("Execute research...")
    
    default_langfuse_client.generation(
        trace_id=trace.id,
        name="execution_llm",
        model="gpt-4",
        input_data="Execute research...",
        output_data=execution_response,
        metadata={"step": "execution"}
    )
    
    # Score the result
    default_langfuse_client.score(
        trace_id=trace.id,
        name="task_quality",
        value=0.9,
        comment="High quality research output"
    )
    
    return execution_response
```

## Langfuse Dashboard

Once configured, you can:

1. **View Traces** - See all LLM operations
2. **Analyze Costs** - Track spending per user/model
3. **Debug Issues** - Inspect failed operations
4. **Monitor Performance** - Track latency and token usage
5. **User Analytics** - Understand usage patterns

## Configuration

See `docs/OBSERVABILITY_SETUP.md` for setup instructions.

**Required Environment Variables:**
```bash
LANGFUSE_KEY=pk_lf_xxxxxxxxxxxxxxxxxxxxx
LANGFUSE_SECRET_KEY=sk_lf_xxxxxxxxxxxxxxxxxxxxx  # Optional
LANGFUSE_HOST=https://cloud.langfuse.com  # Optional
```

## Related Documentation

- `docs/OBSERVABILITY_SETUP.md` - How to set up Langfuse
- `backend/app/observability/langfuse.py` - Langfuse client implementation
- `docs/FRONTEND_BACKEND_INTERACTION.md` - Platform architecture

