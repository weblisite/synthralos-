# Connectors Usage Guide: Where and How Connectors Are Used in SynthralOS

This comprehensive guide explains where connectors are used throughout the SynthralOS platform, how they integrate with different systems, and how users can leverage them.

## Table of Contents

1. [Overview](#overview)
2. [Where Connectors Are Used](#where-connectors-are-used)
3. [How Connectors Work](#how-connectors-work)
4. [User Flows](#user-flows)
5. [Integration Points](#integration-points)
6. [Examples](#examples)
7. [Best Practices](#best-practices)

---

## Overview

Connectors are the **bridge between SynthralOS and external SaaS services**. They enable the platform to:
- **Send data** to external services (actions)
- **Receive data** from external services (triggers/webhooks)
- **Authenticate** securely via OAuth
- **Integrate** seamlessly into workflows, agents, and automation

### Key Concepts

- **Actions**: Operations you can perform (e.g., "send_email", "create_ticket")
- **Triggers**: Events from external services (e.g., "new_email", "ticket_created")
- **OAuth**: Secure authentication without sharing passwords
- **Manifest**: Connector metadata (name, actions, triggers, OAuth config)

---

## Where Connectors Are Used

Connectors are integrated into **5 major areas** of SynthralOS:

### 1. **Workflows** (Primary Use Case)

**Location**: `backend/app/workflows/` and `frontend/src/components/Workflow/`

**How They're Used:**
- Connectors appear as **nodes** in the visual workflow builder
- Users drag connector nodes onto the canvas
- Each connector node can invoke actions or listen to triggers
- Workflow execution engine calls connector actions during workflow runs

**Example Workflow:**
```
[Webhook Trigger] → [Gmail: Send Email] → [Slack: Post Message] → [End]
```

**Code Integration:**
```python
# backend/app/workflows/nodes/connector_node.py (conceptual)
class ConnectorNode:
    def execute(self, state):
        # Get connector from registry
        connector = registry.get_connector(self.connector_slug)
        
        # Invoke action
        result = connector_loader.invoke_action(
            connector_version=connector,
            action_id=self.action_id,
            input_data=self.input_data,
            credentials=self.get_credentials()
        )
        
        return result
```

**User Experience:**
1. User opens Workflow Builder (`/workflows`)
2. Drags "Gmail" connector from node palette
3. Configures node: action="send_email", to="{{trigger.data.email}}"
4. Connects to other nodes
5. Saves and runs workflow

---

### 2. **AI Agents** (Tool Calling)

**Location**: `backend/app/agents/` and `frontend/src/components/Agents/`

**How They're Used:**
- Agents can **automatically discover** available connectors
- Agents use connectors as **tools** during task execution
- When an agent needs to interact with an external service, it calls the connector action
- Connectors are exposed to agents via the tool registry

**Example Agent Task:**
```
User: "Send an email to john@synthralos.ai with subject 'Meeting'"
Agent: 
  1. Identifies need for Gmail connector
  2. Checks if Gmail is authorized
  3. If not authorized, prompts user: "NeedConnector(gmail)"
  4. Once authorized, invokes: gmail.send_email(to="john@synthralos.ai", subject="Meeting")
```

**Code Integration:**
```python
# backend/app/agents/router.py (conceptual)
class AgentRouter:
    def run_task(self, task):
        # Agent framework discovers available tools
        tools = self.get_available_tools()  # Includes connectors
        
        # Agent decides to use connector
        if agent_needs_connector:
            connector_tool = self.get_connector_tool("gmail", "send_email")
            result = agent.execute_with_tool(connector_tool, task)
        
        return result
```

**User Experience:**
1. User opens Chat (`/chat`)
2. Selects "agent" mode
3. Types: "Send an email to support@synthralos.ai"
4. Agent automatically uses Gmail connector (if authorized)
5. If not authorized, agent prompts: "Please authorize Gmail connector"

---

### 3. **Chat Interface** (Conversational Automation)

**Location**: `backend/app/api/routes/chat.py` and `frontend/src/components/Chat/`

**How They're Used:**
- Chat can invoke connectors directly via `/connect <provider>` command
- Chat processor can automatically use connectors based on user intent
- Connectors are exposed as "tools" that the chat can call

**Example Chat Interaction:**
```
User: "/connect gmail"
System: "Redirecting to Gmail authorization..."

User: "Send an email to team@synthralos.ai"
System: 
  1. Detects email intent
  2. Uses Gmail connector
  3. Sends email
  4. Confirms: "Email sent successfully"
```

**Code Integration:**
```python
# backend/app/services/chat_processor.py (conceptual)
class ChatProcessor:
    def process_message(self, message, mode):
        if message.startswith("/connect"):
            connector_slug = message.split()[1]
            return self.initiate_oauth(connector_slug)
        
        # Detect intent
        if self.detects_email_intent(message):
            connector = self.get_connector("gmail")
            return connector.invoke_action("send_email", message_data)
```

**User Experience:**
1. User opens Chat (`/chat`)
2. Types: "/connect gmail"
3. Redirected to OAuth flow
4. Returns to chat, now can use Gmail commands
5. Types: "Send email to..." → Connector automatically invoked

---

### 4. **Direct API Calls** (Programmatic Access)

**Location**: `backend/app/api/routes/connectors.py`

**How They're Used:**
- Developers can call connector actions directly via REST API
- Useful for custom integrations and testing
- Frontend components can call connectors directly

**Example API Call:**
```bash
POST /api/v1/connectors/gmail/send_email
{
  "to": "recipient@synthralos.ai",
  "subject": "Hello",
  "body": "Test email"
}
```

**Code Integration:**
```python
# backend/app/api/routes/connectors.py
@router.post("/{slug}/{action}")
def invoke_connector_action(
    slug: str,
    action: str,
    input_data: dict[str, Any],
    current_user: CurrentUser,
):
    # Get connector
    connector_version = registry.get_connector(slug)
    
    # Get user's OAuth tokens
    tokens = oauth_service.get_tokens(slug, current_user.id)
    
    # Invoke action
    result = connector_loader.invoke_action(
        connector_version=connector_version,
        action_id=action,
        input_data=input_data,
        credentials=tokens
    )
    
    return result
```

**User Experience:**
1. User opens Connector Catalog (`/connectors`)
2. Clicks "View" on Gmail connector
3. Sees available actions
4. Clicks "Test" on "send_email" action
5. Fills in test data
6. Clicks "Run Test" → API call made directly

---

### 5. **Webhooks** (Event Triggers)

**Location**: `backend/app/connectors/webhook.py` and `backend/app/api/routes/connectors.py`

**How They're Used:**
- External services send webhooks to SynthralOS
- Webhook service validates signatures
- Webhook payload is mapped to workflow signals
- Workflows can be triggered by connector events

**Example Webhook Flow:**
```
1. User creates webhook subscription: "When new email arrives"
2. Gmail sends webhook to: POST /api/v1/connectors/gmail/webhook
3. Webhook service validates signature
4. Emits workflow signal: "gmail.new_email"
5. Workflow listening to signal starts execution
```

**Code Integration:**
```python
# backend/app/connectors/webhook.py
class ConnectorWebhookService:
    def handle_webhook(self, connector_slug, payload, signature):
        # Validate signature
        self.validate_signature(connector_slug, payload, signature)
        
        # Map to workflow signal
        signal = self.map_to_signal(connector_slug, payload)
        
        # Emit signal to workflow engine
        workflow_engine.emit_signal(signal)
```

**User Experience:**
1. User creates workflow with Gmail trigger node
2. System automatically creates webhook subscription
3. When new email arrives, webhook is received
4. Workflow automatically starts
5. User sees workflow execution in dashboard

---

## How Connectors Work

### Architecture Overview

```
┌─────────────┐
│   User      │
│  (Frontend) │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│      Connector API Endpoints       │
│  (POST /connectors/{slug}/{action})│
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│    Connector Registry              │
│  (Manifest Lookup & Versioning)    │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│    Connector Hot Loader            │
│  (Loads & Executes Connector Code) │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│    OAuth Service                    │
│  (Nango or Direct OAuth)           │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│    External Service API            │
│  (Gmail, Slack, etc.)              │
└─────────────────────────────────────┘
```

### Component Breakdown

#### 1. **Connector Registry** (`backend/app/connectors/registry.py`)

**Purpose**: Manages connector metadata and versions

**Responsibilities:**
- Store connector manifests
- Version management (SemVer)
- List available connectors
- Get connector by slug/version

**Key Methods:**
```python
registry.list_connectors()  # Get all connectors
registry.get_connector(slug)  # Get specific connector
registry.get_connector_actions(slug)  # Get available actions
```

#### 2. **Connector Hot Loader** (`backend/app/connectors/loader.py`)

**Purpose**: Dynamically loads and executes connector code

**Responsibilities:**
- Load connector wheels (Python packages)
- Isolate connector code (security)
- Invoke connector methods
- Handle errors gracefully

**Key Methods:**
```python
loader.invoke_action(connector_version, action_id, input_data, credentials)
loader.invoke_trigger(connector_version, trigger_id, input_data, credentials)
```

#### 3. **OAuth Service** (`backend/app/connectors/oauth.py`)

**Purpose**: Manages OAuth authentication

**Responsibilities:**
- Generate authorization URLs (Nango or direct)
- Handle OAuth callbacks
- Store/refresh tokens
- Inject credentials into connector calls

**Key Methods:**
```python
oauth_service.generate_authorization_url(connector_slug, user_id, redirect_uri)
oauth_service.handle_callback(state, code)
oauth_service.get_tokens(connector_slug, user_id)
oauth_service.refresh_tokens(connector_slug, user_id)
```

#### 4. **Webhook Service** (`backend/app/connectors/webhook.py`)

**Purpose**: Handles incoming webhooks from external services

**Responsibilities:**
- Validate webhook signatures
- Map webhook payloads to workflow signals
- Emit signals to workflow engine
- Manage webhook subscriptions

**Key Methods:**
```python
webhook_service.handle_webhook(connector_slug, payload, signature)
webhook_service.subscribe(connector_slug, webhook_config)
```

---

## User Flows

### Flow 1: Authorizing a Connector

**Step-by-Step:**

1. **User browses connectors**
   - Navigates to `/connectors`
   - Sees list of 99 available connectors
   - Filters by category (e.g., "Communication & Collaboration")

2. **User selects connector**
   - Clicks "View" on Gmail connector
   - Sees connector details: description, actions, triggers
   - Sees status: "Not Authorized" or "Authorized"

3. **User initiates OAuth**
   - Clicks "Authorize" button
   - System calls: `POST /api/v1/connectors/gmail/authorize`
   - Returns authorization URL (Nango or direct OAuth)

4. **User authorizes**
   - Redirected to Gmail OAuth page
   - Grants permissions
   - Redirected back to callback URL

5. **System completes OAuth**
   - Callback: `GET /api/v1/connectors/gmail/callback?code=...&state=...`
   - System exchanges code for tokens
   - Stores tokens securely (Nango or database)
   - Updates UI: "Authorized ✅"

**Code Flow:**
```python
# Frontend
const authResponse = await fetch('/api/v1/connectors/gmail/authorize', {
  method: 'POST',
  body: JSON.stringify({ redirect_uri: window.location.origin + '/callback' })
})

// Redirect user
window.location.href = authResponse.authorization_url

# Backend (OAuth Service)
def generate_authorization_url(connector_slug, user_id, redirect_uri):
    if use_nango:
        return nango_service.generate_authorization_url(...)
    else:
        return direct_oauth.generate_authorization_url(...)
```

---

### Flow 2: Using Connector in Workflow

**Step-by-Step:**

1. **User creates workflow**
   - Navigates to `/workflows`
   - Clicks "Create Workflow"
   - Opens workflow builder

2. **User adds connector node**
   - Drags "Gmail" connector from node palette
   - Drops onto canvas
   - Node appears: "Gmail Connector"

3. **User configures node**
   - Clicks node to open config panel
   - Selects action: "send_email"
   - Configures parameters:
     - `to`: "{{trigger.data.email}}"
     - `subject`: "Welcome!"
     - `body`: "Thanks for signing up"

4. **User connects nodes**
   - Connects webhook trigger → Gmail node → End node
   - Workflow: "When webhook received → Send email"

5. **User saves workflow**
   - Clicks "Save"
   - Workflow stored with connector node configuration

6. **User runs workflow**
   - Clicks "Run"
   - Workflow engine executes:
     - Receives webhook trigger
     - Executes Gmail node
     - Calls: `POST /api/v1/connectors/gmail/send_email`
     - Returns result

**Code Flow:**
```python
# Workflow Engine
def execute_node(node):
    if node.type == "connector":
        connector_slug = node.config.connector_slug
        action_id = node.config.action_id
        input_data = node.config.input_data
        
        # Get connector
        connector = registry.get_connector(connector_slug)
        
        # Get user's tokens
        tokens = oauth_service.get_tokens(connector_slug, user_id)
        
        # Invoke action
        result = loader.invoke_action(
            connector_version=connector,
            action_id=action_id,
            input_data=input_data,
            credentials=tokens
        )
        
        return result
```

---

### Flow 3: Agent Using Connector Automatically

**Step-by-Step:**

1. **User starts agent task**
   - Opens Chat (`/chat`)
   - Selects "agent" mode
   - Types: "Send an email to support@synthralos.ai saying 'Hello'"

2. **Agent processes request**
   - Agent framework analyzes task
   - Identifies need for email connector
   - Checks available tools (includes connectors)

3. **Agent checks authorization**
   - Agent checks: "Is Gmail authorized?"
   - If not authorized:
     - Agent emits: `NeedConnector(gmail)`
     - UI shows: "Please authorize Gmail connector"
     - User authorizes (see Flow 1)

4. **Agent invokes connector**
   - Agent calls connector action
   - `POST /api/v1/connectors/gmail/send_email`
   - With parameters extracted from user message

5. **Agent returns result**
   - Connector returns: `{ "success": true, "message_id": "..." }`
   - Agent formats response: "Email sent successfully!"

**Code Flow:**
```python
# Agent Router
def run_task(task):
    # Agent discovers tools
    tools = get_available_tools()  # Includes connectors
    
    # Agent decides to use connector
    if agent_needs_email:
        connector_tool = get_connector_tool("gmail", "send_email")
        
        # Check authorization
        if not is_authorized("gmail", user_id):
            return {"need_connector": "gmail"}
        
        # Invoke
        result = connector_tool.invoke(task.extracted_params)
        return {"result": result}
```

---

### Flow 4: Webhook Triggering Workflow

**Step-by-Step:**

1. **User creates workflow with trigger**
   - Creates workflow with Gmail trigger node
   - Configures: "When new email arrives"

2. **System creates webhook subscription**
   - System calls connector webhook subscription API
   - Creates webhook endpoint: `/api/v1/connectors/gmail/webhook`
   - Stores subscription in database

3. **External service sends webhook**
   - Gmail sends POST request to webhook endpoint
   - Payload: `{ "event": "new_email", "email": {...} }`

4. **System processes webhook**
   - Webhook service validates signature
   - Maps payload to workflow signal
   - Emits signal: `gmail.new_email`

5. **Workflow engine receives signal**
   - Workflow listening to signal starts execution
   - Executes workflow nodes
   - User sees execution in dashboard

**Code Flow:**
```python
# Webhook Endpoint
@router.post("/{slug}/webhook")
def handle_webhook(slug, payload, signature):
    # Validate
    webhook_service.validate_signature(slug, payload, signature)
    
    # Map to signal
    signal = webhook_service.map_to_signal(slug, payload)
    
    # Emit to workflow engine
    workflow_engine.emit_signal(signal)
    
    return {"success": True}

# Workflow Engine
def on_signal_received(signal):
    # Find workflows listening to signal
    workflows = get_workflows_by_signal(signal.name)
    
    # Start executions
    for workflow in workflows:
        start_execution(workflow.id, trigger_data=signal.data)
```

---

## Integration Points

### 1. Workflow Engine Integration

**File**: `backend/app/workflows/engine.py` and `backend/app/workflows/nodes/`

**How It Works:**
- Workflow nodes can be of type "connector"
- Node configuration includes: `connector_slug`, `action_id`, `input_data`
- During execution, engine calls connector API endpoint
- Result is passed to next node

**Example Node Configuration:**
```json
{
  "id": "node-1",
  "type": "connector",
  "config": {
    "connector_slug": "gmail",
    "action_id": "send_email",
    "input_data": {
      "to": "{{trigger.data.email}}",
      "subject": "Welcome"
    }
  }
}
```

### 2. Agent Framework Integration

**File**: `backend/app/agents/router.py`

**How It Works:**
- Agents have access to "tool registry"
- Connectors are registered as tools
- Agents can discover and use connectors automatically
- Authorization is checked before invocation

**Example Tool Registration:**
```python
# Connector registered as tool
tool = {
    "name": "gmail_send_email",
    "description": "Send email via Gmail",
    "connector_slug": "gmail",
    "action_id": "send_email"
}

agent_tool_registry.register(tool)
```

### 3. Chat Interface Integration

**File**: `backend/app/services/chat_processor.py`

**How It Works:**
- Chat processor can detect connector-related commands
- `/connect <provider>` command initiates OAuth
- Chat can invoke connectors based on user intent
- Results are formatted for display

**Example Chat Command:**
```
User: "/connect gmail"
System: "Redirecting to Gmail authorization..."

User: "Send email to team@synthralos.ai"
System: [Invokes Gmail connector] "Email sent!"
```

### 4. Frontend Component Integration

**Files**: 
- `frontend/src/components/Connectors/ConnectorCatalog.tsx`
- `frontend/src/components/Workflow/WorkflowBuilder.tsx`
- `frontend/src/components/Chat/`

**How It Works:**
- ConnectorCatalog displays available connectors
- WorkflowBuilder includes connectors in node palette
- Chat interface can trigger connector actions
- OAuth modals handle authorization flows

---

## Examples

### Example 1: Email Notification Workflow

**Use Case**: Send email when webhook received

**Workflow:**
```
[Webhook Trigger] → [Gmail: Send Email] → [End]
```

**Configuration:**
- Webhook Trigger: Receives `{ "email": "user@synthralos.ai" }`
- Gmail Node:
  - Action: `send_email`
  - To: `{{trigger.data.email}}`
  - Subject: "Welcome!"
  - Body: "Thanks for signing up"

**Execution:**
1. Webhook received with email data
2. Gmail node executes
3. Calls: `POST /api/v1/connectors/gmail/send_email`
4. Email sent
5. Workflow completes

### Example 2: Multi-Service Integration

**Use Case**: When ticket created → Send email + Post to Slack

**Workflow:**
```
[Zendesk: Ticket Created] → [Gmail: Send Email] → [Slack: Post Message] → [End]
```

**Configuration:**
- Zendesk Trigger: `ticket_created`
- Gmail Node: Send email to ticket creator
- Slack Node: Post message to #support channel

**Execution:**
1. Zendesk webhook received
2. Gmail node sends email
3. Slack node posts message
4. Workflow completes

### Example 3: Agent Automation

**Use Case**: Agent automatically uses connectors

**User Request:**
```
"Research competitors and send findings to team@synthralos.ai"
```

**Agent Process:**
1. Agent uses web scraping connector to research
2. Agent uses Gmail connector to send email
3. Agent formats findings and sends

**Result:**
- Email sent with research findings
- User sees: "Research completed and email sent!"

---

## Best Practices

### 1. **Authorization Management**

- **Always check authorization** before invoking connectors
- **Handle authorization errors** gracefully
- **Prompt users** to authorize when needed
- **Refresh tokens** automatically when expired

### 2. **Error Handling**

- **Validate input data** before invoking connectors
- **Handle API errors** from external services
- **Retry failed requests** with exponential backoff
- **Log errors** for debugging

### 3. **Security**

- **Never store credentials** in plaintext
- **Use OAuth** for authentication
- **Validate webhook signatures**
- **Isolate connector code** (hot loader)

### 4. **Performance**

- **Cache connector manifests**
- **Lazy load connector wheels**
- **Use connection pooling** for external APIs
- **Monitor connector latency**

### 5. **User Experience**

- **Show connector status** (authorized/not authorized)
- **Provide clear error messages**
- **Guide users** through OAuth flows
- **Test connectors** before using in production

---

## Summary

Connectors are the **foundation of SynthralOS integrations**. They enable:

1. **Workflows** to interact with external services
2. **Agents** to use connectors as tools
3. **Chat** to invoke connectors conversationally
4. **Webhooks** to trigger workflows from external events
5. **Direct API** access for programmatic use

Users can leverage connectors through:
- **Visual workflow builder** (drag-and-drop)
- **Chat interface** (conversational)
- **API endpoints** (programmatic)
- **Agent automation** (automatic)

All connectors use **OAuth for security**, **Nango for unified management**, and **hot loading for flexibility**.

---

## Additional Resources

- [Connector Guide](./CONNECTORS_GUIDE.md) - How to use connectors
- [Nango Integration](./NANGO_INTEGRATION.md) - OAuth management
- [API Documentation](../backend/app/api/routes/connectors.py) - API reference
- [Workflow Examples](./EXAMPLES.md) - Example workflows

