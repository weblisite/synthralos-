# Detailed Explanation: VITE_API_URL and Double /api/v1 Issue

**Date:** December 18, 2025

## The Problem

When you see API calls like `/api/v1/api/v1/users/me` (with double `/api/v1`), it means the frontend is incorrectly constructing URLs. This causes 404 errors because the backend doesn't have endpoints at that path.

## Root Cause

The issue occurs because:

1. **OpenAPI SDK endpoints already include `/api/v1`** in their URL paths
2. **`VITE_API_URL` is being set to include `/api/v1`** when it shouldn't
3. **The SDK combines BASE URL + endpoint URL**, resulting in double prefix

## How URL Construction Works

### Step-by-Step Process

Let's trace through what happens when `UsersService.readUserMe()` is called:

#### Step 1: Frontend Code Calls SDK

```typescript
// frontend/src/hooks/useAuth.ts
const userData = await UsersService.readUserMe()
```

#### Step 2: SDK Method Definition

The SDK method is defined with `/api/v1` already in the path:

```typescript
// frontend/src/client/sdk.gen.ts (line 288-293)
public static readUserMe(): CancelablePromise<UsersReadUserMeResponse> {
    return __request(OpenAPI, {
        method: 'GET',
        url: '/api/v1/users/me'  // ← Already includes /api/v1
    });
}
```

**Key Point:** Every endpoint in `sdk.gen.ts` already has `/api/v1` in the URL path.

#### Step 3: OpenAPI.BASE Configuration

The base URL is set from environment variable:

```typescript
// frontend/src/main.tsx (line 17)
OpenAPI.BASE = import.meta.env.VITE_API_URL
```

#### Step 4: URL Construction in Request Function

The `__request` function combines BASE + endpoint URL:

```typescript
// frontend/src/client/core/request.ts (simplified)
function __request(config, options) {
    const url = `${OpenAPI.BASE}${options.url}`
    // Makes HTTP request to this URL
}
```

### What Happens with Wrong Configuration

#### ❌ WRONG: VITE_API_URL includes /api/v1

```bash
# Environment variable (WRONG)
VITE_API_URL=https://synthralos-backend.onrender.com/api/v1
```

**URL Construction:**
```
OpenAPI.BASE = "https://synthralos-backend.onrender.com/api/v1"
options.url = "/api/v1/users/me"

Final URL = OpenAPI.BASE + options.url
         = "https://synthralos-backend.onrender.com/api/v1" + "/api/v1/users/me"
         = "https://synthralos-backend.onrender.com/api/v1/api/v1/users/me"
```

**Result:** ❌ 404 Not Found (endpoint doesn't exist)

### What Happens with Correct Configuration

#### ✅ CORRECT: VITE_API_URL is base URL only

```bash
# Environment variable (CORRECT)
VITE_API_URL=https://synthralos-backend.onrender.com
```

**URL Construction:**
```
OpenAPI.BASE = "https://synthralos-backend.onrender.com"
options.url = "/api/v1/users/me"

Final URL = OpenAPI.BASE + options.url
         = "https://synthralos-backend.onrender.com" + "/api/v1/users/me"
         = "https://synthralos-backend.onrender.com/api/v1/users/me"
```

**Result:** ✅ 200 OK (endpoint exists)

## Visual Comparison

### Wrong Configuration Flow

```
┌─────────────────────────────────────────────────────────┐
│ 1. Environment Variable                                  │
│    VITE_API_URL=https://backend.onrender.com/api/v1     │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 2. OpenAPI.BASE Set                                     │
│    OpenAPI.BASE = "https://backend.onrender.com/api/v1"│
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 3. SDK Method Called                                     │
│    UsersService.readUserMe()                            │
│    url: "/api/v1/users/me"                              │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 4. URL Construction                                      │
│    Final = BASE + url                                   │
│    = "https://backend.onrender.com/api/v1" +            │
│      "/api/v1/users/me"                                 │
│    = "https://backend.onrender.com/api/v1/api/v1/users/me"│
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 5. HTTP Request                                          │
│    GET /api/v1/api/v1/users/me                          │
│    ❌ 404 Not Found                                      │
└─────────────────────────────────────────────────────────┘
```

### Correct Configuration Flow

```
┌─────────────────────────────────────────────────────────┐
│ 1. Environment Variable                                  │
│    VITE_API_URL=https://backend.onrender.com           │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 2. OpenAPI.BASE Set                                     │
│    OpenAPI.BASE = "https://backend.onrender.com"       │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 3. SDK Method Called                                     │
│    UsersService.readUserMe()                            │
│    url: "/api/v1/users/me"                              │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 4. URL Construction                                      │
│    Final = BASE + url                                   │
│    = "https://backend.onrender.com" +                   │
│      "/api/v1/users/me"                                 │
│    = "https://backend.onrender.com/api/v1/users/me"     │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 5. HTTP Request                                          │
│    GET /api/v1/users/me                                 │
│    ✅ 200 OK                                             │
└─────────────────────────────────────────────────────────┘
```

## Why SDK Endpoints Include /api/v1

The OpenAPI SDK is **auto-generated** from the backend's OpenAPI specification. The backend defines all routes with `/api/v1` prefix:

```python
# backend/app/main.py
app.include_router(api_router, prefix=settings.API_V1_STR)  # /api/v1

# backend/app/api/routes/users.py
router = APIRouter(prefix="/users", tags=["users"])

# Final route: /api/v1/users/me
```

When the OpenAPI spec is generated, it includes the full path including `/api/v1`, so the SDK methods are generated with `/api/v1` already in the URL.

## How to Fix

### Step 1: Identify Current Value

Check what `VITE_API_URL` is currently set to in Render:

1. Go to **Render Dashboard**
2. Click **`synthralos-frontend`** service
3. Click **Environment** tab
4. Find **`VITE_API_URL`** variable

### Step 2: Update the Value

**If it's currently:**
```
https://synthralos-backend.onrender.com/api/v1
```

**Change it to:**
```
https://synthralos-backend.onrender.com
```

**Remove `/api/v1` from the end.**

### Step 3: Save and Redeploy

1. Click **Save Changes**
2. Render will automatically redeploy the frontend
3. Wait for deployment to complete (~2-3 minutes)

### Step 4: Verify

After redeployment, check browser DevTools:

1. Open your frontend: `https://synthralos-frontend.onrender.com`
2. Open **DevTools** → **Network** tab
3. Look for API calls to `/api/v1/users/me`
4. **Should see:** `/api/v1/users/me` (single prefix) ✅
5. **Should NOT see:** `/api/v1/api/v1/users/me` (double prefix) ❌

## Examples from Codebase

### Example 1: UsersService.readUserMe()

**SDK Definition:**
```typescript
// frontend/src/client/sdk.gen.ts
public static readUserMe() {
    return __request(OpenAPI, {
        method: 'GET',
        url: '/api/v1/users/me'  // ← Has /api/v1
    });
}
```

**Usage:**
```typescript
// frontend/src/hooks/useAuth.ts
const userData = await UsersService.readUserMe()
```

**With Correct VITE_API_URL:**
```
BASE: https://synthralos-backend.onrender.com
URL: /api/v1/users/me
Final: https://synthralos-backend.onrender.com/api/v1/users/me ✅
```

**With Wrong VITE_API_URL:**
```
BASE: https://synthralos-backend.onrender.com/api/v1
URL: /api/v1/users/me
Final: https://synthralos-backend.onrender.com/api/v1/api/v1/users/me ❌
```

### Example 2: WorkflowsService.readWorkflows()

**SDK Definition:**
```typescript
// frontend/src/client/sdk.gen.ts
public static readWorkflows() {
    return __request(OpenAPI, {
        method: 'GET',
        url: '/api/v1/workflows'  // ← Has /api/v1
    });
}
```

**With Correct VITE_API_URL:**
```
BASE: https://synthralos-backend.onrender.com
URL: /api/v1/workflows
Final: https://synthralos-backend.onrender.com/api/v1/workflows ✅
```

**With Wrong VITE_API_URL:**
```
BASE: https://synthralos-backend.onrender.com/api/v1
URL: /api/v1/workflows
Final: https://synthralos-backend.onrender.com/api/v1/api/v1/workflows ❌
```

## Direct Fetch Calls (Not Using SDK)

Some components use direct `fetch()` calls instead of the SDK:

```typescript
// frontend/src/components/Dashboard/DashboardStats.tsx
const response = await fetch("/api/v1/stats/dashboard", {
    headers: {
        Authorization: `Bearer ${token}`
    }
})
```

**Important:** These relative URLs (`/api/v1/...`) work differently:

- **In Development:** Vite proxy forwards to backend
- **In Production:** Browser resolves relative to current domain

For production, these should use absolute URLs or the SDK.

## Summary

| Configuration | VITE_API_URL Value | Result |
|--------------|-------------------|--------|
| ❌ **Wrong** | `https://backend.onrender.com/api/v1` | Double prefix: `/api/v1/api/v1/...` → 404 |
| ✅ **Correct** | `https://backend.onrender.com` | Single prefix: `/api/v1/...` → 200 |

**Key Rule:** `VITE_API_URL` should be the **base URL only** (domain + port, no path). The SDK automatically adds `/api/v1` to all endpoints.

## Related Documentation

- `docs/FRONTEND_BACKEND_INTERACTION.md` - How frontend and backend communicate
- `docs/DEPLOYMENT_WARNINGS.md` - Common deployment issues
- `render.yaml` - Blueprint configuration

