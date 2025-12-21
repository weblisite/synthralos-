# Unused Endpoints Explanation

**Date:** December 20, 2025
**Status:** Documentation

---

## 🎯 What Are "Unused Endpoints"?

**Unused endpoints** are backend API routes that are **fully implemented and functional** but are **not currently called by any frontend component**. They exist in the backend codebase, work correctly, and return real database data, but the frontend UI doesn't use them yet.

---

## 📊 Current Situation

### ✅ What We Have Now

**Backend:** 100+ endpoints implemented
- All endpoints are functional
- All endpoints use real database data
- All endpoints have proper error handling
- All endpoints are tested and working

**Frontend:** 50+ API calls implemented
- All calls use `apiClient.request()`
- All calls fetch real database data
- All calls are integrated with UI components

### ⚠️ The Gap

**30+ endpoints exist but aren't used by frontend:**
- These endpoints are **ready to use**
- They just need **frontend components** to call them
- They're **optional** - not needed for core functionality

---

## 🔍 Examples of Unused Endpoints

### Example 1: Storage Management Endpoints

**Backend Has:**
```python
# backend/app/api/routes/storage.py

@router.get("/download/{bucket}/{file_path:path}")
async def download_file(...)  # ✅ Implemented

@router.delete("/delete/{bucket}/{file_path:path}")
async def delete_file(...)  # ✅ Implemented

@router.get("/list/{bucket}")
async def list_files(...)  # ✅ Implemented

@router.post("/signed-url")
async def create_signed_url(...)  # ✅ Implemented

@router.get("/buckets")
async def list_buckets(...)  # ✅ Implemented
```

**Frontend Currently Uses:**
- ✅ `POST /api/v1/storage/upload` - Used by `FileUpload.tsx`

**Frontend Doesn't Use (Yet):**
- ⚠️ `GET /api/v1/storage/download/{bucket}/{file_path}` - No download button in UI
- ⚠️ `DELETE /api/v1/storage/delete/{bucket}/{file_path}` - No delete button in UI
- ⚠️ `GET /api/v1/storage/list/{bucket}` - No file browser in UI
- ⚠️ `POST /api/v1/storage/signed-url` - No share link feature in UI
- ⚠️ `GET /api/v1/storage/buckets` - No bucket selector in UI

**Why They're Unused:**
- The current `FileUpload.tsx` component only handles uploading
- There's no file management UI (browser, delete, download)
- These features haven't been requested yet

**When You'd Integrate Them:**
- When you want to add a file browser/manager UI
- When users need to download uploaded files
- When users need to delete files
- When you want to show all files in a bucket

**How to Integrate:**
```typescript
// Example: Add file download feature
const handleDownload = async (bucket: string, filePath: string) => {
  try {
    // Get signed URL from backend
    const { url } = await apiClient.request<{ url: string }>(
      "/api/v1/storage/signed-url",
      {
        method: "POST",
        body: JSON.stringify({ bucket, file_path: filePath }),
      }
    )
    // Open download link
    window.open(url, '_blank')
  } catch (error) {
    showErrorToast("Failed to generate download URL")
  }
}
```

---

### Example 2: Code Tool Management Endpoints

**Backend Has:**
```python
# backend/app/api/routes/code.py

@router.post("/register-tool")
def register_tool(...)  # ✅ Implemented

@router.get("/tools/{tool_id}")
def get_tool(...)  # ✅ Implemented

@router.get("/tools/{tool_id}/versions")
def get_tool_versions(...)  # ✅ Implemented

@router.post("/tools/{tool_id}/deprecate")
def deprecate_tool(...)  # ✅ Implemented
```

**Frontend Currently Uses:**
- ✅ `POST /api/v1/code/execute` - Used by `CodeToolRegistry.tsx`
- ✅ `GET /api/v1/code/tools` - Used by `CodeToolRegistry.tsx`
- ✅ `GET /api/v1/code/sandboxes` - Used by `CodeToolRegistry.tsx`

**Frontend Doesn't Use (Yet):**
- ⚠️ `POST /api/v1/code/register-tool` - No tool registration form in UI
- ⚠️ `GET /api/v1/code/tools/{tool_id}` - No tool details page
- ⚠️ `GET /api/v1/code/tools/{tool_id}/versions` - No version history view
- ⚠️ `POST /api/v1/code/tools/{tool_id}/deprecate` - No deprecation button

**Why They're Unused:**
- Current UI focuses on executing code, not managing tools
- Tool registration/management is an admin feature
- These features haven't been prioritized

**When You'd Integrate Them:**
- When you want to add a tool marketplace
- When admins need to register custom tools
- When users need to see tool details/versions
- When you need to deprecate outdated tools

**How to Integrate:**
```typescript
// Example: Add tool registration form
const handleRegisterTool = async (toolData: ToolData) => {
  try {
    const tool = await apiClient.request(
      "/api/v1/code/register-tool",
      {
        method: "POST",
        body: JSON.stringify(toolData),
      }
    )
    showSuccessToast("Tool registered successfully")
    // Refresh tools list
    queryClient.invalidateQueries({ queryKey: ["codeTools"] })
  } catch (error) {
    showErrorToast("Failed to register tool")
  }
}
```

---

### Example 3: Agent Task Management Endpoints

**Backend Has:**
```python
# backend/app/api/routes/agents.py

@router.get("/status/{task_id}")
def get_task_status(...)  # ✅ Implemented

@router.get("/tasks")
def list_agent_tasks(...)  # ✅ Implemented
```

**Frontend Currently Uses:**
- ✅ `POST /api/v1/agents/run` - Used by `AgentCatalog.tsx`
- ✅ `GET /api/v1/agents/catalog` - Used by `AgentCatalog.tsx`

**Frontend Doesn't Use (Yet):**
- ⚠️ `GET /api/v1/agents/status/{task_id}` - No task status polling
- ⚠️ `GET /api/v1/agents/tasks` - No task history/list view

**Why They're Unused:**
- Current UI runs tasks but doesn't track them
- No task history or status page exists
- These features haven't been built yet

**When You'd Integrate Them:**
- When you want to add a task history page
- When you need to poll task status
- When users need to see all their agent tasks
- When you want to show task progress

**How to Integrate:**
```typescript
// Example: Add task status polling
const pollTaskStatus = async (taskId: string) => {
  const status = await apiClient.request(
    `/api/v1/agents/status/${taskId}`
  )
  return status
}

// Example: Add task list view
const fetchAgentTasks = async () => {
  const tasks = await apiClient.request("/api/v1/agents/tasks")
  return tasks
}
```

---

## 🤔 Why Are These Endpoints Unused?

### Reason 1: Feature Not Yet Built
**Example:** File download feature
- Backend can generate download URLs ✅
- Frontend doesn't have a download button yet ⚠️
- **Solution:** Add download button when feature is needed

### Reason 2: Feature Not Prioritized
**Example:** Tool registration
- Backend can register tools ✅
- Frontend focuses on execution, not management ⚠️
- **Solution:** Add admin UI when tool marketplace is prioritized

### Reason 3: Feature Planned for Future
**Example:** Execution timeline visualization
- Backend can return timeline data ✅
- Frontend shows logs but not timeline graph ⚠️
- **Solution:** Add timeline visualization component when designed

### Reason 4: Advanced Feature
**Example:** RAG routing evaluation
- Backend can evaluate routing decisions ✅
- Frontend focuses on basic querying ⚠️
- **Solution:** Add advanced features UI when users need them

---

## 🚀 How to Integrate Unused Endpoints

### Step 1: Identify the Need
**Question:** Do users need this feature?
- **Yes** → Proceed to Step 2
- **No** → Leave endpoint unused (it's ready when needed)

### Step 2: Design the UI
**Example:** Adding file download feature
```typescript
// Design: Add download button to file list
<Button onClick={() => handleDownload(file.bucket, file.path)}>
  Download
</Button>
```

### Step 3: Create Frontend Component
**Example:** File download handler
```typescript
const handleDownload = async (bucket: string, filePath: string) => {
  try {
    // Call unused endpoint
    const { url } = await apiClient.request<{ url: string }>(
      "/api/v1/storage/signed-url",
      {
        method: "POST",
        body: JSON.stringify({ bucket, file_path: filePath }),
      }
    )
    window.open(url, '_blank')
  } catch (error) {
    showErrorToast("Failed to download file")
  }
}
```

### Step 4: Test Integration
- Test the endpoint works
- Test error handling
- Test UI updates correctly

### Step 5: Deploy
- Feature is now integrated
- Endpoint is now "used"

---

## 📋 Complete List of Unused Endpoints

### Storage (5 endpoints)
- `GET /api/v1/storage/download/{bucket}/{file_path}` - Download file
- `DELETE /api/v1/storage/delete/{bucket}/{file_path}` - Delete file
- `GET /api/v1/storage/list/{bucket}` - List files
- `POST /api/v1/storage/signed-url` - Generate signed URL
- `GET /api/v1/storage/buckets` - List buckets

**Use Case:** File management UI, file browser

### Code Tools (4 endpoints)
- `POST /api/v1/code/register-tool` - Register tool
- `GET /api/v1/code/tools/{tool_id}` - Get tool details
- `GET /api/v1/code/tools/{tool_id}/versions` - Get tool versions
- `POST /api/v1/code/tools/{tool_id}/deprecate` - Deprecate tool

**Use Case:** Tool marketplace, tool management

### Agents (2 endpoints)
- `GET /api/v1/agents/status/{task_id}` - Get task status
- `GET /api/v1/agents/tasks` - List agent tasks

**Use Case:** Task history, task status tracking

### RAG (5 endpoints)
- `POST /api/v1/rag/switch/evaluate` - Evaluate routing
- `GET /api/v1/rag/switch/logs` - Get routing logs
- `GET /api/v1/rag/query/{query_id}` - Get query details
- `POST /api/v1/rag/agent0/validate` - Validate Agent0 prompt
- `POST /api/v1/rag/finetune` - Start finetune job

**Use Case:** Advanced RAG features, routing optimization

### OCR (2 endpoints)
- `POST /api/v1/ocr/batch` - Batch extract
- `POST /api/v1/ocr/process/{job_id}` - Process job manually

**Use Case:** Batch processing, manual job processing

### Scraping (2 endpoints)
- `POST /api/v1/scraping/crawl` - Create crawl jobs
- `POST /api/v1/scraping/change-detection` - Monitor page changes

**Use Case:** Multi-page crawling, change monitoring

### Browser (1 endpoint)
- `POST /api/v1/browser/monitor` - Monitor page changes

**Use Case:** Page change detection

### OSINT (2 endpoints)
- `POST /api/v1/osint/digest` - Create digest
- `POST /api/v1/osint/streams/{stream_id}/execute` - Execute stream

**Use Case:** Batch OSINT queries, manual stream execution

### Workflows (1 endpoint)
- `GET /api/v1/workflows/executions/{execution_id}/timeline` - Get execution timeline

**Use Case:** Timeline visualization

### Connectors (4 endpoints)
- `GET /api/v1/connectors/{slug}/actions` - Get connector actions
- `GET /api/v1/connectors/{slug}/triggers` - Get connector triggers
- `GET /api/v1/connectors/{slug}/versions` - Get connector versions
- `POST /api/v1/connectors/{slug}/rotate` - Rotate credentials

**Use Case:** Connector details page, credential management

### Admin (1 endpoint)
- `GET /api/v1/admin/connectors/stats` - Get connector statistics

**Use Case:** Connector analytics dashboard

**Total:** 30+ unused endpoints ready for integration

---

## 💡 When Should You Integrate Unused Endpoints?

### ✅ Integrate When:

1. **Users Request the Feature**
   - "I need to download files"
   - "I want to see my task history"
   - "Can I manage my tools?"

2. **Feature Adds Value**
   - Improves user experience
   - Enables new workflows
   - Solves a real problem

3. **Feature is Prioritized**
   - Part of roadmap
   - High user demand
   - Competitive advantage

### ❌ Don't Integrate When:

1. **No User Need**
   - Feature isn't requested
   - No clear use case
   - Low priority

2. **Feature Not Designed**
   - UI/UX not planned
   - Requirements unclear
   - Premature optimization

3. **Better Alternatives Exist**
   - External tool better
   - Different approach preferred
   - Feature deprecated

---

## 🎯 Summary

**"Optional endpoints: integrate unused endpoints when features are needed"** means:

1. **30+ endpoints exist** that are fully functional but not used by frontend
2. **They're ready to use** - just need frontend components to call them
3. **They're optional** - not needed for core platform functionality
4. **Integrate them** when you build features that need them

**Think of it like:**
- Backend has all the tools ✅
- Frontend uses most tools ✅
- Some tools are in the toolbox, ready when needed ⚠️
- Use them when building features that need them 🚀

**Example:**
- Backend has file download endpoint ✅
- Frontend doesn't have download button yet ⚠️
- When you add download button → call the endpoint → feature complete ✅

---

**Key Takeaway:** These endpoints are **not broken or missing** - they're **ready and waiting** for frontend features that need them. Integrate them when building those features!

---

**Documentation Created:** December 20, 2025
