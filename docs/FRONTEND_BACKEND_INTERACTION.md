# Frontend-Backend Interaction Guide

**Date:** December 18, 2025

## Architecture Overview

SynthralOS uses a **decoupled frontend-backend architecture** deployed on Render:

```
┌─────────────────────────────────────────────────────────────┐
│                     User's Browser                          │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  React Frontend (synthralos-frontend.onrender.com)  │  │
│  │  - React + TypeScript + TanStack Router              │  │
│  │  - Supabase Auth Client (browser-side)               │  │
│  └─────────────────────────────────────────────────────┘  │
│                        │                                    │
│                        │ HTTPS                              │
│                        │                                    │
│                        ▼                                    │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  FastAPI Backend (synthralos-backend.onrender.com)  │  │
│  │  - FastAPI + Python                                  │  │
│  │  - Supabase Auth Server (token verification)         │  │
│  │  - Supabase Database (PostgreSQL)                    │  │
│  │  - Supabase Storage                                  │  │
│  └─────────────────────────────────────────────────────┘  │
│                        │                                    │
│                        │                                    │
│                        ▼                                    │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  Supabase (External Service)                        │  │
│  │  - Authentication                                    │  │
│  │  - Database (PostgreSQL)                             │  │
│  │  - Storage                                           │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Deployment URLs

After deploying with Render Blueprint:

- **Frontend:** `https://synthralos-frontend.onrender.com`
- **Backend:** `https://synthralos-backend.onrender.com`
- **Backend API:** `https://synthralos-backend.onrender.com/api/v1`

## Authentication Flow

### 1. User Login (Frontend → Supabase → Backend)

```
1. User enters credentials in frontend
   ↓
2. Frontend calls Supabase Auth: supabase.auth.signInWithPassword()
   ↓
3. Supabase returns JWT access_token
   ↓
4. Frontend stores token in browser (Supabase client handles this)
   ↓
5. Frontend makes API calls to backend with token in Authorization header
   ↓
6. Backend verifies token with Supabase and returns user data
```

### 2. API Request Flow

```
Frontend Component
  ↓
OpenAPI SDK (auto-generated from backend OpenAPI spec)
  ↓
HTTP Request: GET https://synthralos-backend.onrender.com/api/v1/users/me
  Headers:
    Authorization: Bearer <supabase_jwt_token>
  ↓
Backend FastAPI Endpoint
  ↓
Supabase Token Verification (get_current_user dependency)
  ↓
Database Query (Supabase PostgreSQL)
  ↓
Response: User data
```

## Configuration

### Frontend Environment Variables

Set in Render Dashboard → `synthralos-frontend` → Environment:

```bash
VITE_API_URL=https://synthralos-backend.onrender.com
VITE_SUPABASE_URL=https://lorefpaifkembnzmlodm.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Important:** `VITE_API_URL` should be the **base URL only** (without `/api/v1`). The OpenAPI SDK automatically adds `/api/v1` to all endpoints.

### Backend Environment Variables

Set in Render Dashboard → `synthralos-backend` → Environment:

```bash
SUPABASE_URL=https://lorefpaifkembnzmlodm.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_DB_URL=postgresql://postgres:password@db.lorefpaifkembnzmlodm.supabase.co:5432/postgres
FRONTEND_HOST=https://synthralos-frontend.onrender.com
BACKEND_CORS_ORIGINS=https://synthralos-frontend.onrender.com
```

## API Communication

### How Frontend Calls Backend

1. **OpenAPI SDK** (`frontend/src/client/sdk.gen.ts`):
   - Auto-generated from backend OpenAPI spec
   - Base URL set via `OpenAPI.BASE = import.meta.env.VITE_API_URL`
   - Token automatically added via `OpenAPI.TOKEN` callback

2. **Example API Call:**

```typescript
// frontend/src/hooks/useAuth.ts
import { UsersService } from "@/client"

const userData = await UsersService.readUserMe()
// Makes: GET https://synthralos-backend.onrender.com/api/v1/users/me
// Headers: Authorization: Bearer <token>
```

3. **Direct Fetch Calls:**

Some components use direct `fetch()` calls:

```typescript
// frontend/src/components/Dashboard/DashboardStats.tsx
const response = await fetch("/api/v1/stats/dashboard", {
  headers: {
    Authorization: `Bearer ${token}`
  }
})
```

**Note:** In production, these `/api/v1/...` paths are relative and will be resolved to the backend URL. The frontend's Vite proxy is only used in development.

### CORS Configuration

Backend CORS is configured to allow requests from the frontend:

```python
# backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.all_cors_origins,  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Data Flow Examples

### Example 1: User Login

```
1. User submits login form
   ↓
2. Frontend: supabase.auth.signInWithPassword({ email, password })
   ↓
3. Supabase: Validates credentials, returns JWT token
   ↓
4. Frontend: Stores token, calls UsersService.readUserMe()
   ↓
5. Backend: Verifies token, queries database, returns user data
   ↓
6. Frontend: Updates UI with user data
```

### Example 2: Creating a Workflow

```
1. User creates workflow in frontend
   ↓
2. Frontend: fetch("/api/v1/workflows", { method: "POST", body: workflowData })
   ↓
3. Backend: Validates token, saves to Supabase database
   ↓
4. Backend: Returns created workflow
   ↓
5. Frontend: Updates UI, shows success message
```

### Example 3: File Upload (OCR)

```
1. User uploads file in frontend
   ↓
2. Frontend: Uploads to Supabase Storage via frontend SDK
   ↓
3. Frontend: Calls backend OCR API with file reference
   ↓
4. Backend: Reads file from Supabase Storage, processes with OCR engine
   ↓
5. Backend: Returns OCR results
   ↓
6. Frontend: Displays results
```

## WebSocket Connections

### Chat Interface

The chat interface uses WebSocket for real-time communication:

```
Frontend: ws://synthralos-backend.onrender.com/api/v1/agws?token=<jwt>
  ↓
Backend: WebSocket endpoint handles chat messages
  ↓
Real-time bidirectional communication
```

## Health Checks

Render automatically checks backend health:

```
GET https://synthralos-backend.onrender.com/api/v1/utils/health-check
Response: true (200 OK)
```

## Common Issues and Solutions

### Issue 1: Double `/api/v1` in URL

**Symptom:** `GET /api/v1/api/v1/users/me` returns 404

**Cause:** `VITE_API_URL` includes `/api/v1` when it shouldn't

**Solution:** Set `VITE_API_URL=https://synthralos-backend.onrender.com` (without `/api/v1`)

### Issue 2: CORS Errors

**Symptom:** `Access-Control-Allow-Origin` errors in browser console

**Solution:** Ensure `BACKEND_CORS_ORIGINS` includes the frontend URL

### Issue 3: 401 Unauthorized

**Symptom:** API calls return 401 even after login

**Solution:**
- Check token is being sent: `Authorization: Bearer <token>`
- Verify token hasn't expired
- Check Supabase Auth configuration

### Issue 4: 307 Redirect on Health Check

**Symptom:** Health check returns 307 Temporary Redirect

**Solution:** Use `/api/v1/utils/health-check` (without trailing slash)

## Monitoring

### Backend Logs

View in Render Dashboard → `synthralos-backend` → Logs

**Key log messages:**
- `✅ FastAPI app initialization complete` - Server started
- `✅ Tesseract OCR engine initialized` - OCR ready
- `INFO: Uvicorn running on http://0.0.0.0:10000` - Server listening

### Frontend Logs

View in Render Dashboard → `synthralos-frontend` → Logs

**Key log messages:**
- `nginx/1.29.4` - Nginx server started
- `Your service is live 🎉` - Deployment successful

## Testing the Connection

### 1. Test Backend Health

```bash
curl https://synthralos-backend.onrender.com/api/v1/utils/health-check
# Expected: true
```

### 2. Test Frontend

Open `https://synthralos-frontend.onrender.com` in browser

### 3. Test API with Token

```bash
# Get token from browser (after login)
TOKEN="your_jwt_token"

curl -H "Authorization: Bearer $TOKEN" \
  https://synthralos-backend.onrender.com/api/v1/users/me
```

## Related Documentation

- `docs/RENDER_DEPLOYMENT.md` - Full deployment guide
- `docs/SUPABASE_DATABASE_MIGRATION.md` - Supabase setup
- `render.yaml` - Blueprint configuration
