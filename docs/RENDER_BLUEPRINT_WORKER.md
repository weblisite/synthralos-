# Worker in Render Blueprint - Explanation

## Current Blueprint Structure

Your `render.yaml` blueprint now contains **3 services**:

```yaml
services:
  # 1. Backend API Service (Web Service)
  - type: web
    name: synthralos-backend
    # ... handles HTTP requests

  # 2. Frontend Service (Web Service)
  - type: web
    name: synthralos-frontend
    # ... serves React UI

  # 3. Workflow Worker (Background Worker) ← NEW!
  - type: worker
    name: synthralos-workflow-worker
    # ... processes workflow executions
```

## Where the Worker Is

The worker is **already added** to your `render.yaml` blueprint at **line 240**.

It's configured as:
- **Type**: `worker` (Background Worker service)
- **Name**: `synthralos-workflow-worker`
- **Dockerfile**: `./backend/Dockerfile.worker`
- **Plan**: `starter` ($7/month)

## How Render Blueprint Works

When you push to GitHub and Render processes your blueprint:

1. **Render reads `render.yaml`**
2. **Creates all services** listed in the `services:` section:
   - ✅ Backend web service
   - ✅ Frontend web service
   - ✅ **Worker service** (automatically created!)
3. **Deploys all services** automatically

**The worker will be created automatically** - you don't need to do anything manually!

## Service Types in Render

- **`type: web`** - Web service (handles HTTP requests, has a URL)
  - Your backend and frontend use this
  - Gets a public URL (e.g., `https://synthralos-backend.onrender.com`)

- **`type: worker`** - Background worker (runs continuously, no HTTP endpoint)
  - Your worker uses this
  - No public URL (runs in background)
  - Processes tasks from database

## What Happens When You Deploy

### Step 1: Push to GitHub

```bash
git add render.yaml backend/Dockerfile.worker
git commit -m "Add workflow worker to blueprint"
git push
```

### Step 2: Render Processes Blueprint

Render will:
1. ✅ Detect changes in `render.yaml`
2. ✅ Create worker service (if it doesn't exist)
3. ✅ Build worker Docker image from `Dockerfile.worker`
4. ✅ Deploy worker service

### Step 3: Configure Environment Variables

After deployment, go to Render Dashboard:

1. **Open Worker Service** → `synthralos-workflow-worker`
2. **Go to Environment** tab
3. **Add environment variables** (same as backend):
   - `SUPABASE_DB_URL` (required)
   - `SUPABASE_URL` (required)
   - `SUPABASE_ANON_KEY` (required)
   - `SECRET_KEY` (required)
   - `WORKFLOW_WORKER_CONCURRENCY=10` (optional)
   - All other backend env vars

### Step 4: Verify Worker Running

1. **Check Logs**: Worker Service → Logs
2. **Look for**: `🚀 Workflow worker started (poll_interval=1.0s)`
3. **Test**: Create and run a workflow

## Blueprint Structure Explained

```
render.yaml
└── services:
    ├── Backend (type: web)
    │   └── Handles HTTP API requests
    │
    ├── Frontend (type: web)
    │   └── Serves React UI
    │
    └── Worker (type: worker) ← This is where your worker is!
        └── Processes workflow executions
```

All three services are **siblings** in the blueprint - they're separate but work together.

## Important Notes

✅ **Worker is separate service** - Not part of backend or frontend
✅ **Automatically created** - When blueprint is processed
✅ **Same codebase** - Uses `backend/Dockerfile.worker`
✅ **Same database** - Connects to same Supabase database
✅ **Different purpose** - Processes executions, doesn't serve HTTP

## Deployment Checklist

- [x] Worker added to `render.yaml` blueprint
- [x] `Dockerfile.worker` created
- [ ] **Push to GitHub** (triggers Render deployment)
- [ ] **Set environment variables** in Render dashboard
- [ ] **Verify worker running** (check logs)
- [ ] **Test workflow execution** end-to-end

## Summary

**The worker is already in your blueprint!** It's configured as:
- **Type**: `worker` (Background Worker)
- **Location**: After frontend service in `render.yaml`
- **Status**: Will be created automatically when you push

**Next step**: Push to GitHub, and Render will create all 3 services (backend, frontend, worker) automatically!
