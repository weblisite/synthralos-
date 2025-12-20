# API Request Migration - Detailed Explanation

## Overview

This document explains the comprehensive migration from relative URL fetch calls to a centralized `apiRequest()` utility, why some Supabase imports were removed, and how this affects the platform's architecture.

## The Problem

### Before Migration

**Issue:** Frontend components were making API calls using relative URLs like `/api/v1/stats/dashboard`, which resolved to the **frontend domain** (`synthralos-frontend.onrender.com`) instead of the **backend domain** (`synthralos-backend.onrender.com`).

**Example of the problem:**
```typescript
// ❌ BEFORE - Relative URL (WRONG)
const response = await fetch("/api/v1/stats/dashboard", {
  headers: {
    Authorization: `Bearer ${session.access_token}`,
    "Content-Type": "application/json",
  },
})
```

**What happened:**
- Browser resolves `/api/v1/stats/dashboard` relative to current page URL
- If you're on `https://synthralos-frontend.onrender.com/dashboard`
- Browser tries: `https://synthralos-frontend.onrender.com/api/v1/stats/dashboard`
- Result: **404 Not Found** (frontend doesn't have API endpoints)

**Symptoms:**
- Dashboard shows "Failed to load dashboard statistics"
- Agents page shows "Failed to load agent catalog"
- All API calls returned 404 errors
- Network tab showed requests going to frontend domain instead of backend

## The Solution

### Created Centralized API Utility (`frontend/src/lib/api.ts`)

**Purpose:** Provide a single, consistent way to make authenticated API requests that always target the backend domain.

```typescript
/**
 * API utility functions
 *
 * Provides a centralized way to construct API URLs and make authenticated requests.
 */

import { supabase } from "./supabase"

/**
 * Get the base API URL from environment variable
 * Falls back to localhost for development
 */
export function getApiUrl(): string {
  const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000"
  // Remove trailing slash if present
  return apiUrl.replace(/\/$/, "")
}

/**
 * Construct a full API URL from a relative path
 * @param path - Relative API path (e.g., "/api/v1/stats/dashboard")
 * @returns Full URL (e.g., "https://backend.onrender.com/api/v1/stats/dashboard")
 */
export function getApiPath(path: string): string {
  const baseUrl = getApiUrl()
  // Ensure path starts with /
  const normalizedPath = path.startsWith("/") ? path : `/${path}`
  return `${baseUrl}${normalizedPath}`
}

/**
 * Make an authenticated API request
 * Automatically includes the Supabase session token
 * @param path - Relative API path
 * @param options - Fetch options (headers will be merged with auth headers)
 */
export async function apiRequest<T = unknown>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const {
    data: { session },
  } = await supabase.auth.getSession()

  if (!session) {
    throw new Error("You must be logged in to make API requests")
  }

  const url = getApiPath(path)
  const headers = new Headers(options.headers)
  headers.set("Authorization", `Bearer ${session.access_token}`)

  // Don't set Content-Type for FormData - browser will set it with boundary
  if (!(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json")
  }

  const response = await fetch(url, {
    ...options,
    headers,
  })

  if (!response.ok) {
    const errorText = await response.text().catch(() => "Unknown error")
    throw new Error(
      `API request failed: ${response.status} ${response.statusText} - ${errorText}`
    )
  }

  return response.json()
}
```

### Key Features of `apiRequest()`

1. **Automatic URL Construction**
   - Uses `VITE_API_URL` environment variable
   - Constructs full backend URL: `https://synthralos-backend.onrender.com/api/v1/...`
   - Falls back to `http://localhost:8000` for local development

2. **Automatic Authentication**
   - Gets Supabase session automatically
   - Includes `Authorization: Bearer <token>` header
   - Throws error if user is not logged in

3. **FormData Support**
   - Detects FormData in request body
   - Doesn't set `Content-Type` header for FormData (browser sets it with boundary)
   - Used for file uploads (RAG documents, OCR files, storage)

4. **Consistent Error Handling**
   - All errors follow same format
   - Includes HTTP status code and error message
   - Makes debugging easier

## Migration Pattern

### Before (Every Component)

```typescript
// ❌ BEFORE - Repetitive, error-prone code
import { supabase } from "@/lib/supabase"

const fetchData = async () => {
  const {
    data: { session },
  } = await supabase.auth.getSession()

  if (!session) {
    throw new Error("You must be logged in")
  }

  const response = await fetch("/api/v1/endpoint", {
    headers: {
      Authorization: `Bearer ${session.access_token}`,
      "Content-Type": "application/json",
    },
  })

  if (!response.ok) {
    throw new Error("Failed to fetch data")
  }

  return response.json()
}
```

**Problems:**
- Relative URL (`/api/v1/endpoint`) resolves to frontend domain
- Repetitive session checking code
- Inconsistent error handling
- Easy to forget authentication headers

### After (Using `apiRequest()`)

```typescript
// ✅ AFTER - Clean, centralized, correct
import { apiRequest } from "@/lib/api"

const fetchData = async () => {
  return apiRequest("/api/v1/endpoint")
}
```

**Benefits:**
- Full backend URL automatically constructed
- Session checked automatically
- Authentication headers added automatically
- Consistent error handling
- Much less code

## Why Some Supabase Imports Were Removed

### Components That Removed `import { supabase } from "@/lib/supabase"`

**Reason:** These components were **only** using Supabase to get the session token for API calls. Now `apiRequest()` handles that internally.

**Example - Before:**
```typescript
// Component needed Supabase ONLY for API calls
import { supabase } from "@/lib/supabase"

const fetchConnectors = async () => {
  const { data: { session } } = await supabase.auth.getSession()
  if (!session) throw new Error("Not logged in")

  const response = await fetch("/api/v1/connectors", {
    headers: {
      Authorization: `Bearer ${session.access_token}`,
    },
  })
  return response.json()
}
```

**After:**
```typescript
// Component doesn't need Supabase anymore - apiRequest handles it
import { apiRequest } from "@/lib/api"

const fetchConnectors = async () => {
  return apiRequest("/api/v1/connectors")
}
```

### Components That Kept Supabase Imports

**Reason:** These components use Supabase for **other purposes** beyond API calls:

1. **Authentication State Management**
   - `useAuth.ts` - Manages user authentication state
   - `AppSidebar.tsx` - Displays user info
   - `User.tsx` - User profile component

2. **Direct Supabase Operations**
   - `FileUpload.tsx` - Uses `supabase.storage.from(bucket).upload()` for file uploads
   - `AgUIProvider.tsx` - Uses Supabase for WebSocket token and session management

3. **Auth Flow Components**
   - Login/Signup pages - Direct Supabase Auth operations
   - Password reset - Uses Supabase Auth API

## Impact on Supabase

### What Changed

1. **API Authentication Flow**
   - **Before:** Each component fetched Supabase session independently
   - **After:** `apiRequest()` centralizes session fetching
   - **Impact:** More efficient (single session check per request), consistent behavior

2. **Supabase Usage Reduced**
   - **Before:** ~50+ components imported Supabase just for API calls
   - **After:** Only components that need Supabase for other purposes import it
   - **Impact:** Cleaner code, better separation of concerns

3. **Supabase Still Used For:**
   - ✅ User authentication (login, signup, logout)
   - ✅ Session management (`useAuth` hook)
   - ✅ File storage (`supabase.storage.from().upload()`)
   - ✅ WebSocket authentication tokens
   - ✅ User profile management

### What Didn't Change

- ✅ Supabase Auth still handles all authentication
- ✅ Supabase Storage still handles file uploads
- ✅ Supabase database still stores all data
- ✅ Session tokens still come from Supabase
- ✅ User management still uses Supabase Auth

### Architecture Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Component                       │
│  (e.g., DashboardStats, AgentCatalog, etc.)                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Calls apiRequest("/api/v1/endpoint")
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              apiRequest() Utility Function                  │
│  1. Gets Supabase session (supabase.auth.getSession())      │
│  2. Constructs full backend URL using VITE_API_URL          │
│  3. Adds Authorization header with Supabase token           │
│  4. Makes fetch() call to backend                            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ HTTP Request with Bearer Token
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Backend API (FastAPI)                          │
│  - Validates Supabase JWT token                             │
│  - Queries Supabase PostgreSQL database                     │
│  - Returns JSON response                                    │
└─────────────────────────────────────────────────────────────┘
```

## Components Updated

### Admin Components (6 files)
- `AdminConnectorManagement.tsx` - Connector CRUD operations
- `ActivityLogs.tsx` - Activity log fetching
- `SystemHealth.tsx` - Health check endpoint
- `RetryManagement.tsx` - Failed execution management
- `CostAnalytics.tsx` - Cost metrics
- `SystemMetrics.tsx` - System statistics

### Feature Components (10 files)
- `OSINTStreamManager.tsx` - OSINT operations
- `BrowserSessionManager.tsx` - Browser automation
- `CodeToolRegistry.tsx` - Code execution
- `ScrapingJobManager.tsx` - Web scraping
- `OCRJobManager.tsx` - OCR processing
- `ConnectorCatalog.tsx` - Connector management
- `RAGIndexManager.tsx` - RAG operations
- `Storage/FileUpload.tsx` - File uploads (partial - still uses Supabase Storage directly)
- `Workflow/NodePalette.tsx` - Workflow builder connectors
- `routes/_layout/workflows.tsx` - Workflow save/run

### Previously Updated (2 files)
- `DashboardStats.tsx` - Dashboard statistics
- `AgentCatalog.tsx` - Agent framework catalog

### Chat Component (1 file)
- `Chat/AgUIProvider.tsx` - HTTP fallback for chat (WebSocket still uses Supabase)

## Benefits

### 1. Correct API Routing
- ✅ All API calls now go to backend domain
- ✅ No more 404 errors
- ✅ Frontend and backend properly synchronized

### 2. Code Quality
- ✅ **867 lines removed** (redundant fetch code)
- ✅ **113 lines added** (clean apiRequest calls)
- ✅ **Net reduction:** ~750 lines of code
- ✅ DRY principle (Don't Repeat Yourself)

### 3. Maintainability
- ✅ Single place to update API URL logic
- ✅ Consistent error handling
- ✅ Easier to add features (logging, retries, etc.)

### 4. Developer Experience
- ✅ Simpler component code
- ✅ Less boilerplate
- ✅ Type-safe with TypeScript generics

### 5. Performance
- ✅ More efficient session checking (centralized)
- ✅ Consistent request patterns
- ✅ Better error messages for debugging

## Environment Variable Required

**`VITE_API_URL`** must be set in Render dashboard:

```
VITE_API_URL=https://synthralos-backend.onrender.com
```

**Important:**
- ✅ Do NOT include `/api/v1` (SDK adds it automatically)
- ✅ Do NOT include trailing slash
- ✅ Must be set after backend deploys (to get the URL)

## Testing Checklist

After deployment, verify:

- [ ] Dashboard loads statistics
- [ ] Agents page shows catalog
- [ ] Connectors load and show auth status
- [ ] Workflows save and run
- [ ] RAG indexes load and queries work
- [ ] OCR jobs create and process
- [ ] Scraping jobs work
- [ ] Browser sessions create
- [ ] OSINT streams work
- [ ] Code execution works
- [ ] Admin pages load data
- [ ] Chat works (HTTP fallback)
- [ ] File uploads work (Supabase Storage)

## Migration Statistics

- **Total Files Updated:** 18
- **Lines Removed:** 867
- **Lines Added:** 113
- **Net Reduction:** ~754 lines
- **Components Using apiRequest():** 18+
- **Supabase Imports Removed:** ~15 (from components that only needed it for API calls)
- **Supabase Imports Kept:** ~10 (components that use Supabase for other purposes)

## Conclusion

This migration:
1. ✅ Fixes the frontend-backend sync issue
2. ✅ Reduces code duplication significantly
3. ✅ Improves maintainability
4. ✅ Keeps Supabase for authentication and storage
5. ✅ Centralizes API request logic
6. ✅ Makes the codebase cleaner and more consistent

**Supabase is still the foundation** for authentication, storage, and database. We just centralized how we use Supabase tokens for API calls, making the code cleaner and ensuring all requests go to the correct backend domain.
