# SynthralOS - Comprehensive Product Requirements Document

**Version:** 1.0
**Last Updated:** 2025-01-15
**Owner:** Engineering Team
**Status:** Active Development

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Core Components](#core-components)
4. [Database Schema](#database-schema)
5. [API Specifications](#api-specifications)
6. [Frontend Components](#frontend-components)
7. [Integration Requirements](#integration-requirements)
8. [Security & Compliance](#security--compliance)
9. [Observability & Monitoring](#observability--monitoring)
10. [Deployment & Infrastructure](#deployment--infrastructure)
11. [Development Roadmap](#development-roadmap)
12. [Success Metrics](#success-metrics)

---

## Executive Summary

SynthralOS is an AI-powered automation platform that combines workflow orchestration, agent frameworks, and no-code building capabilities. Built on FastAPI (Python) and React (TypeScript), it provides:

- **Visual Workflow Builder** - Drag-and-drop automation creation
- **AI Agent Orchestration** - Multi-framework agent routing and execution
- **Connector Ecosystem** - 150+ SaaS integrations via ACI.dev
- **RAG & Memory** - Intelligent context retrieval and storage
- **OCR & Document Processing** - Multi-engine document extraction
- **Web Scraping** - Proxy-aware, self-healing scraping
- **Browser Automation** - Headless browser orchestration
- **Custom Code Execution** - Secure sandboxed code runtime
- **Chat Interface** - Conversational automation builder (ag-ui)

### Key Technologies

- **Backend:** FastAPI, SQLModel, PostgreSQL (Supabase), Custom Workflow Engine (Temporal-like), LangGraph
- **Frontend:** React, TypeScript, TanStack Router, React Flow, ag-ui
- **Orchestration:** Custom Durable Workflow Engine (Temporal-like functionality), LangGraph (business logic)
- **Auth:** BetterAuth (OAuth 2.0/OIDC + MFA + RBAC)
- **Secrets:** Infisical (runtime secret injection)
- **Observability:** Signoz (OTel), PostHog, Langfuse, Wazuh

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Layer (React)                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │ ag-ui    │  │ Langflow │  │ Clay UI  │  │ Dashboard│ │
│  │ Chat     │  │ Builder  │  │ Tables   │  │           │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ WebSocket + REST
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Backend (Python Only)                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              API Router Layer                        │   │
│  │  /workflows  /agents  /connectors  /rag  /ocr  etc  │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         Execution Layer (LangGraph + Temporal)        │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐        │   │
│  │  │Workflow  │  │ Agent    │  │ Connector │        │   │
│  │  │Engine    │  │ Router   │  │ Registry  │        │   │
│  │  └──────────┘  └──────────┘  └──────────┘        │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         Service Layer (Python Microservices)         │   │
│  │  OCR │ RAG │ Scraping │ Browser │ OSINT │ Code      │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│         Infrastructure Layer                                 │
│  PostgreSQL │ Redis │ Temporal │ Infisical │ Signoz      │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

#### Custom Workflow Engine + LangGraph Division

- **Custom Workflow Engine (Temporal-like):** Durability, retries, versioning, pause/resume, exactly-once guarantees, scheduling, signals
- **LangGraph:** Business logic, branching, conditionals, tool calls, state management

#### Execution Flow

1. User creates workflow in UI → Saved as `Workflow` model
2. Workflow triggered → Custom Workflow Engine creates execution record
3. LangGraph executes nodes → Each node wrapped in Workflow Engine activity
4. Activities call services → Connectors, Agents, OCR, RAG, etc.
5. Results persisted → Workflow Engine history (PostgreSQL) + execution logs
6. UI updates → WebSocket events to frontend

**Note:** We are building a custom workflow orchestration engine that replicates Temporal's core functionality (durability, retries, versioning, scheduling) rather than integrating Temporal itself. This gives us full control over the implementation and allows for tighter integration with our PostgreSQL database and LangGraph execution.

---

## Core Components

### 1. Automation Kernel

**Purpose:** Core workflow execution engine with Temporal durability

**Key Features:**
- Workflow persistence and versioning
- CRON and webhook triggers
- Auto-retry with configurable backoff
- Replay API for failed executions
- Human-in-the-loop prompts
- Connector handshake flow
- Custom durable workflow engine (Temporal-like functionality)

**Deliverables:**
- D1: Custom Workflow Engine Service (Python) - Replicates Temporal functionality
- D2: Connector Registry Service
- D3: Kernel API endpoints
- D4: AG-UI Chat Hooks
- D5: Admin Panel Extension
- D6: Documentation & Samples

**Functional Requirements:**
- F-1: Persist every workflow execution + steps in workflow history (≥30 days)
- F-2: Support CRON & webhook triggers via custom scheduler & signal system
- F-3: Auto-retry Step Activities (configurable back-off)
- F-4: Connector Registry returns manifest (name, scopes, auth_URL, logo)
- F-5: AG-UI chat can invoke `/connect <provider>`
- F-6: Agents can emit `NeedConnector(provider)` event
- F-7: Version workflows (every graph change saved as vN)
- F-8: Expose Replay API to restart from any failed activity
- F-9: All secrets pulled via Infisical injection
- F-10: Latency <300ms for Kernel API non-blocking calls

### 2. Connector Registry (ICI)

**Purpose:** Internal connector system for SaaS integrations

**Key Features:**
- One-click connector registration (manifest + wheel)
- Hot-load connector code in isolated env
- UI wizard for schema mapping
- Webhook ingress → Temporal signals
- Auto-generated documentation
- Version pinning (SemVer)

**Database Models:**
- `Connector` - Base connector metadata
- `ConnectorVersion` - Versioned connector code
- `ConnectorSecret` - Tenant-scoped secrets (stored in Infisical)
- `WebhookSubscription` - Webhook trigger subscriptions

**API Endpoints:**
- `POST /connectors/register` - Register new connector
- `GET /connectors/list` - List available connectors
- `POST /connectors/{slug}/authorize` - OAuth flow initiation
- `GET /connectors/{slug}/callback` - OAuth callback
- `POST /connectors/{slug}/{action}` - Invoke connector action
- `POST /connectors/{slug}/webhook` - Webhook ingress
- `POST /connectors/{slug}/rotate` - Rotate credentials

**Security:**
- All endpoints authenticated via BetterAuth JWT
- Secrets stored in Infisical (never plaintext)
- CI checks: Gitleaks, dependency scanning
- Wheel isolation (venv-per-wheel)

### 3. AI Agents Stack

**Purpose:** Multi-framework agent routing and execution

**Supported Frameworks:**
- AgentGPT, AutoGPT, BabyAGI (simple/recursive)
- MetaGPT, CrewAI (multi-role)
- AutoGen (tool-calling planner)
- Archon (self-healing)
- Agent0 (belief/goal reactive)
- Semantic Kernel (plugin chains)
- Modular Agent Protocol (GPU/Edge)

**Routing Logic:**
- `agent_type = simple` → AgentGPT
- `recursive_planning = true` → AutoGPT/BabyAGI
- `agent_roles > 1` → MetaGPT
- `agent_self_fix = true` → Archon
- `user_prefers_copilot_ui = true` → ag-ui interface

**Database Models:**
- `AgentTask` - Task execution record
- `AgentTaskLog` - Task logs
- `AgentFrameworkConfig` - Framework configuration
- `AgentContextCache` - Context caching (Context7/Mem0)

**API Endpoints:**
- `POST /agents/run` - Execute agent task
- `GET /agents/status/{task_id}` - Get task status
- `POST /agents/switch/evaluate` - Evaluate routing decision
- `GET /agents/catalog` - List available agents

### 4. RAG & Memory Stack

**Purpose:** Retrieval-augmented generation and persistent memory

**Vector Databases:**
- LightRAG (fast lookup, <1MB files)
- Milvus (large datasets, >1GB)
- Weaviate (metadata filtering)
- Qdrant (tag-aware search)
- SupaVec/pgvector (cost-effective default)
- ChromaDB (lightweight)
- Pinecone (external/user-supplied)

**Routing Logic:**
- `file_size < 1MB` → LightRAG
- `dataset_size > 1GB` → Milvus
- `query.requires_metadata = true` → Weaviate
- `structured_memory = true` → Graphiti/Zep
- `user.plan = free` → SupaVec
- `ocr_result_injected = true` → SupaVec/LightRAG

**Database Models:**
- `RAGIndex` - Vector index metadata
- `RAGDocument` - Document records
- `RAGQuery` - Query logs
- `RAGSwitchLog` - Routing decisions
- `RAGFinetuneJob` - Fine-tuning jobs
- `RAGFinetuneDataset` - Training datasets

**API Endpoints:**
- `POST /rag/query` - Query RAG index
- `POST /rag/index` - Create/update index
- `POST /rag/switch/evaluate` - Evaluate routing
- `POST /rag/agent0/validate` - Validate Agent0 prompt
- `GET /rag/switch/logs` - Routing logs
- `POST /rag/finetune` - Start fine-tuning job

### 5. OCR Stack

**Purpose:** Multi-engine OCR for document extraction

**Engines:**
- DocTR (structured table extraction)
- EasyOCR (handwriting)
- Google Vision API (heavy PDFs)
- PaddleOCR (low-latency regional)
- Tesseract (fallback)
- Omniparser (structured JSON)

**Routing Logic:**
- `layout = table` → DocTR
- `handwriting_detected = true` → EasyOCR
- `heavy_pdf_or_image = true` → Google Vision
- `region = EU / latency > 1s` → PaddleOCR
- `result = empty` → Tesseract
- `structured_json_required = true` → Omniparser

**Database Models:**
- `OCRJob` - OCR job record
- `OCRDocument` - Document metadata
- `OCRResult` - Extraction results

**API Endpoints:**
- `POST /ocr/extract` - Extract text from document
- `GET /ocr/status/{job_id}` - Get job status
- `POST /ocr/batch` - Batch processing

### 6. Web Scraping Stack

**Purpose:** Proxy-aware, self-healing web scraping

**Engines:**
- BeautifulSoup (simple HTML)
- Crawl4AI (multi-page crawling)
- Playwright (JS rendering)
- Scrapy (spider framework)
- ScrapeGraph AI (visual crawl)
- Jobspy (job board specialized)
- WaterCrawl (agent-driven crawling)

**Proxy Infrastructure:**
- Residential proxies (BrightData/Oxylabs)
- ISP proxies
- Mobile proxies (4G LTE)
- Datacenter proxies
- Self-hosted VPS

**Features:**
- Rotating proxy pool
- Behavioral stealth (ghost-cursor, UA rotation)
- Self-healing selectors (agent fixes failing selectors)
- Change detection (DOM diffing)
- Deduplication (content checksums)
- Per-domain behavior profiles

**Database Models:**
- `ScrapeJob` - Scraping job record
- `ScrapeResult` - Scraped content
- `ProxyLog` - Proxy usage logs
- `DomainProfile` - Domain-specific behavior
- `ContentChecksum` - Deduplication tracking

**API Endpoints:**
- `POST /scraping/scrape` - Scrape single URL
- `POST /scraping/crawl` - Multi-page crawl
- `GET /scraping/status/{job_id}` - Job status
- `POST /scraping/change-detection` - Monitor page changes

### 7. Browser Automation Stack

**Purpose:** Multi-engine browser automation

**Engines:**
- Playwright (JS-heavy pages)
- Puppeteer (headless Chrome)
- browser-use.com (lightweight)
- AI Browser Agent (LLM-guided)
- Browserbase/Stagehand (fleet-scale)
- Undetected-Chromedriver (anti-bot)
- Cloudscraper (Cloudflare bypass)

**Features:**
- Autonomous browser agent
- Change watcher (ChangeDetection.io)
- RAG Helper Clicker (predefined flow)
- Proxy & stealth middleware (shared with scraping)
- Screenshot capture
- DOM extraction

**Database Models:**
- `BrowserSession` - Browser session record
- `BrowserAction` - Action logs
- `ChangeDetection` - DOM change tracking

**API Endpoints:**
- `POST /browser/execute` - Execute browser action
- `POST /browser/monitor` - Monitor page changes
- `GET /browser/session/{session_id}` - Session details

### 8. OSINT Stack

**Purpose:** Social monitoring and intelligence gathering

**Engines:**
- Twint (Twitter, no API)
- Tweepy (Twitter, with API)
- Social-Listener (live Telegram/Reddit)
- NewsCatcher (blog/news crawl)
- Huginn (scheduled digests)

**Features:**
- Live stream adapter (WebSocket-like)
- Historical backfill engine
- Noise filtering & deduplication
- Structured output schema
- Alert system

**Database Models:**
- `OSINTStream` - Stream configuration
- `OSINTAlert` - Alert records
- `OSINTSignal` - Signal data

**API Endpoints:**
- `POST /osint/stream` - Start live stream
- `POST /osint/digest` - Historical digest
- `GET /osint/alerts` - List alerts

### 9. Custom Code Execution

**Purpose:** Secure code execution in workflows

**Runtimes:**
- E2B (fast, <50ms)
- WasmEdge (secure WASM)
- Bacalhau (distributed/GPU)
- Cline Node (JS/TS persistent)
- MCP Server (multi-tenant)

**Features:**
- Inline code node (Monaco editor)
- Sandbox code agent studio
- ETL integration hooks
- Tool registry & versioning
- Pydantic/Zod validation
- Cost controls

**Database Models:**
- `CodeExecution` - Execution record
- `CodeToolRegistry` - Tool registry
- `CodeSandbox` - Sandbox configuration

**API Endpoints:**
- `POST /code/execute` - Execute code
- `POST /code/register-tool` - Register tool
- `GET /code/tools` - List tools

### 10. Chat & Copilot UI (ag-ui)

**Purpose:** Conversational automation builder

**Features:**
- Embeddable widget (`<AgProvider>`)
- WebSocket bridge (`/api/agws`)
- Four-mode router:
  - `automation` - Tools-only LangGraph flow
  - `agent` - Single agent execution
  - `agent_flow` - Agent + downstream tools
  - `code` - Code sandbox execution
- Inline editors (Monaco, Clay UI)
- Dev-inspect toggle
- Real-time streaming

**API Endpoints:**
- `POST /chat` - Chat endpoint (4 modes)
- `WebSocket /api/agws` - WebSocket bridge

---

## Database Schema

### Core Models

#### Workflow Models

```python
class Workflow(SQLModel, table=True):
    id: uuid.UUID (PK)
    name: str
    description: str | None
    owner_id: uuid.UUID (FK → User)
    is_active: bool
    version: int
    trigger_config: dict (JSON)
    graph_config: dict (JSON)  # LangGraph state
    created_at: datetime
    updated_at: datetime

class WorkflowNode(SQLModel, table=True):
    id: uuid.UUID (PK)
    workflow_id: uuid.UUID (FK → Workflow)
    node_type: str
    node_id: str  # LangGraph node ID
    position_x: float
    position_y: float
    config: dict (JSON)

class WorkflowExecution(SQLModel, table=True):
    id: uuid.UUID (PK)
    workflow_id: uuid.UUID (FK → Workflow)
    workflow_version: int  # Version of workflow used for this execution
    execution_id: str (unique, indexed)  # Custom execution ID
    status: str  # running, completed, failed, paused, waiting_for_signal
    started_at: datetime
    completed_at: datetime | None
    error_message: str | None
    current_node_id: str | None  # Current executing node
    execution_state: dict (JSON)  # Full execution state snapshot
    retry_count: int (default=0)
    next_retry_at: datetime | None

class ExecutionLog(SQLModel, table=True):
    id: uuid.UUID (PK)
    execution_id: uuid.UUID (FK → WorkflowExecution)
    node_id: str
    level: str  # info, error, debug
    message: str
    timestamp: datetime

class WorkflowSchedule(SQLModel, table=True):
    id: uuid.UUID (PK)
    workflow_id: uuid.UUID (FK → Workflow)
    cron_expression: str
    is_active: bool
    next_run_at: datetime | None
    last_run_at: datetime | None

class WorkflowSignal(SQLModel, table=True):
    id: uuid.UUID (PK)
    execution_id: uuid.UUID (FK → WorkflowExecution)
    signal_type: str  # connector_ready, human_input, webhook, etc.
    signal_data: dict (JSON)
    received_at: datetime
    processed: bool (default=False)
```

#### Connector Models

```python
class Connector(SQLModel, table=True):
    id: uuid.UUID (PK)
    slug: str (unique, indexed)
    name: str
    status: str  # draft, beta, stable, deprecated
    latest_version_id: uuid.UUID | None (FK → ConnectorVersion)
    created_at: datetime

class ConnectorVersion(SQLModel, table=True):
    id: uuid.UUID (PK)
    connector_id: uuid.UUID (FK → Connector)
    version: str  # SemVer
    manifest: dict (JSONB)
    wheel_url: str | None
    created_at: datetime

class WebhookSubscription(SQLModel, table=True):
    id: uuid.UUID (PK)
    connector_version_id: uuid.UUID (FK → ConnectorVersion)
    trigger_id: str
    tenant_id: uuid.UUID
    endpoint_secret: str
    created_at: datetime
```

#### Agent Models

```python
class AgentTask(SQLModel, table=True):
    id: uuid.UUID (PK)
    agent_framework: str
    task_type: str
    status: str
    input_data: dict (JSON)
    output_data: dict (JSON) | None
    started_at: datetime
    completed_at: datetime | None
    error_message: str | None

class AgentTaskLog(SQLModel, table=True):
    id: uuid.UUID (PK)
    task_id: uuid.UUID (FK → AgentTask)
    level: str
    message: str
    timestamp: datetime
```

#### RAG Models

```python
class RAGIndex(SQLModel, table=True):
    id: uuid.UUID (PK)
    name: str
    vector_db_type: str  # chromadb, milvus, etc.
    owner_id: uuid.UUID (FK → User)
    created_at: datetime

class RAGDocument(SQLModel, table=True):
    id: uuid.UUID (PK)
    index_id: uuid.UUID (FK → RAGIndex)
    content: str
    metadata: dict (JSON)
    embedding: list[float] | None
    created_at: datetime

class RAGQuery(SQLModel, table=True):
    id: uuid.UUID (PK)
    index_id: uuid.UUID (FK → RAGIndex)
    query_text: str
    results: dict (JSON)
    latency_ms: int
    created_at: datetime
```

#### OCR Models

```python
class OCRJob(SQLModel, table=True):
    id: uuid.UUID (PK)
    document_url: str
    engine: str
    status: str
    result: dict (JSON) | None
    started_at: datetime
    completed_at: datetime | None
```

#### Scraping Models

```python
class ScrapeJob(SQLModel, table=True):
    id: uuid.UUID (PK)
    url: str
    engine: str
    proxy_id: str | None
    status: str
    result: dict (JSON) | None
    started_at: datetime
    completed_at: datetime | None

class ProxyLog(SQLModel, table=True):
    id: uuid.UUID (PK)
    ip_id: str
    agent_id: str | None
    domain_scraped: str
    status_code: int
    retry_count: int
    block_reason: str | None
    latency_ms: int
    timestamp: datetime

class DomainProfile(SQLModel, table=True):
    id: uuid.UUID (PK)
    domain: str (unique)
    max_requests_per_hour: int
    requires_login: bool
    captcha_likelihood: str
    scroll_needed: bool
    idle_before_click: float
    config: dict (JSON)
```

#### Telemetry Models

```python
class ModelCostLog(SQLModel, table=True):
    id: uuid.UUID (PK)
    agent_id: uuid.UUID | None
    model: str
    tokens_input: int
    tokens_output: int
    usd_cost: float
    created_at: datetime

class ToolUsageLog(SQLModel, table=True):
    id: uuid.UUID (PK)
    tool_id: str
    tool_type: str  # connector, ocr, scraping, etc.
    status: str
    latency_ms: int
    error_message: str | None
    created_at: datetime

class EventLog(SQLModel, table=True):
    id: uuid.UUID (PK)
    event_type: str
    context: dict (JSON)
    status: str
    created_at: datetime
```

### Indexes

**Critical indexes for performance:**
- `workflow_execution.workflow_id`
- `workflow_execution.status`
- `workflow_execution.started_at`
- `execution_log.execution_id`
- `execution_log.timestamp`
- `connector_version.connector_id`
- `agent_task_log.task_id`
- `rag_query.index_id`
- `rag_query.created_at`
- `tool_usage_log.tool_id`
- `tool_usage_log.created_at`

---

## API Specifications

### Base URL
- Development: `http://localhost:8000/api/v1`
- Production: `https://api.{domain}/api/v1`

### Authentication
- All endpoints require BetterAuth JWT token
- Header: `Authorization: Bearer <token>`
- Token validation via BetterAuth `/introspect`

### Workflow Endpoints

#### `POST /workflows`
Create new workflow

**Request:**
```json
{
  "name": "My Workflow",
  "description": "Description",
  "graph_config": {...},
  "trigger_config": {...}
}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "My Workflow",
  "version": 1,
  "created_at": "2025-01-15T10:00:00Z"
}
```

#### `POST /workflows/{workflow_id}/run`
Execute workflow

**Request:**
```json
{
  "trigger_data": {...}
}
```

**Response:**
```json
{
  "execution_id": "uuid",
  "status": "running",
  "workflow_execution_id": "exec-12345"
}
```

#### `GET /workflows/{workflow_id}/executions`
List executions

#### `GET /workflows/executions/{execution_id}/status`
Get execution status

#### `POST /workflows/executions/{execution_id}/replay`
Replay from failed step

### Connector Endpoints

#### `POST /connectors/register`
Register connector (manifest + wheel)

#### `GET /connectors/list`
List available connectors

#### `POST /connectors/{slug}/authorize`
Initiate OAuth flow

#### `POST /connectors/{slug}/{action}`
Invoke connector action

#### `POST /connectors/{slug}/webhook`
Webhook ingress - Validates signature, maps payload, emits workflow signal

### Agent Endpoints

#### `POST /agents/run`
Execute agent task

#### `GET /agents/status/{task_id}`
Get task status

#### `POST /agents/switch/evaluate`
Evaluate routing decision

### RAG Endpoints

#### `POST /rag/query`
Query RAG index

#### `POST /rag/index`
Create/update index

#### `POST /rag/switch/evaluate`
Evaluate routing

### OCR Endpoints

#### `POST /ocr/extract`
Extract text from document

#### `GET /ocr/status/{job_id}`
Get job status

### Scraping Endpoints

#### `POST /scraping/scrape`
Scrape single URL

#### `POST /scraping/crawl`
Multi-page crawl

### Browser Endpoints

#### `POST /browser/execute`
Execute browser action

#### `POST /browser/monitor`
Monitor page changes

### Chat Endpoints

#### `POST /chat`
Chat endpoint (4 modes)

**Request:**
```json
{
  "mode": "automation|agent|agent_flow|code",
  "prompt": "User prompt",
  "context": {...}
}
```

#### `WebSocket /api/agws`
WebSocket bridge for real-time events

---

## Frontend Components

### 1. Workflow Builder

**Technology:** React Flow (`@xyflow/react`)

**Features:**
- Drag-and-drop node palette
- Node configuration forms
- Real-time validation
- Zoom, pan, nesting
- Save/load workflows
- Version control UI

**Components:**
- `WorkflowCanvas.tsx` - Main canvas
- `NodePalette.tsx` - Available nodes
- `NodeConfigPanel.tsx` - Configuration
- `ExecutionPanel.tsx` - Live execution view

### 2. Chat Interface (ag-ui)

**Technology:** `@ag-ui/core`

**Features:**
- Conversational UI
- Streaming responses
- Inline editors (Monaco, Clay UI)
- Dev-inspect mode
- Tool call visualization

**Components:**
- `AgUIProvider.tsx` - Provider wrapper
- `ChatWindow.tsx` - Chat interface
- `MessageBubble.tsx` - Message display
- `ToolCallCard.tsx` - Tool call visualization

### 3. Admin Panel

**Features:**
- Execution history
- Temporal Web iframe
- Retry management
- Cost analytics
- System health

**Components:**
- `AdminDashboard.tsx` - Main dashboard
- `ExecutionHistory.tsx` - Execution list
- `TemporalWeb.tsx` - Temporal UI iframe
- `CostAnalytics.tsx` - Cost dashboard

### 4. Connector Management

**Features:**
- Connector catalog
- Registration wizard
- OAuth flow UI
- Test runner
- Documentation viewer

**Components:**
- `ConnectorCatalog.tsx` - Connector list
- `ConnectorWizard.tsx` - Registration wizard
- `OAuthModal.tsx` - OAuth flow
- `ConnectorDocs.tsx` - Documentation

---

## Integration Requirements

### 1. BetterAuth Integration

**Purpose:** Unified authentication (OAuth 2.0/OIDC + MFA + RBAC)

**Requirements:**
- JWT token validation middleware
- Session management (30min access, 14day refresh)
- RBAC: owner, editor, viewer
- MFA support
- OAuth providers: Google, GitHub, etc.

**Implementation:**
- Middleware: `app/api/middleware/auth.py`
- Dependency: `get_current_user` updated to use BetterAuth

### 2. Infisical Integration

**Purpose:** Runtime secret injection

**Requirements:**
- Store connector OAuth tokens
- Store API keys
- Tenant-scoped secrets
- Audit logging
- Key rotation

**Implementation:**
- SDK: `infisical>=0.3.0`
- Service: `app/services/secrets.py`
- Pattern: Fetch secrets at runtime, cache in memory

### 3. Custom Workflow Engine (Temporal-like)

**Purpose:** Workflow durability and orchestration

**Requirements:**
- Custom workflow engine that replicates Temporal functionality
- Workflow persistence in PostgreSQL
- Retry logic with exponential backoff
- Versioning support
- Pause/resume capability
- Signal system (for webhooks, human prompts, connector handshakes)
- CRON scheduling
- Exactly-once execution guarantees
- Execution history and audit trail

**Core Features:**
- **Durability:** All workflow state persisted in PostgreSQL
- **Retries:** Configurable retry policies with exponential backoff
- **Versioning:** Workflow versions tracked, executions use original version
- **Signals:** Event-driven workflow continuation (webhooks, user input, connector ready)
- **Scheduling:** CRON-based workflow triggers
- **History:** Complete execution history with node-level logs
- **Replay:** Ability to replay from any point in execution

**Implementation:**
- Engine: `app/workflows/engine.py` - Core workflow orchestration
- Worker: `app/workflows/worker.py` - Background worker for execution
- Scheduler: `app/workflows/scheduler.py` - CRON job scheduler
- Activities: `app/workflows/activities.py` - Node execution handlers
- Signals: `app/workflows/signals.py` - Signal handling system

### 4. LangGraph Integration

**Purpose:** Business logic orchestration

**Requirements:**
- Graph building from Workflow model
- Node execution handlers
- State management
- Error handling

**Implementation:**
- SDK: `langgraph>=0.0.20`
- Engine: `app/workflows/langgraph_engine.py`
- Nodes: `app/workflows/nodes/`

### 5. ACI.dev Integration

**Purpose:** Connector base classes

**Requirements:**
- Import `aci.clients.base`
- Extend `BaseConnector`
- OAuth flow helpers
- Action/trigger definitions

**Implementation:**
- SDK: `aci>=0.1.0` (if available)
- Base: `app/connectors/base.py`
- Connectors: `app/connectors/{provider}/`

### 6. Observability Stack

**Signoz (OpenTelemetry):**
- OTel SDK integration
- Span creation for all operations
- Trace export to Signoz

**PostHog:**
- User analytics
- Feature flags
- Funnel tracking

**Langfuse:**
- LLM call logging
- Agent thoughts
- Customer-visible traces

**Wazuh:**
- Security event logging
- Audit trail
- Alerting

---

## Security & Compliance

### Authentication & Authorization

- **BetterAuth:** OAuth 2.0/OIDC, MFA, RBAC
- **JWT Validation:** All API endpoints
- **Session Management:** 30min access, 14day refresh
- **Role-Based Access:** owner, editor, viewer

### Secrets Management

- **Infisical:** All secrets stored here
- **No Plaintext:** Never in logs, env files, or Temporal payloads
- **Runtime Injection:** Secrets fetched at execution time
- **Audit Logging:** All secret access logged
- **Key Rotation:** Supported via `/rotate` endpoint

### Data Protection

- **Encryption:** E2EE for secrets (Infisical AES-256)
- **Tenant Isolation:** RLS enforced in Supabase
- **PII Redaction:** Before external sinks
- **Compliance:** GDPR, PCI-DSS (tokenized), HIPAA opt-in

### Security Scanning

- **CI Checks:** Gitleaks, dependency scanning
- **Code Review:** Required for connector registration
- **Pen Testing:** Before production launch

---

## Observability & Monitoring

### Metrics

**Prometheus Metrics:**
- `workflow_execution_total{status}`
- `connector_request_latency_seconds{slug,action}`
- `connector_error_total{slug,action}`
- `agent_task_latency_ms{framework}`
- `rag_query_latency_ms{vector_db}`
- `ocr_job_latency_ms{engine}`
- `scrape_job_latency_ms{engine}`

### Traces

**OpenTelemetry Spans:**
- Workflow execution spans
- Node execution spans
- Connector call spans
- Agent task spans
- RAG query spans
- OCR job spans

### Logs

**Structured Logging:**
- Execution logs (PostgreSQL)
- Tool usage logs
- Event logs
- Error logs (GlitchTip)

### Dashboards

- **Signoz:** Latency, errors, traces
- **PostHog:** User analytics, funnels
- **Langfuse:** LLM calls, agent thoughts
- **Custom:** Cost analytics, system health

---

## Deployment & Infrastructure

### Docker Compose Services

```yaml
services:
  db: # PostgreSQL (Supabase)
  redis: # Redis for task queue/caching
  backend: # SynthralOS backend app
  frontend: # React app
  workflow-worker: # Custom workflow engine worker service
  scheduler: # CRON scheduler service
```

### Environment Variables

```bash
# Workflow Engine
WORKFLOW_WORKER_CONCURRENCY=10
WORKFLOW_MAX_RETRIES=3
WORKFLOW_RETRY_BACKOFF_MULTIPLIER=2.0
WORKFLOW_HISTORY_RETENTION_DAYS=30

# Infisical
INFISICAL_URL=https://app.infisical.com
INFISICAL_CLIENT_ID=...
INFISICAL_CLIENT_SECRET=...

# BetterAuth
BETTER_AUTH_URL=http://localhost:8000
BETTER_AUTH_SECRET=...

# Redis
REDIS_URL=redis://redis:6379

# Vector DBs
CHROMADB_URL=http://chromadb:8000
MILVUS_URL=localhost:19530

# Observability
SIGNOZ_ENDPOINT=http://signoz:4318
POSTHOG_KEY=...
LANGFUSE_KEY=...
```

### Kubernetes (Production)

- Horizontal Pod Autoscaling (HPA)
- Service mesh (Istio/Linkerd)
- Ingress (Traefik/Nginx)
- Persistent volumes for Temporal

---

## Development Roadmap

### Phase 1: Foundation (Weeks 1-2)
- Database models & migrations
- Custom workflow engine implementation (Temporal-like)
- LangGraph engine
- Basic API endpoints
- BetterAuth integration
- Infisical integration

### Phase 2: Core Execution (Weeks 3-4)
- Workflow execution engine
- Connector registry (ICI)
- Agent routing
- Basic observability

### Phase 3: Services (Weeks 5-6)
- OCR service
- RAG service
- Scraping service
- Browser automation

### Phase 4: Frontend (Weeks 7-8)
- Workflow builder UI
- ag-ui chat integration
- Admin panel

### Phase 5: Advanced Features (Weeks 9+)
- OSINT stack
- Custom code execution
- Advanced agent frameworks
- Performance optimization

---

## Success Metrics

### Performance Targets

- Workflow execution latency: <300ms (non-blocking)
- Agent routing latency: <500ms
- RAG query latency: <1s (p95)
- OCR job latency: <800ms (median), <4s (p95)
- Scrape job latency: <1s (median), <6s (p95)

### Reliability Targets

- Workflow success rate: ≥99.5%
- Agent task success rate: ≥95%
- OCR accuracy: ≥95%
- Scrape selector success: ≥92%

### Scalability Targets

- Concurrent executions: 1k+
- Burst TPS: 50+
- Vector DB queries: 10k/day
- Scrape jobs: 100k/day

---

## Appendix

### A. Database Migration Checklist

- [ ] Create all workflow models
- [ ] Create all connector models
- [ ] Create all agent models
- [ ] Create all RAG models
- [ ] Create all OCR models
- [ ] Create all scraping models
- [ ] Create all telemetry models
- [ ] Add indexes
- [ ] Add foreign keys
- [ ] Add constraints

### B. API Endpoint Checklist

- [ ] Workflow endpoints (6)
- [ ] Connector endpoints (8)
- [ ] Agent endpoints (4)
- [ ] RAG endpoints (6)
- [ ] OCR endpoints (3)
- [ ] Scraping endpoints (4)
- [ ] Browser endpoints (3)
- [ ] OSINT endpoints (3)
- [ ] Code endpoints (3)
- [ ] Chat endpoints (2)

### C. Frontend Component Checklist

- [ ] Workflow builder
- [ ] Chat interface (ag-ui)
- [ ] Admin panel
- [ ] Connector management
- [ ] Agent catalog
- [ ] RAG index management
- [ ] Execution history
- [ ] Cost analytics

### D. Integration Checklist

- [ ] BetterAuth
- [ ] Infisical
- [ ] Temporal
- [ ] LangGraph
- [ ] ACI.dev
- [ ] Signoz
- [ ] PostHog
- [ ] Langfuse
- [ ] Wazuh

---

**End of PRD**
