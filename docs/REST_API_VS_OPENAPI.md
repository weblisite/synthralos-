# REST API vs OpenAPI: Key Differences Explained

**Date:** December 18, 2025

## Quick Answer

- **REST API** = An **architectural style/pattern** for building web services
- **OpenAPI** = A **specification format** for describing/documenting APIs

They're related but serve different purposes:
- **REST** = How you **build** the API
- **OpenAPI** = How you **document** the API

## Detailed Explanation

### REST API (Representational State Transfer)

**What it is:** An architectural style/pattern for designing web services

**Key characteristics:**
- Uses HTTP methods (GET, POST, PUT, DELETE, etc.)
- Stateless (each request contains all information needed)
- Resource-based URLs (`/users/123`, `/workflows/456`)
- Standard HTTP status codes (200, 404, 500, etc.)
- JSON/XML data formats

**Example REST API endpoint:**
```
GET /api/v1/users/123
POST /api/v1/workflows
PUT /api/v1/workflows/456
DELETE /api/v1/users/123
```

**REST is a concept/pattern** - it's not a file format or tool.

### OpenAPI (Formerly Swagger)

**What it is:** A specification format (file format) for describing REST APIs

**Key characteristics:**
- Machine-readable format (YAML or JSON)
- Describes endpoints, request/response schemas, authentication
- Used for documentation, code generation, testing
- Standardized format (OpenAPI 3.0, 3.1)

**Example OpenAPI spec snippet:**
```yaml
openapi: 3.0.0
info:
  title: SynthralOS API
  version: 1.0.0
paths:
  /api/v1/users/me:
    get:
      summary: Get current user
      responses:
        '200':
          description: User data
          content:
            application/json:
              schema:
                type: object
                properties:
                  id:
                    type: string
                  email:
                    type: string
```

**OpenAPI is a file format** - it's a way to describe APIs.

## Visual Comparison

### REST API (Architecture)

```
┌─────────────────────────────────────────┐
│  REST API Architecture                  │
│                                         │
│  Client → HTTP Request → Server         │
│                                         │
│  GET  /api/v1/users/123                │
│  POST /api/v1/workflows                │
│  PUT  /api/v1/workflows/456             │
│  DELETE /api/v1/users/123              │
│                                         │
│  Uses:                                  │
│  - HTTP methods                         │
│  - Resource URLs                        │
│  - Status codes                         │
│  - JSON/XML                             │
└─────────────────────────────────────────┘
```

### OpenAPI (Specification)

```
┌─────────────────────────────────────────┐
│  OpenAPI Specification                  │
│                                         │
│  openapi.json / openapi.yaml            │
│                                         │
│  Describes:                             │
│  - Endpoints                            │
│  - Request schemas                      │
│  - Response schemas                     │
│  - Authentication                      │
│                                         │
│  Used for:                              │
│  - Documentation                        │
│  - Code generation                     │
│  - API testing                         │
└─────────────────────────────────────────┘
```

## How They Work Together

### In Our Codebase

```
┌─────────────────────────────────────────────────────────┐
│  Step 1: Build REST API (Backend)                       │
│                                                         │
│  FastAPI automatically creates REST endpoints:          │
│                                                         │
│  @router.get("/users/me")                              │
│  def get_current_user():                                │
│      return user_data                                   │
│                                                         │
│  This follows REST principles:                          │
│  - GET method                                           │
│  - Resource URL (/users/me)                            │
│  - JSON response                                        │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  Step 2: Generate OpenAPI Spec (Backend)                │
│                                                         │
│  FastAPI auto-generates OpenAPI spec:                   │
│                                                         │
│  GET /api/v1/openapi.json                              │
│                                                         │
│  Returns:                                               │
│  {                                                      │
│    "openapi": "3.0.0",                                 │
│    "paths": {                                           │
│      "/api/v1/users/me": {                             │
│        "get": { ... }                                   │
│      }                                                  │
│    }                                                    │
│  }                                                      │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  Step 3: Generate Frontend SDK (Frontend)               │
│                                                         │
│  @hey-api/openapi-ts reads OpenAPI spec:               │
│                                                         │
│  npm run generate-client                                │
│                                                         │
│  Generates:                                             │
│  - TypeScript types                                     │
│  - SDK methods (UsersService.readUserMe())             │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  Step 4: Use SDK (Frontend)                            │
│                                                         │
│  Frontend calls REST API using generated SDK:           │
│                                                         │
│  await UsersService.readUserMe()                       │
│  → Makes HTTP GET request                              │
│  → To REST endpoint: /api/v1/users/me                 │
└─────────────────────────────────────────────────────────┘
```

## Key Differences Table

| Aspect | REST API | OpenAPI |
|--------|----------|---------|
| **Type** | Architectural pattern/style | Specification format |
| **Purpose** | How to build web services | How to describe APIs |
| **Format** | Not a format (it's a concept) | YAML or JSON file |
| **Scope** | Design principles | API documentation |
| **Tools** | None (it's a pattern) | Swagger UI, code generators |
| **Example** | `GET /users/123` | `openapi.json` file |

## Real-World Analogy

Think of building a house:

- **REST API** = The architectural style (like "Modern" or "Victorian")
  - Defines principles: use standard materials, follow building codes
  - Similar to REST: use HTTP methods, follow REST principles

- **OpenAPI** = The blueprints/drawings
  - Describes exactly what to build: dimensions, materials, layout
  - Similar to OpenAPI: describes endpoints, schemas, authentication

You can build a REST API without OpenAPI (just code it), but OpenAPI helps document and generate code for it.

## Examples

### Example 1: REST API Endpoint (Code)

```python
# backend/app/api/routes/users.py
@router.get("/users/me")
def get_current_user(current_user: CurrentUser):
    """Get current user - REST API endpoint"""
    return {
        "id": current_user.id,
        "email": current_user.email
    }
```

This is a **REST API endpoint** - it follows REST principles:
- Uses GET method
- Resource-based URL (`/users/me`)
- Returns JSON

### Example 2: OpenAPI Spec (Description)

```yaml
# Generated from the code above
paths:
  /api/v1/users/me:
    get:
      summary: Get current user
      tags:
        - users
      security:
        - bearerAuth: []
      responses:
        '200':
          description: User data
          content:
            application/json:
              schema:
                type: object
                properties:
                  id:
                    type: string
                    format: uuid
                  email:
                    type: string
                    format: email
```

This is an **OpenAPI specification** - it describes the REST API endpoint.

### Example 3: Using Both Together

```typescript
// Frontend uses OpenAPI-generated SDK to call REST API

// 1. OpenAPI spec was used to generate this SDK method
import { UsersService } from "@/client"

// 2. SDK method makes REST API call
const user = await UsersService.readUserMe()
// → HTTP GET /api/v1/users/me (REST API call)
```

## Common Misconceptions

### ❌ "REST API and OpenAPI are the same"

**Reality:** REST is an architecture, OpenAPI is a specification format.

### ❌ "You need OpenAPI to build a REST API"

**Reality:** You can build REST APIs without OpenAPI. OpenAPI is for documentation/code generation.

### ❌ "OpenAPI is a type of API"

**Reality:** OpenAPI describes APIs. It's not an API itself - it's metadata about APIs.

### ✅ "OpenAPI describes REST APIs"

**Reality:** Yes! OpenAPI is commonly used to describe REST APIs (though it can describe other API types too).

## In Our Codebase

### What We Have

1. **REST API** (Backend)
   - FastAPI creates REST endpoints
   - Follows REST principles
   - Located in `backend/app/api/routes/`

2. **OpenAPI Spec** (Backend)
   - Auto-generated by FastAPI
   - Available at `/api/v1/openapi.json`
   - Describes all REST endpoints

3. **OpenAPI SDK** (Frontend)
   - Generated from OpenAPI spec
   - Located in `frontend/src/client/`
   - Used to call REST API endpoints

### Workflow

```
REST API Code (Python)
    ↓
FastAPI generates OpenAPI spec
    ↓
OpenAPI spec downloaded
    ↓
Frontend SDK generated from spec
    ↓
Frontend uses SDK to call REST API
```

## Summary

| Concept | What It Is | Example |
|---------|------------|---------|
| **REST API** | Architectural pattern for building web services | `GET /api/v1/users/123` |
| **OpenAPI** | Specification format for describing APIs | `openapi.json` file |
| **Relationship** | OpenAPI describes REST APIs | OpenAPI spec documents REST endpoints |

**Key Takeaway:**
- **REST** = How you build APIs (architectural pattern)
- **OpenAPI** = How you describe APIs (specification format)
- They work together: REST APIs are built, OpenAPI describes them

## Related Documentation

- `docs/OPENAPI_VS_OPENAI_CLARIFICATION.md` - OpenAPI vs OpenAI (the company)
- `docs/FRONTEND_BACKEND_INTERACTION.md` - How frontend and backend communicate
- `docs/VITE_API_URL_EXPLANATION.md` - How OpenAPI SDK constructs URLs
