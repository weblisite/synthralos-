# Frontend-Backend Sync Fix

## Problem

The frontend was making API calls to relative URLs (e.g., `/api/v1/stats/dashboard`) which resolved to the frontend domain (`https://synthralos-frontend.onrender.com`) instead of the backend domain (`https://synthralos-backend.onrender.com`).

### Symptoms
- Dashboard shows "Failed to load dashboard statistics"
- Agents page shows "Failed to load agent catalog"
- 404 errors in browser console for API endpoints
- Network requests show calls to `synthralos-frontend.onrender.com/api/v1/...` instead of `synthralos-backend.onrender.com/api/v1/...`

### Root Cause
1. Components were using relative URLs in `fetch()` calls
2. `VITE_API_URL` environment variable may not be set correctly in Render deployment
3. No centralized API utility to ensure consistent URL construction

## Solution

### 1. Created API Utility (`frontend/src/lib/api.ts`)
- `getApiUrl()`: Gets the base API URL from `VITE_API_URL` env var
- `getApiPath(path)`: Constructs full API URLs from relative paths
- `apiRequest<T>(path, options)`: Makes authenticated API requests with automatic token injection

### 2. Updated Components
- **DashboardStats**: Now uses `apiRequest()` instead of raw `fetch()` with relative URL
- **AgentCatalog**: Now uses `apiRequest()` for both catalog fetch and task execution

### 3. Render Deployment Configuration

**IMPORTANT**: Ensure `VITE_API_URL` is set correctly in Render dashboard:

1. Go to Render Dashboard > synthralos-frontend service
2. Navigate to Environment tab
3. Set `VITE_API_URL` to: `https://synthralos-backend.onrender.com`
   - **DO NOT** include `/api/v1` - the SDK adds it automatically
   - **DO NOT** include trailing slash

### 4. Verification Steps

After deploying the fix:

1. **Check Environment Variable**:
   ```bash
   # In Render dashboard, verify VITE_API_URL is set to:
   https://synthralos-backend.onrender.com
   ```

2. **Test Dashboard**:
   - Login to frontend
   - Navigate to Dashboard
   - Should see statistics instead of "Failed to load dashboard statistics"

3. **Test Agents Page**:
   - Navigate to `/agents`
   - Should see agent catalog instead of "Failed to load agent catalog"

4. **Check Browser Console**:
   - Open DevTools > Network tab
   - Verify API calls go to `synthralos-backend.onrender.com`
   - Should see 200 responses instead of 404

5. **Check Browser Console Logs**:
   - Should see successful API responses
   - No more 404 errors for `/api/v1/stats/dashboard` or `/api/v1/agents/catalog`

## Remaining Components to Fix

The following components still use relative URLs and should be updated to use `apiRequest()`:

- `frontend/src/components/Admin/AdminConnectorManagement.tsx`
- `frontend/src/components/Admin/ActivityLogs.tsx`
- `frontend/src/components/Admin/SystemHealth.tsx`
- `frontend/src/components/Admin/RetryManagement.tsx`
- `frontend/src/components/Admin/CostAnalytics.tsx`
- `frontend/src/components/Admin/SystemMetrics.tsx`
- `frontend/src/components/OSINT/OSINTStreamManager.tsx`
- `frontend/src/components/Browser/BrowserSessionManager.tsx`
- `frontend/src/components/Code/CodeToolRegistry.tsx`
- `frontend/src/components/Scraping/ScrapingJobManager.tsx`
- `frontend/src/components/OCR/OCRJobManager.tsx`
- `frontend/src/components/Connectors/ConnectorCatalog.tsx`
- `frontend/src/components/RAG/RAGIndexManager.tsx`
- `frontend/src/components/Storage/FileUpload.tsx`
- `frontend/src/components/Workflow/NodePalette.tsx`
- `frontend/src/routes/_layout/workflows.tsx`

## Migration Pattern

To fix remaining components:

1. **Import the utility**:
   ```typescript
   import { apiRequest } from "@/lib/api"
   ```

2. **Replace fetch calls**:
   ```typescript
   // Before:
   const response = await fetch("/api/v1/endpoint", {
     headers: {
       Authorization: `Bearer ${session.access_token}`,
       "Content-Type": "application/json",
     },
   })
   const data = await response.json()

   // After:
   const data = await apiRequest("/api/v1/endpoint")
   ```

3. **For POST/PUT/DELETE**:
   ```typescript
   // Before:
   const response = await fetch("/api/v1/endpoint", {
     method: "POST",
     headers: {
       Authorization: `Bearer ${session.access_token}`,
       "Content-Type": "application/json",
     },
     body: JSON.stringify(data),
   })

   // After:
   const result = await apiRequest("/api/v1/endpoint", {
     method: "POST",
     body: JSON.stringify(data),
   })
   ```

## Testing

After deploying fixes:

1. Test all major pages:
   - Dashboard
   - Agents
   - Connectors
   - Workflows
   - RAG
   - OCR
   - Scraping
   - Browser
   - OSINT
   - Code
   - Chat

2. Verify network requests:
   - All API calls should go to backend domain
   - No 404 errors
   - Proper authentication headers

3. Check console:
   - No CORS errors
   - No 404 errors
   - Successful API responses
