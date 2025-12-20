# Clarification: OpenAPI vs OpenAI

**Date:** December 18, 2025

## Important Distinction

### ❌ NOT OpenAI (The AI Company)

**OpenAI** is the company that created ChatGPT, GPT-4, DALL-E, etc. This is **NOT** what the frontend uses to communicate with the backend.

### ✅ OpenAPI (The API Specification Standard)

**OpenAPI** (formerly Swagger) is an **API specification standard** that defines how REST APIs are documented and consumed. This is what our frontend uses to communicate with the backend.

## What is OpenAPI?

OpenAPI is a specification for describing REST APIs. It allows:

1. **API Documentation** - Automatic documentation generation
2. **Code Generation** - Auto-generate client SDKs from API specs
3. **API Testing** - Generate test clients
4. **Type Safety** - TypeScript types generated from API schema

## How Our Codebase Uses OpenAPI

### 1. Backend Generates OpenAPI Spec

FastAPI automatically generates an OpenAPI specification:

```python
# backend/app/main.py
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",  # ← OpenAPI spec endpoint
)
```

**Accessible at:** `https://synthralos-backend.onrender.com/api/v1/openapi.json`

### 2. Frontend Generates SDK from OpenAPI Spec

The frontend uses `@hey-api/openapi-ts` to generate a TypeScript SDK:

```bash
# frontend/package.json
"generate-client": "openapi-ts"
```

This command:
1. Downloads the OpenAPI spec from the backend
2. Generates TypeScript types and client SDK
3. Creates `frontend/src/client/sdk.gen.ts` with all API methods

### 3. Frontend Uses Generated SDK

```typescript
// frontend/src/hooks/useAuth.ts
import { UsersService } from "@/client"  // ← Generated SDK

const userData = await UsersService.readUserMe()
// Makes: GET /api/v1/users/me
```

## Communication Flow

```
┌─────────────────────────────────────────────────────────┐
│  Backend (FastAPI)                                      │
│                                                         │
│  1. Defines API routes                                 │
│     @router.get("/users/me")                          │
│                                                         │
│  2. Auto-generates OpenAPI spec                        │
│     GET /api/v1/openapi.json                           │
│     ↓                                                   │
│     {                                                   │
│       "paths": {                                        │
│         "/api/v1/users/me": {                          │
│           "get": { ... }                               │
│         }                                               │
│       }                                                 │
│     }                                                   │
└─────────────────────────────────────────────────────────┘
                        │
                        │ HTTP GET
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│  Frontend Build Process                                 │
│                                                         │
│  1. Downloads OpenAPI spec                             │
│     npm run generate-client                             │
│                                                         │
│  2. Generates TypeScript SDK                           │
│     @hey-api/openapi-ts                                 │
│     ↓                                                   │
│     frontend/src/client/sdk.gen.ts                      │
│                                                         │
│  3. Generated SDK includes:                            │
│     - UsersService.readUserMe()                         │
│     - WorkflowsService.readWorkflows()                  │
│     - etc.                                              │
└─────────────────────────────────────────────────────────┘
                        │
                        │ Runtime
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│  Frontend (React)                                       │
│                                                         │
│  1. Uses generated SDK                                 │
│     import { UsersService } from "@/client"            │
│                                                         │
│  2. Makes API calls                                    │
│     await UsersService.readUserMe()                    │
│                                                         │
│  3. SDK constructs HTTP request                        │
│     GET https://backend.onrender.com/api/v1/users/me   │
└─────────────────────────────────────────────────────────┘
```

## What Was Defined in PRD.md?

### PRD.md Section: API Specifications

The PRD mentions:

```
## API Specifications
```

And shows:

```
│                            │ WebSocket + REST
```

**This means:**
- **REST API** - Standard HTTP REST endpoints (using OpenAPI spec)
- **WebSocket** - Real-time communication for chat/workflows

### What PRD.md Doesn't Specify

The PRD doesn't explicitly mention:
- Using OpenAPI specification standard
- Auto-generating frontend SDK from backend spec
- Using `@hey-api/openapi-ts` tool

**These are implementation details** chosen for:
- Type safety
- Code generation
- Maintainability
- Consistency between frontend and backend

## Why Use OpenAPI?

### Benefits

1. **Type Safety** - TypeScript types match backend exactly
2. **Auto-Generation** - No manual API client code
3. **Consistency** - Frontend always matches backend API
4. **Documentation** - Auto-generated API docs
5. **Validation** - Request/response validation

### Without OpenAPI

If we didn't use OpenAPI, we'd have to:
- Manually write API client code
- Manually maintain TypeScript types
- Manually update when backend changes
- Risk type mismatches

## How It Works in Render

### Development Flow

1. **Backend changes** - Add new endpoint
2. **Backend redeploys** - OpenAPI spec updates
3. **Frontend regenerates SDK** - `npm run generate-client`
4. **Frontend uses new endpoint** - TypeScript types available

### Production Flow

1. **Backend deployed** - OpenAPI spec available at `/api/v1/openapi.json`
2. **Frontend build** - Downloads spec, generates SDK
3. **Frontend deployed** - Uses generated SDK to call backend

## Summary

| Term | What It Is | Used For |
|------|------------|----------|
| **OpenAI** | AI company (ChatGPT, GPT-4) | ❌ NOT used for frontend-backend communication |
| **OpenAPI** | API specification standard | ✅ Used to generate frontend SDK from backend API |

**Key Points:**
- Frontend communicates with backend using **OpenAPI-generated SDK**
- OpenAPI is a **specification standard**, not a company
- PRD.md mentions REST API but doesn't specify OpenAPI (implementation detail)
- This is how modern web apps ensure type safety and consistency

## Related Documentation

- `docs/VITE_API_URL_EXPLANATION.md` - How OpenAPI SDK constructs URLs
- `docs/FRONTEND_BACKEND_INTERACTION.md` - Full communication flow
- `frontend/README.md` - How to regenerate SDK
