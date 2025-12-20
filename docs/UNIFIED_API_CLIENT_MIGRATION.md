# Unified API Client Migration

## Overview

All API calls across the platform now use a unified `apiClient` interface that defaults to `apiRequest()` but leverages OpenAPI SDK when available for type safety.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend Components                      │
│              (All use apiClient interface)                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │   apiClient          │
            │   (Unified Interface)│
            └──────────┬───────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
        ▼                             ▼
┌──────────────┐            ┌─────────────────┐
│ OpenAPI SDK  │            │  apiRequest()    │
│ (Type-safe)  │            │  (Default)       │
│              │            │                  │
│ - Users      │            │ - Dashboard      │
│ - Auth       │            │ - Agents         │
│ - Utils      │            │ - Connectors    │
│              │            │ - Workflows     │
│              │            │ - RAG           │
│              │            │ - OCR           │
│              │            │ - Scraping      │
│              │            │ - Browser       │
│              │            │ - OSINT         │
│              │            │ - Code          │
│              │            │ - Storage        │
│              │            │ - Admin         │
│              │            │ - Chat          │
└──────────────┘            └─────────────────┘
```

## Usage

### Using apiClient for OpenAPI SDK endpoints

```typescript
import { apiClient } from "@/lib/apiClient"

// Users API (uses OpenAPI SDK internally)
const user = await apiClient.users.getMe()
const users = await apiClient.users.getAll(0, 100)
await apiClient.users.create(userData)
await apiClient.users.update(userId, userData)
await apiClient.users.delete(userId)

// Auth API (uses OpenAPI SDK internally)
await apiClient.auth.recoverPassword(email)
await apiClient.auth.resetPassword(token, newPassword)

// Utils API (uses OpenAPI SDK internally)
await apiClient.utils.healthCheck()
```

### Using apiClient.request() for other endpoints

```typescript
import { apiClient } from "@/lib/apiClient"

// Dashboard stats (uses apiRequest internally)
const stats = await apiClient.request<DashboardStats>("/api/v1/stats/dashboard")

// Agents (uses apiRequest internally)
const frameworks = await apiClient.request("/api/v1/agents/catalog")
await apiClient.request("/api/v1/agents/run", {
  method: "POST",
  body: JSON.stringify({ task_type: "analyze", input_data: {} })
})

// Workflows (uses apiRequest internally)
const workflow = await apiClient.request("/api/v1/workflows", {
  method: "POST",
  body: JSON.stringify({ name: "My Workflow" })
})
```

## Migration Summary

### Before Migration

Components used either:
- Direct OpenAPI SDK calls: `UsersService.readUserMe()`
- Direct `apiRequest()` calls: `apiRequest("/api/v1/stats/dashboard")`

### After Migration

All components now use:
- `apiClient.users.*` for user operations (wraps OpenAPI SDK)
- `apiClient.auth.*` for auth operations (wraps OpenAPI SDK)
- `apiClient.request()` for all other endpoints (uses apiRequest internally)

## Benefits

1. **Unified Interface**: Single entry point for all API calls
2. **Type Safety**: OpenAPI SDK provides types for stable endpoints
3. **Flexibility**: apiRequest() handles new/experimental endpoints
4. **Consistency**: All API calls go through same authentication and URL construction
5. **Maintainability**: Easy to add new endpoints or migrate to OpenAPI SDK

## Files Updated

### Core API Files
- `frontend/src/lib/apiClient.ts` - New unified API client
- `frontend/src/lib/api.ts` - Base apiRequest utility (unchanged)

### Components Updated
- `frontend/src/hooks/useAuth.ts` - Uses `apiClient.users.getMe()`
- `frontend/src/components/Admin/*` - All use `apiClient`
- `frontend/src/components/UserSettings/*` - All use `apiClient`
- `frontend/src/components/Dashboard/*` - Uses `apiClient.request()`
- `frontend/src/components/Agents/*` - Uses `apiClient.request()`
- `frontend/src/components/Connectors/*` - Uses `apiClient.request()`
- `frontend/src/components/Workflow/*` - Uses `apiClient.request()`
- `frontend/src/components/RAG/*` - Uses `apiClient.request()`
- `frontend/src/components/OCR/*` - Uses `apiClient.request()`
- `frontend/src/components/Scraping/*` - Uses `apiClient.request()`
- `frontend/src/components/Browser/*` - Uses `apiClient.request()`
- `frontend/src/components/OSINT/*` - Uses `apiClient.request()`
- `frontend/src/components/Code/*` - Uses `apiClient.request()`
- `frontend/src/components/Storage/*` - Uses `apiClient.request()`
- `frontend/src/components/Chat/*` - Uses `apiClient.request()`
- `frontend/src/routes/*` - All use `apiClient`

## Configuration

Both systems use the same environment variable:

```bash
VITE_API_URL=https://synthralos-backend.onrender.com
```

Both systems use Supabase Auth for authentication automatically.

## Future Enhancements

1. **Expand OpenAPI Schema**: Add more endpoints to backend OpenAPI schema
2. **Regenerate SDK**: Run `npm run generate:api` to update SDK
3. **Migrate to apiClient**: Update components to use `apiClient.*` methods instead of `apiClient.request()`

## Example: Migrating a Component

### Before
```typescript
import { apiRequest } from "@/lib/api"

const fetchStats = async () => {
  return apiRequest<DashboardStats>("/api/v1/stats/dashboard")
}
```

### After
```typescript
import { apiClient } from "@/lib/apiClient"

const fetchStats = async () => {
  return apiClient.request<DashboardStats>("/api/v1/stats/dashboard")
}
```

Both work identically, but using `apiClient` provides:
- Consistent interface across platform
- Easy migration path to OpenAPI SDK when endpoint is added to schema
- Centralized error handling and authentication
