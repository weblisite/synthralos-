# OpenAPI SDK vs apiRequest() - How They Work Together

## Overview

The frontend uses **TWO complementary systems** for making API calls to the backend:

1. **OpenAPI SDK** - Generated TypeScript client for type-safe API calls
2. **apiRequest()** - Custom utility for endpoints not covered by OpenAPI SDK

Both systems work together seamlessly, using the same configuration and authentication.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Components                      │
└──────────────┬──────────────────────────────┬───────────────┘
               │                              │
               ▼                              ▼
    ┌──────────────────────┐      ┌──────────────────────┐
    │   OpenAPI SDK        │      │   apiRequest()        │
    │   (Generated)        │      │   (Custom Utility)    │
    └──────────┬───────────┘      └──────────┬─────────────┘
               │                              │
               │ Uses OpenAPI.BASE            │ Uses getApiUrl()
               │ Uses OpenAPI.TOKEN           │ Uses Supabase session
               │                              │
               ▼                              ▼
    ┌──────────────────────────────────────────────────────┐
    │         Both Use Same Configuration                 │
    │  - VITE_API_URL (from environment)                  │
    │  - Supabase Auth Token (from session)                │
    │  - Target: https://synthralos-backend.onrender.com  │
    └──────────────────────┬──────────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │   Backend API          │
              │   (FastAPI)            │
              └────────────────────────┘
```

## OpenAPI SDK

### What It Is

The **OpenAPI SDK** is a **generated TypeScript client** created from your backend's OpenAPI schema. It provides:

- ✅ **Type-safe** API calls with TypeScript types
- ✅ **Auto-completion** in IDE
- ✅ **Generated services** like `UsersService`, `LoginService`
- ✅ **Request/response validation** based on OpenAPI schema

### Configuration (in `main.tsx`)

```typescript
import { OpenAPI } from "./client"

// Set base URL from environment variable
OpenAPI.BASE = import.meta.env.VITE_API_URL

// Configure token provider (uses Supabase)
OpenAPI.TOKEN = async () => {
  const { data: { session } } = await supabase.auth.getSession()
  return session?.access_token || ""
}
```

### How It Works

1. **Uses Axios** under the hood (HTTP client library)
2. **Constructs URLs** using `OpenAPI.BASE + endpoint path`
3. **Adds Authorization header** using `OpenAPI.TOKEN()` callback
4. **Returns typed responses** based on OpenAPI schema

### Example Usage

```typescript
import { UsersService } from "@/client"

// Type-safe API call
const user = await UsersService.readUserMe()
// TypeScript knows: user is UserPublic type
// IDE provides autocomplete for user properties
```

### Endpoints Covered by OpenAPI SDK

Based on the generated services, OpenAPI SDK covers:

- ✅ **Users** - `UsersService.readUsers()`, `UsersService.createUser()`, etc.
- ✅ **Login** - `LoginService.loginAccessToken()`, `LoginService.recoverPassword()`, etc.
- ✅ **Utils** - `UtilsService.healthCheck()`, `UtilsService.testEmail()`, etc.
- ❌ **Items** - `ItemsService` (but Items feature was removed)

### Components Using OpenAPI SDK

- `useAuth.ts` - `UsersService.readUserMe()`
- `AddUser.tsx` - `UsersService.createUser()`
- `EditUser.tsx` - `UsersService.updateUser()`
- `DeleteUser.tsx` - `UsersService.deleteUser()`
- `UserInformation.tsx` - `UsersService.updateUserMe()`
- `ChangePassword.tsx` - `UsersService.updatePasswordMe()`
- `DeleteConfirmation.tsx` - `UsersService.deleteUserMe()`
- `admin.tsx` route - `UsersService.readUsers()`
- `recover-password.tsx` - `LoginService.recoverPassword()`
- `reset-password.tsx` - `LoginService.resetPassword()`

## apiRequest() Utility

### What It Is

**apiRequest()** is a **custom utility function** I created to handle API endpoints that are **NOT covered by the OpenAPI SDK**. It provides:

- ✅ **Consistent URL construction** using `VITE_API_URL`
- ✅ **Automatic authentication** using Supabase session
- ✅ **FormData support** for file uploads
- ✅ **Consistent error handling**

### Configuration (in `frontend/src/lib/api.ts`)

```typescript
import { supabase } from "./supabase"

export function getApiUrl(): string {
  const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000"
  return apiUrl.replace(/\/$/, "")
}

export async function apiRequest<T>(path: string, options: RequestInit = {}): Promise<T> {
  // Gets Supabase session
  const { data: { session } } = await supabase.auth.getSession()
  
  // Constructs full backend URL
  const url = getApiPath(path) // Uses VITE_API_URL
  
  // Adds Authorization header
  headers.set("Authorization", `Bearer ${session.access_token}`)
  
  // Makes fetch() call
  return fetch(url, { ...options, headers }).then(r => r.json())
}
```

### How It Works

1. **Uses native `fetch()`** API (no external dependencies)
2. **Constructs URLs** using `getApiUrl()` + path
3. **Gets Supabase session** internally
4. **Adds Authorization header** automatically
5. **Returns JSON** response

### Example Usage

```typescript
import { apiRequest } from "@/lib/api"

// Simple API call
const stats = await apiRequest<DashboardStats>("/api/v1/stats/dashboard")

// POST request
const result = await apiRequest("/api/v1/workflows", {
  method: "POST",
  body: JSON.stringify({ name: "My Workflow" })
})
```

### Endpoints Covered by apiRequest()

These endpoints are **NOT in the OpenAPI schema**, so they use `apiRequest()`:

- ✅ **Dashboard Stats** - `/api/v1/stats/dashboard`
- ✅ **Agents** - `/api/v1/agents/catalog`, `/api/v1/agents/run`
- ✅ **Connectors** - `/api/v1/connectors/list`, `/api/v1/connectors/{slug}/auth-status`
- ✅ **Workflows** - `/api/v1/workflows`, `/api/v1/workflows/{id}/run`
- ✅ **RAG** - `/api/v1/rag/indexes`, `/api/v1/rag/query`
- ✅ **OCR** - `/api/v1/ocr/jobs`, `/api/v1/ocr/extract`
- ✅ **Scraping** - `/api/v1/scraping/jobs`, `/api/v1/scraping/scrape`
- ✅ **Browser** - `/api/v1/browser/sessions`, `/api/v1/browser/session`
- ✅ **OSINT** - `/api/v1/osint/streams`, `/api/v1/osint/alerts`
- ✅ **Code** - `/api/v1/code/tools`, `/api/v1/code/execute`
- ✅ **Storage** - `/api/v1/storage/upload`
- ✅ **Admin** - `/api/v1/admin/connectors/list`, `/api/v1/admin/system/health`
- ✅ **Chat** - `/api/v1/chat` (HTTP fallback)

## How They Work Together

### Shared Configuration

Both systems use the **same environment variable**:

```bash
VITE_API_URL=https://synthralos-backend.onrender.com
```

**OpenAPI SDK:**
```typescript
OpenAPI.BASE = import.meta.env.VITE_API_URL
// Results in: https://synthralos-backend.onrender.com
```

**apiRequest():**
```typescript
const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000"
// Results in: https://synthralos-backend.onrender.com
```

### Shared Authentication

Both systems use **Supabase Auth** for authentication:

**OpenAPI SDK:**
```typescript
OpenAPI.TOKEN = async () => {
  const { data: { session } } = await supabase.auth.getSession()
  return session?.access_token || ""
}
// SDK automatically adds: Authorization: Bearer <token>
```

**apiRequest():**
```typescript
const { data: { session } } = await supabase.auth.getSession()
headers.set("Authorization", `Bearer ${session.access_token}`)
// Manually adds: Authorization: Bearer <token>
```

### URL Construction

Both construct URLs the same way:

**OpenAPI SDK:**
```typescript
// OpenAPI.BASE = "https://synthralos-backend.onrender.com"
// Endpoint: "/api/v1/users/me"
// Result: "https://synthralos-backend.onrender.com/api/v1/users/me"
UsersService.readUserMe()
```

**apiRequest():**
```typescript
// getApiUrl() = "https://synthralos-backend.onrender.com"
// Path: "/api/v1/stats/dashboard"
// Result: "https://synthralos-backend.onrender.com/api/v1/stats/dashboard"
apiRequest("/api/v1/stats/dashboard")
```

## When to Use Which

### Use OpenAPI SDK When:

✅ Endpoint is **in the OpenAPI schema** (users, login, utils)
✅ You want **type safety** and **autocomplete**
✅ You want **generated TypeScript types**
✅ Endpoint is **stable** and **well-defined**

**Example:**
```typescript
// ✅ Use OpenAPI SDK
import { UsersService } from "@/client"
const user = await UsersService.readUserMe() // Type-safe!
```

### Use apiRequest() When:

✅ Endpoint is **NOT in the OpenAPI schema** (stats, agents, workflows, etc.)
✅ Endpoint is **new** or **experimental**
✅ You need **FormData support** for file uploads
✅ Endpoint might **change frequently**

**Example:**
```typescript
// ✅ Use apiRequest()
import { apiRequest } from "@/lib/api"
const stats = await apiRequest("/api/v1/stats/dashboard")
```

## Migration Impact

### Before Migration

**Problem:** Components used relative URLs that resolved to frontend domain:

```typescript
// ❌ Relative URL - wrong domain
const response = await fetch("/api/v1/stats/dashboard", {
  headers: { Authorization: `Bearer ${token}` }
})
// Tried: https://synthralos-frontend.onrender.com/api/v1/stats/dashboard
// Result: 404 ❌
```

### After Migration

**Solution:** Both systems now correctly target backend domain:

**OpenAPI SDK (unchanged - was already correct):**
```typescript
// ✅ Already using OpenAPI.BASE = VITE_API_URL
UsersService.readUserMe()
// Uses: https://synthralos-backend.onrender.com/api/v1/users/me ✅
```

**apiRequest() (fixed - now uses backend URL):**
```typescript
// ✅ Now uses getApiUrl() = VITE_API_URL
apiRequest("/api/v1/stats/dashboard")
// Uses: https://synthralos-backend.onrender.com/api/v1/stats/dashboard ✅
```

## Benefits of This Architecture

### 1. Type Safety Where Possible
- OpenAPI SDK provides type safety for stable endpoints
- apiRequest() provides flexibility for new/experimental endpoints

### 2. Consistency
- Both use same `VITE_API_URL` environment variable
- Both use same Supabase authentication
- Both target same backend domain

### 3. Flexibility
- Can add new endpoints without regenerating OpenAPI SDK
- Can use OpenAPI SDK for stable, well-defined endpoints
- Can migrate endpoints from apiRequest() to OpenAPI SDK when ready

### 4. Best of Both Worlds
- **OpenAPI SDK**: Type safety, autocomplete, validation
- **apiRequest()**: Flexibility, FormData support, quick iteration

## Future Improvements

### Option 1: Expand OpenAPI Schema

Add more endpoints to backend OpenAPI schema, then regenerate SDK:

```bash
# Backend generates OpenAPI schema
# Frontend regenerates SDK
npm run generate:api

# Now can use:
import { StatsService } from "@/client"
const stats = await StatsService.getDashboardStats()
```

### Option 2: Keep Both Systems

Continue using:
- **OpenAPI SDK** for stable, well-defined endpoints
- **apiRequest()** for new, experimental, or frequently-changing endpoints

### Option 3: Create Hybrid Utility

Create a wrapper that tries OpenAPI SDK first, falls back to apiRequest():

```typescript
async function apiCall(endpoint: string, options?: RequestInit) {
  // Try OpenAPI SDK if available
  if (hasOpenAPIService(endpoint)) {
    return openAPICall(endpoint, options)
  }
  // Fall back to apiRequest()
  return apiRequest(endpoint, options)
}
```

## Summary

**OpenAPI SDK and apiRequest() work together:**

1. ✅ **Same configuration** - Both use `VITE_API_URL`
2. ✅ **Same authentication** - Both use Supabase Auth
3. ✅ **Same target** - Both hit backend domain
4. ✅ **Different purposes** - OpenAPI for type-safe stable endpoints, apiRequest() for flexible new endpoints
5. ✅ **Complementary** - Each serves its purpose without conflict

**The migration fixed apiRequest() to use backend URLs, while OpenAPI SDK was already correct. Both systems now work seamlessly together.**

