# Frontend-Backend Synchronization Implementation Plan

This document outlines the step-by-step plan to fix all discrepancies, replace mock/placeholder data, and ensure full frontend-backend synchronization.

**Created:** 2025-01-15

---

## Phase 1: Critical Fixes ✅ (COMPLETED)

### ✅ 1.1 Session Detection Fix
- **Status:** ✅ COMPLETED
- **File:** `frontend/src/hooks/useAuth.ts`
- **Change:** Simplified session detection to use `onAuthStateChange` as authoritative source
- **Impact:** User profile menu should now render correctly

---

## Phase 2: Placeholder Implementation Replacements 🔄

### 2.1 RAG Service - Vector Database Queries
**Priority:** HIGH
**Files:**
- `backend/app/rag/service.py` - `_execute_query` method (line 281-312)

**Current Implementation:**
```python
# Placeholder implementation
return {
    "results": [
        {
            "document_id": f"doc_{i}",
            "content": f"Placeholder result {i} for query: {query_text}",
            "score": 0.9 - (i * 0.1),
        }
        for i in range(min(top_k, 3))
    ],
    "vector_db": client.get("type", "unknown"),
}
```

**Required Implementation:**
- Implement actual vector database queries based on `vector_db_type`
- Support ChromaDB, Milvus, Weaviate, Qdrant, SupaVec, LightRAG, Pinecone
- Query actual documents from RAGIndex
- Return real similarity scores and document content

**Steps:**
1. Check which vector DB is configured
2. Implement query logic for each supported vector DB
3. Query actual documents from the index
4. Return real results with actual scores

---

### 2.2 OCR Service - OCR Engine Calls
**Priority:** HIGH
**Files:**
- `backend/app/ocr/service.py` - `_execute_ocr` method (line 324-347)

**Current Implementation:**
```python
# Placeholder implementation
return {
    "text": f"Placeholder OCR result for {document_url} using {engine}",
    "structured_data": None,
    "confidence_score": 0.95,
}
```

**Required Implementation:**
- Implement actual OCR engine calls (DocTR, EasyOCR, Google Vision API, PaddleOCR, Tesseract, Omniparser)
- Download/access document from URL
- Execute OCR using selected engine
- Return real extracted text and structured data

**Steps:**
1. Implement document download/access logic
2. Implement OCR engine integrations
3. Execute OCR and return real results
4. Handle errors and fallbacks

---

### 2.3 Scraping Service - Scraping Engine Calls
**Priority:** HIGH
**Files:**
- `backend/app/scraping/service.py` - `_execute_scraping` method (line 399-455)

**Current Implementation:**
```python
# Placeholder implementation
return {
    "content": f"Placeholder scraped content for {url} using {engine}",
    "html": f"<html><body>Placeholder HTML for {url}</body></html>",
    "headers": headers,
    "status_code": 200,
    "latency_ms": 0,
}
```

**Required Implementation:**
- Implement actual scraping engine calls (BeautifulSoup, Crawl4AI, Playwright, Scrapy, ScrapeGraph AI, Jobspy, WaterCrawl)
- Execute scraping with proper headers, proxies, stealth config
- Return real scraped content and HTML
- Measure actual latency

**Steps:**
1. Implement scraping engine integrations
2. Apply headers, proxies, stealth config
3. Execute scraping and return real results
4. Handle errors and retries

---

### 2.4 Browser Service - Browser Automation Calls
**Priority:** HIGH
**Files:**
- `backend/app/browser/service.py` - `_execute_action` method (line 413-451)

**Current Implementation:**
```python
# Placeholder implementation
return {
    "message": f"Placeholder browser action: {action_type}",
    "action_type": action_type,
    "timestamp": datetime.utcnow().isoformat(),
}
```

**Required Implementation:**
- Implement actual browser automation (Playwright, Puppeteer, browser-use.com, AI Browser Agent, Browserbase/Stagehand)
- Execute browser actions (navigate, click, fill, screenshot, etc.)
- Return real action results

**Steps:**
1. Implement browser engine integrations
2. Execute browser actions
3. Return real results
4. Handle errors and timeouts

---

### 2.5 OSINT Service - OSINT Engine Calls
**Priority:** HIGH
**Files:**
- `backend/app/osint/service.py` - `_execute_with_engine` method (line 364-392)

**Current Implementation:**
```python
# Placeholder implementation
return {
    "items": [],
    "total_count": 0,
    "platform": platform,
    "query_text": query_text,
    "query_type": query_type,
    "timestamp": datetime.utcnow().isoformat(),
}
```

**Required Implementation:**
- Implement actual OSINT engine calls (Twint, Tweepy, Social-Listener, NewsCatcher, Huginn)
- Execute OSINT queries on platforms
- Return real signals/items

**Steps:**
1. Implement OSINT engine integrations
2. Execute queries on platforms
3. Return real results
4. Handle rate limits and errors

---

### 2.6 Code Execution Service - Runtime Calls
**Priority:** HIGH
**Files:**
- `backend/app/code/service.py` - `execute_code` method (line 367)

**Current Implementation:**
```python
# For now, return placeholder
```

**Required Implementation:**
- Implement actual code execution runtime calls (E2B, WasmEdge, Bacalhau, Cline Node, MCP Server)
- Execute code in sandboxed environment
- Return real execution results

**Steps:**
1. Implement runtime integrations
2. Execute code in sandbox
3. Return real results
4. Handle timeouts and errors

---

### 2.7 Chat Processor - LLM Integration
**Priority:** HIGH
**Files:**
- `backend/app/services/chat_processor.py` - `process` method (line 76-83)

**Current Implementation:**
```python
# For now, return a placeholder response
```

**Required Implementation:**
- Implement actual LLM integration
- Process chat messages with context
- Return real LLM responses
- Handle tool calls and workflow creation

**Steps:**
1. Integrate LLM service (OpenAI, Anthropic, etc.)
2. Process messages with context
3. Return real responses
4. Handle tool calls and workflows

---

### 2.8 Agent Frameworks - Framework Integrations
**Priority:** MEDIUM
**Files:**
- `backend/app/agents/frameworks/*.py` - Multiple frameworks

**Current Implementation:**
- All frameworks return placeholder execution results

**Required Implementation:**
- Implement actual agent framework integrations
- Execute tasks using real frameworks
- Return real execution results

**Steps:**
1. Install and configure agent framework libraries
2. Implement framework-specific execution logic
3. Return real results
4. Handle errors and timeouts

---

### 2.9 Workflow Activities - Activity Execution
**Priority:** MEDIUM
**Files:**
- `backend/app/workflows/activities.py` - HTTP Request and Code Execution activities

**Current Implementation:**
- Returns placeholder results

**Required Implementation:**
- Implement actual HTTP request execution
- Implement actual code execution in workflow context
- Return real results

**Steps:**
1. Implement HTTP request activity
2. Implement code execution activity
3. Return real results
4. Handle errors

---

### 2.10 Guardrails Service - ArchGW Integration
**Priority:** LOW
**Files:**
- `backend/app/guardrails/service.py`

**Current Implementation:**
- Placeholder implementation

**Required Implementation:**
- Implement actual guardrails service
- Integrate with ArchGW if available
- Return real guardrail checks

**Steps:**
1. Implement guardrails service
2. Integrate with ArchGW
3. Return real checks

---

## Phase 3: Frontend Integration for Unused Backend Endpoints

### 3.1 Connector Features
- Add UI for connector versions (`GET /api/v1/connectors/{slug}/versions`)
- Add UI for connector actions (`GET /api/v1/connectors/{slug}/actions`)
- Add UI for connector triggers (`GET /api/v1/connectors/{slug}/triggers`)
- Add refresh token functionality (`POST /api/v1/connectors/{slug}/refresh`)

### 3.2 RAG Features
- Add UI for RAG switch evaluation (`POST /api/v1/rag/switch/evaluate`)
- Add UI for RAG switch logs (`GET /api/v1/rag/switch/logs`)
- Add UI for query history (`GET /api/v1/rag/query/{query_id}`)
- Add fine-tuning UI (`POST /api/v1/rag/finetune`)
- Add Agent0 validation UI (`POST /api/v1/rag/agent0/validate`)

### 3.3 Scraping Features
- Add multi-page crawl UI (`POST /api/v1/scraping/crawl`)

### 3.4 Browser Features
- Add browser action execution UI (`POST /api/v1/browser/execute/{session_id}`)
- Add page monitoring UI (`POST /api/v1/browser/monitor`)

### 3.5 OSINT Features
- Add batch digest UI (`POST /api/v1/osint/digest`)

### 3.6 Agent Features
- Add switch evaluation UI (`POST /api/v1/agents/switch/evaluate`)
- Add task list UI (`GET /api/v1/agents/tasks`)

### 3.7 Code Features
- Add tool version UI (`GET /api/v1/code/tools/{tool_id}/versions`)
- Add tool deprecation UI (`POST /api/v1/code/tools/{tool_id}/deprecate`)

---

## Phase 4: Testing & Verification

### 4.1 End-to-End Testing
- Test all frontend-backend integrations
- Verify real database data is used
- Test error handling
- Test authentication flows

### 4.2 Performance Testing
- Test database query performance
- Test API response times
- Optimize slow queries

### 4.3 Security Testing
- Verify authentication on all endpoints
- Test authorization checks
- Test input validation

---

## Implementation Order

1. ✅ **Phase 1: Critical Fixes** - Session detection
2. **Phase 2: High Priority Placeholders** - RAG, OCR, Scraping, Browser, OSINT, Code, Chat
3. **Phase 2: Medium Priority** - Agent frameworks, Workflow activities
4. **Phase 2: Low Priority** - Guardrails
5. **Phase 3: Frontend Integration** - Add UI for unused endpoints
6. **Phase 4: Testing** - End-to-end verification

---

## Notes

- All placeholder implementations should be replaced with real service calls
- Database queries should use actual models and relationships
- Error handling should be comprehensive
- Logging should be added for debugging
- Performance should be optimized where possible

