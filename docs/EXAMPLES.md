# SynthralOS Examples

This document provides practical examples for using SynthralOS features including workflows, connectors, agents, and more.

## Table of Contents

1. [Workflow Examples](#workflow-examples)
2. [Connector Examples](#connector-examples)
3. [Agent Examples](#agent-examples)
4. [RAG Examples](#rag-examples)
5. [OCR Examples](#ocr-examples)
6. [Scraping Examples](#scraping-examples)
7. [Browser Automation Examples](#browser-automation-examples)
8. [OSINT Examples](#osint-examples)
9. [Code Execution Examples](#code-execution-examples)

---

## Workflow Examples

### Example 1: Simple Email Notification Workflow

A workflow that sends an email notification when triggered.

**Workflow Configuration:**
```json
{
  "name": "Email Notification Workflow",
  "description": "Sends email notification on trigger",
  "trigger_config": {
    "type": "webhook",
    "webhook_path": "/webhook/email-notification"
  },
  "graph_config": {
    "nodes": [
      {
        "id": "trigger-1",
        "type": "trigger",
        "config": {
          "trigger_type": "webhook"
        }
      },
      {
        "id": "email-1",
        "type": "connector",
        "config": {
          "connector_slug": "smtp",
          "action": "send_email",
          "parameters": {
            "to": "{{trigger.data.email}}",
            "subject": "Notification",
            "body": "{{trigger.data.message}}"
          }
        }
      }
    ],
    "edges": [
      {
        "source": "trigger-1",
        "target": "email-1"
      }
    ]
  }
}
```

**API Request:**
```bash
curl -X POST http://localhost:8000/api/v1/workflows/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Email Notification Workflow",
    "description": "Sends email notification on trigger",
    "trigger_config": {
      "type": "webhook",
      "webhook_path": "/webhook/email-notification"
    },
    "graph_config": {
      "nodes": [...],
      "edges": [...]
    }
  }'
```

### Example 2: Data Processing Pipeline

A workflow that scrapes data, processes it with OCR, stores in RAG, and sends results.

**Workflow Configuration:**
```json
{
  "name": "Data Processing Pipeline",
  "description": "Scrape → OCR → RAG → Notify",
  "trigger_config": {
    "type": "cron",
    "cron_expression": "0 9 * * *"
  },
  "graph_config": {
    "nodes": [
      {
        "id": "trigger-1",
        "type": "trigger",
        "config": {
          "trigger_type": "cron",
          "cron_expression": "0 9 * * *"
        }
      },
      {
        "id": "scrape-1",
        "type": "scraping",
        "config": {
          "url": "https://synthralos.ai/data",
          "engine": "playwright"
        }
      },
      {
        "id": "ocr-1",
        "type": "ocr_switch",
        "config": {
          "document_url": "{{scrape-1.result.document_url}}",
          "auto_select_engine": true
        }
      },
      {
        "id": "rag-1",
        "type": "rag_switch",
        "config": {
          "index_id": "data-index",
          "query_text": "{{ocr-1.result.text}}",
          "auto_select_db": true
        }
      },
      {
        "id": "notify-1",
        "type": "connector",
        "config": {
          "connector_slug": "slack",
          "action": "send_message",
          "parameters": {
            "channel": "#alerts",
            "message": "Processing complete: {{rag-1.result}}"
          }
        }
      }
    ],
    "edges": [
      {"source": "trigger-1", "target": "scrape-1"},
      {"source": "scrape-1", "target": "ocr-1"},
      {"source": "ocr-1", "target": "rag-1"},
      {"source": "rag-1", "target": "notify-1"}
    ]
  }
}
```

### Example 3: Conditional Workflow with Logic Nodes

A workflow that processes data conditionally based on content.

**Workflow Configuration:**
```json
{
  "name": "Conditional Processing",
  "graph_config": {
    "nodes": [
      {
        "id": "trigger-1",
        "type": "trigger"
      },
      {
        "id": "scrape-1",
        "type": "scraping",
        "config": {
          "url": "{{trigger.data.url}}"
        }
      },
      {
        "id": "condition-1",
        "type": "condition",
        "config": {
          "condition": "{{scrape-1.result.content.length}} > 1000",
          "true_path": "rag-1",
          "false_path": "notify-small"
        }
      },
      {
        "id": "rag-1",
        "type": "rag_switch",
        "config": {
          "index_id": "large-content-index",
          "query_text": "{{scrape-1.result.content}}"
        }
      },
      {
        "id": "notify-small",
        "type": "connector",
        "config": {
          "connector_slug": "email",
          "action": "send",
          "parameters": {
            "to": "admin@synthralos.ai",
            "subject": "Small content detected",
            "body": "Content too small for processing"
          }
        }
      }
    ],
    "edges": [
      {"source": "trigger-1", "target": "scrape-1"},
      {"source": "scrape-1", "target": "condition-1"},
      {"source": "condition-1", "target": "rag-1", "condition": "true"},
      {"source": "condition-1", "target": "notify-small", "condition": "false"}
    ]
  }
}
```

---

## Connector Examples

### Example 1: Register a Custom Connector

Register a new connector with manifest and wheel file.

**Connector Manifest:**
```json
{
  "name": "Custom Slack Connector",
  "slug": "slack-custom",
  "version": "1.0.0",
  "description": "Custom Slack integration for SynthralOS",
  "categories": ["communication", "notifications"],
  "logo_url": "https://synthralos.ai/logo.png",
  "oauth": {
    "authorization_url": "https://slack.com/oauth/authorize",
    "token_url": "https://slack.com/api/oauth.access",
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET",
    "scopes": ["chat:write", "channels:read"]
  },
  "actions": {
    "send_message": {
      "name": "Send Message",
      "description": "Send a message to a Slack channel",
      "input_schema": {
        "type": "object",
        "properties": {
          "channel": {
            "type": "string",
            "description": "Channel name or ID"
          },
          "message": {
            "type": "string",
            "description": "Message text"
          }
        },
        "required": ["channel", "message"]
      },
      "output_schema": {
        "type": "object",
        "properties": {
          "ts": {
            "type": "string",
            "description": "Message timestamp"
          },
          "ok": {
            "type": "boolean",
            "description": "Success status"
          }
        }
      }
    }
  },
  "triggers": {
    "message_received": {
      "name": "Message Received",
      "description": "Triggered when a message is received",
      "output_schema": {
        "type": "object",
        "properties": {
          "channel": {"type": "string"},
          "user": {"type": "string"},
          "text": {"type": "string"},
          "ts": {"type": "string"}
        }
      }
    }
  }
}
```

**API Request:**
```bash
curl -X POST http://localhost:8000/api/v1/connectors/register \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "manifest": {
      "name": "Custom Slack Connector",
      "slug": "slack-custom",
      "version": "1.0.0",
      ...
    },
    "wheel_url": "https://synthralos.ai/slack-connector-1.0.0-py3-none-any.whl"
  }'
```

### Example 2: Invoke Connector Action

Invoke an action on a registered connector.

**API Request:**
```bash
curl -X POST http://localhost:8000/api/v1/connectors/slack-custom/send_message \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "#general",
    "message": "Hello from SynthralOS!"
  }'
```

### Example 3: OAuth Authorization Flow

Authorize a connector for OAuth access.

**Step 1: Initiate OAuth**
```bash
curl -X POST http://localhost:8000/api/v1/connectors/slack-custom/authorize \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "authorization_url": "https://slack.com/oauth/authorize?client_id=...&redirect_uri=...&state=...",
  "state": "random-state-token"
}
```

**Step 2: User authorizes in browser, then callback:**
```bash
curl -X GET "http://localhost:8000/api/v1/connectors/slack-custom/callback?code=AUTH_CODE&state=random-state-token" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Agent Examples

### Example 1: Simple Agent Task

Execute a simple agent task using auto-selected framework.

**API Request:**
```bash
curl -X POST http://localhost:8000/api/v1/agents/run \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "research",
    "input_data": {
      "topic": "Latest developments in AI",
      "depth": "summary"
    },
    "task_requirements": {
      "agent_type": "simple",
      "user_prefers_copilot_ui": true
    }
  }'
```

**Response:**
```json
{
  "id": "task-uuid",
  "agent_framework": "agentgpt",
  "task_type": "research",
  "status": "running",
  "started_at": "2025-01-15T10:00:00Z"
}
```

### Example 2: Multi-Agent Task with CrewAI

Execute a task requiring multiple agents with different roles.

**API Request:**
```bash
curl -X POST http://localhost:8000/api/v1/agents/run \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "content_creation",
    "input_data": {
      "topic": "Write a blog post about automation",
      "target_audience": "developers"
    },
    "task_requirements": {
      "agent_roles": 3,
      "recursive_planning": false
    }
  }'
```

The router will automatically select CrewAI for multi-agent tasks.

### Example 3: Self-Healing Agent with Archon

Execute a task with self-healing capabilities.

**API Request:**
```bash
curl -X POST http://localhost:8000/api/v1/agents/run \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "web_scraping",
    "input_data": {
      "url": "https://synthralos.ai",
      "selectors": [".content", ".title"]
    },
    "task_requirements": {
      "agent_self_fix": true,
      "recursive_planning": true
    }
  }'
```

### Example 4: Check Agent Task Status

Get the status and results of an agent task.

**API Request:**
```bash
curl -X GET http://localhost:8000/api/v1/agents/status/task-uuid \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "id": "task-uuid",
  "agent_framework": "agentgpt",
  "task_type": "research",
  "status": "completed",
  "started_at": "2025-01-15T10:00:00Z",
  "completed_at": "2025-01-15T10:05:30Z",
  "duration_ms": 330000,
  "output_data": {
    "response": "AI developments summary...",
    "tool_calls": [
      {
        "name": "web_search",
        "arguments": {"query": "AI developments 2025"},
        "output": "Search results...",
        "status": "completed"
      }
    ]
  },
  "logs": [
    {
      "level": "info",
      "message": "Task started",
      "timestamp": "2025-01-15T10:00:00Z"
    },
    {
      "level": "info",
      "message": "Task completed successfully",
      "timestamp": "2025-01-15T10:05:30Z"
    }
  ]
}
```

---

## RAG Examples

### Example 1: Create RAG Index

Create a new RAG index for document storage.

**API Request:**
```bash
curl -X POST http://localhost:8000/api/v1/rag/index \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Documentation Index",
    "vector_db_type": "chromadb"
  }'
```

**Response:**
```json
{
  "id": "index-uuid",
  "name": "Documentation Index",
  "vector_db_type": "chromadb",
  "owner_id": "user-uuid",
  "created_at": "2025-01-15T10:00:00Z"
}
```

### Example 2: Index Documents

Add documents to a RAG index.

**API Request:**
```bash
curl -X POST http://localhost:8000/api/v1/rag/index/index-uuid/documents \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      {
        "content": "SynthralOS is an AI-powered automation platform...",
        "metadata": {
          "title": "Introduction",
          "category": "overview"
        }
      },
      {
        "content": "Workflows are created using the visual builder...",
        "metadata": {
          "title": "Workflows",
          "category": "features"
        }
      }
    ]
  }'
```

### Example 3: Query RAG Index

Query a RAG index for relevant documents.

**API Request:**
```bash
curl -X POST http://localhost:8000/api/v1/rag/query \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "index_id": "index-uuid",
    "query_text": "How do I create a workflow?",
    "top_k": 5,
    "query_requirements": {
      "requires_metadata": true,
      "user_plan": "free"
    }
  }'
```

**Response:**
```json
{
  "query_id": "query-uuid",
  "index_id": "index-uuid",
  "vector_db_type": "chromadb",
  "results": [
    {
      "document_id": "doc-uuid-1",
      "content": "Workflows are created using the visual builder...",
      "metadata": {
        "title": "Workflows",
        "category": "features"
      },
      "score": 0.95
    }
  ],
  "routing_reason": "Default routing to ChromaDB (lightweight, suitable for free plan)"
}
```

---

## OCR Examples

### Example 1: Extract Text from Image

Extract text from an image using auto-selected OCR engine.

**API Request:**
```bash
curl -X POST http://localhost:8000/api/v1/ocr/extract \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "document_url": "https://synthralos.ai/document.png",
    "query_requirements": {
      "layout_type": "table",
      "handwriting_detected": false
    }
  }'
```

**Response:**
```json
{
  "id": "job-uuid",
  "document_url": "https://synthralos.ai/document.png",
  "engine": "doctr",
  "status": "completed",
  "started_at": "2025-01-15T10:00:00Z",
  "completed_at": "2025-01-15T10:00:15Z",
  "result": {
    "text": "Extracted text content...",
    "confidence": 0.98,
    "layout": "table",
    "metadata": {
      "pages": 1,
      "language": "en"
    }
  }
}
```

### Example 2: Batch OCR Processing

Process multiple documents in batch.

**API Request:**
```bash
curl -X POST http://localhost:8000/api/v1/ocr/batch \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      {
        "document_url": "https://synthralos.ai/doc1.pdf",
        "engine": "paddleocr"
      },
      {
        "document_url": "https://synthralos.ai/doc2.jpg",
        "engine": "easyocr"
      }
    ]
  }'
```

---

## Scraping Examples

### Example 1: Simple Web Scraping

Scrape a single URL with auto-selected engine and proxy.

**API Request:**
```bash
curl -X POST http://localhost:8000/api/v1/scraping/scrape \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://synthralos.ai",
    "auto_select_proxy": true,
    "scrape_requirements": {
      "requires_js": true,
      "stealth_mode": true
    }
  }'
```

**Response:**
```json
{
  "id": "job-uuid",
  "url": "https://synthralos.ai",
  "engine": "playwright",
  "proxy_id": "proxy-uuid",
  "status": "completed",
  "started_at": "2025-01-15T10:00:00Z",
  "completed_at": "2025-01-15T10:00:05Z",
  "result": {
    "content": "Scraped HTML content...",
    "html": "<html>...</html>",
    "metadata": {
      "title": "Example Page",
      "status_code": 200
    }
  }
}
```

### Example 2: Multi-URL Crawling

Crawl multiple URLs with Scrapy.

**API Request:**
```bash
curl -X POST http://localhost:8000/api/v1/scraping/crawl \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://synthralos.ai/page1",
      "https://synthralos.ai/page2",
      "https://synthralos.ai/page3"
    ],
    "engine": "scrapy",
    "scrape_requirements": {
      "follow_links": true,
      "max_depth": 2
    }
  }'
```

---

## Browser Automation Examples

### Example 1: Create Browser Session

Create a browser session for automation.

**API Request:**
```bash
curl -X POST http://localhost:8000/api/v1/browser/session \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "browser_tool": "playwright",
    "auto_select_proxy": true,
    "automation_requirements": {
      "headless": true,
      "stealth_mode": true
    }
  }'
```

**Response:**
```json
{
  "id": "session-uuid",
  "session_id": "browser-session-id",
  "browser_tool": "playwright",
  "proxy_id": "proxy-uuid",
  "status": "active",
  "started_at": "2025-01-15T10:00:00Z"
}
```

### Example 2: Execute Browser Actions

Execute actions in a browser session.

**API Request:**
```bash
curl -X POST http://localhost:8000/api/v1/browser/session/session-uuid/execute \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action_type": "navigate",
    "action_data": {
      "url": "https://synthralos.ai"
    }
  }'
```

**Follow-up Actions:**
```bash
# Click an element
curl -X POST http://localhost:8000/api/v1/browser/session/session-uuid/execute \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action_type": "click",
    "action_data": {
      "selector": "button.submit"
    }
  }'

# Fill a form field
curl -X POST http://localhost:8000/api/v1/browser/session/session-uuid/execute \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action_type": "fill",
    "action_data": {
      "selector": "input[name=\"email\"]",
      "value": "user@synthralos.ai"
    }
  }'

# Take a screenshot
curl -X POST http://localhost:8000/api/v1/browser/session/session-uuid/execute \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action_type": "screenshot",
    "action_data": {
      "full_page": true
    }
  }'
```

### Example 3: Monitor Page Changes

Monitor a page for changes.

**API Request:**
```bash
curl -X POST http://localhost:8000/api/v1/browser/monitor \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://synthralos.ai/monitor",
    "check_interval_seconds": 60
  }'
```

---

## OSINT Examples

### Example 1: Create OSINT Stream

Create a live stream for monitoring social media.

**API Request:**
```bash
curl -X POST http://localhost:8000/api/v1/osint/stream \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "twitter",
    "keywords": ["AI", "automation", "SynthralOS"],
    "requirements": {
      "real_time": true,
      "filter_retweets": true
    }
  }'
```

**Response:**
```json
{
  "id": "stream-uuid",
  "platform": "twitter",
  "keywords": ["AI", "automation", "SynthralOS"],
  "engine": "tweepy",
  "is_active": true,
  "created_at": "2025-01-15T10:00:00Z"
}
```

### Example 2: Historical OSINT Digest

Get historical data for keywords.

**API Request:**
```bash
curl -X POST http://localhost:8000/api/v1/osint/digest \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "twitter",
    "keywords": ["AI developments"],
    "date_range": {
      "start": "2025-01-01",
      "end": "2025-01-15"
    }
  }'
```

### Example 3: List OSINT Alerts

Get alerts from OSINT streams.

**API Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/osint/alerts?stream_id=stream-uuid&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Code Execution Examples

### Example 1: Execute Python Code

Execute Python code in a secure sandbox.

**API Request:**
```bash
curl -X POST http://localhost:8000/api/v1/code/execute \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def process_data(data):\n    return sum(data) / len(data)\n\nresult = process_data([1, 2, 3, 4, 5])\nprint(result)",
    "language": "python",
    "timeout_seconds": 30
  }'
```

**Response:**
```json
{
  "id": "execution-uuid",
  "code": "...",
  "language": "python",
  "runtime": "e2b",
  "status": "completed",
  "started_at": "2025-01-15T10:00:00Z",
  "completed_at": "2025-01-15T10:00:02Z",
  "output": "3.0\n",
  "error": null
}
```

### Example 2: Register Code Tool

Register a reusable code tool.

**API Request:**
```bash
curl -X POST http://localhost:8000/api/v1/code/register-tool \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_id": "data-processor",
    "name": "Data Processor",
    "version": "1.0.0",
    "code": "def process(data):\n    return sorted(data, reverse=True)",
    "runtime": "e2b",
    "description": "Sorts data in descending order",
    "input_schema": {
      "type": "object",
      "properties": {
        "data": {
          "type": "array",
          "items": {"type": "number"}
        }
      },
      "required": ["data"]
    },
    "output_schema": {
      "type": "object",
      "properties": {
        "result": {
          "type": "array",
          "items": {"type": "number"}
        }
      }
    }
  }'
```

### Example 3: List Code Tools

List available code tools.

**API Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/code/tools?runtime=e2b" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Chat Interface Examples

### Example 1: Send Chat Message (Automation Mode)

Send a message in automation mode to create a workflow.

**WebSocket Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/agws?token=YOUR_TOKEN');

ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'message',
    content: 'Create a workflow that sends an email every Monday at 9 AM',
    mode: 'automation'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};
```

### Example 2: Agent Mode Chat

Chat with an agent in agent mode.

**HTTP Request:**
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Research the latest AI developments and summarize them",
    "mode": "agent"
  }'
```

---

## Complete Workflow Example: E-commerce Price Monitor

A complete workflow that monitors product prices and sends alerts.

**Workflow Configuration:**
```json
{
  "name": "Price Monitor",
  "description": "Monitors product prices and sends alerts on price drops",
  "trigger_config": {
    "type": "cron",
    "cron_expression": "0 */6 * * *"
  },
  "graph_config": {
    "nodes": [
      {
        "id": "trigger-1",
        "type": "trigger",
        "config": {
          "trigger_type": "cron",
          "cron_expression": "0 */6 * * *"
        }
      },
      {
        "id": "scrape-1",
        "type": "scraping",
        "config": {
          "url": "{{trigger.data.product_url}}",
          "engine": "playwright",
          "scrape_requirements": {
            "requires_js": true,
            "stealth_mode": true
          }
        }
      },
      {
        "id": "code-1",
        "type": "code",
        "config": {
          "code": "import re\ndef extract_price(html):\n    match = re.search(r'\\$([\\d,]+\\.[\\d]{2})', html)\n    return float(match.group(1).replace(',', '')) if match else None\n\nprice = extract_price('{{scrape-1.result.html}}')\nresult = {'price': price}",
          "language": "python"
        }
      },
      {
        "id": "condition-1",
        "type": "condition",
        "config": {
          "condition": "{{code-1.result.price}} < {{trigger.data.threshold_price}}",
          "true_path": "notify-1",
          "false_path": "end"
        }
      },
      {
        "id": "notify-1",
        "type": "connector",
        "config": {
          "connector_slug": "email",
          "action": "send",
          "parameters": {
            "to": "{{trigger.data.email}}",
            "subject": "Price Alert: Product Price Dropped!",
            "body": "The price is now ${{code-1.result.price}}, below your threshold of ${{trigger.data.threshold_price}}"
          }
        }
      }
    ],
    "edges": [
      {"source": "trigger-1", "target": "scrape-1"},
      {"source": "scrape-1", "target": "code-1"},
      {"source": "code-1", "target": "condition-1"},
      {"source": "condition-1", "target": "notify-1", "condition": "true"}
    ]
  }
}
```

---

## Tips and Best Practices

1. **Workflow Design:**
   - Keep workflows focused on a single task
   - Use condition nodes for branching logic
   - Test workflows with sample data before production

2. **Connector Usage:**
   - Store OAuth tokens securely (handled automatically via Infisical)
   - Test connector actions before using in workflows
   - Use connector webhooks for real-time triggers

3. **Agent Selection:**
   - Let the router auto-select frameworks unless you have specific requirements
   - Use `agent_self_fix: true` for unreliable external APIs
   - Use multi-agent frameworks for complex tasks requiring multiple perspectives

4. **Performance:**
   - Use caching for frequently accessed data
   - Batch operations when possible (e.g., batch OCR)
   - Monitor execution times and optimize slow nodes

5. **Error Handling:**
   - Workflows automatically retry failed nodes
   - Check execution logs for debugging
   - Use the replay API to retry failed executions

---

For more information, see the [API Documentation](../backend/openapi.json) and [PRD](./PRD.md).

