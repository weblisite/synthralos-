# Production Worker Setup - Quick Guide

## The Problem

When users click "Run" on a workflow in production:
1. ✅ API creates execution in database
2. ❌ **Without worker**: Execution stays in database, never runs
3. ✅ **With worker**: Worker picks it up and executes it

**The worker MUST be running in production for workflows to execute.**

## Solution: Render Background Worker

Since you're using Render, deploy the worker as a **Background Worker** service.

## Quick Setup (5 Minutes)

### Step 1: Create Worker Dockerfile

File: `backend/Dockerfile.worker` (already created ✅)

### Step 2: Update render.yaml

Add worker service to `render.yaml` (already updated ✅)

### Step 3: Deploy

1. **Push to GitHub**:
```bash
git add backend/Dockerfile.worker render.yaml
git commit -m "Add workflow worker for production"
git push
```

2. **Render will auto-deploy** the worker service

### Step 4: Configure Environment Variables

In Render Dashboard → Worker Service → Environment:

Copy **all environment variables** from your backend service:
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_DB_URL` (auto-set from database)
- `SECRET_KEY`
- `ENVIRONMENT=production`
- `WORKFLOW_WORKER_CONCURRENCY=10`
- All other backend env vars

### Step 5: Verify

1. **Check Logs**: Render Dashboard → Worker → Logs
2. **Look for**: `🚀 Workflow worker started (poll_interval=1.0s)`
3. **Test**: Create and run a workflow in frontend
4. **Check**: Execution should complete (check Executions tab)

## How It Works in Production

```
User clicks "Run" in frontend
    ↓
API Server (Render Web Service)
    ↓ Creates execution (status="running")
    ↓
Database (PostgreSQL)
    ↓ Stores execution record
    ↓
Worker (Render Background Worker)
    ↓ Polls database every 1 second
    ↓ Finds running execution
    ↓ Executes workflow nodes
    ↓ Updates execution status
    ↓
User sees execution complete in frontend
```

## Monitoring

### Check Worker Status

- **Render Dashboard** → Worker Service → Status should be "Running"
- **Logs** → Should show "🚀 Workflow worker started"

### Check Execution Activity

- **Frontend** → Workflows → Executions tab
- **Should see**: Executions completing successfully

### Worker Logs

Look for these messages:
```
🚀 Workflow worker started (poll_interval=1.0s)
📝 Executing node: trigger-node-1
✅ Node trigger-node-1 completed successfully
✅ Execution completed: exec-abc123
```

## Troubleshooting

### Worker Not Running

1. Check Render Dashboard → Worker Service → Status
2. Check Logs for errors
3. Verify environment variables are set

### Executions Not Processing

1. Check worker logs for errors
2. Verify database connection (SUPABASE_DB_URL)
3. Check execution status in database: `SELECT * FROM workflow_executions WHERE status='running'`

### Worker Crashes

1. Check logs for error messages
2. Check resource limits (may need to upgrade plan)
3. Verify all environment variables are set correctly

## Scaling

### Add More Workers

If you have high execution volume:

1. **Option 1**: Upgrade worker plan (more CPU/memory)
2. **Option 2**: Create additional worker service in Render
3. **Option 3**: Increase `WORKFLOW_WORKER_CONCURRENCY` env var

### Multiple Workers

You can run multiple worker services safely:
- Each polls independently
- Database handles concurrency
- No conflicts - workers won't process same execution twice

## Cost

- **Render Background Worker**: ~$7/month (Starter plan)
- **Can upgrade**: For more resources if needed
- **Worth it**: Without worker, workflows don't execute!

## Important Notes

✅ **Worker runs separately** from API server
✅ **Polls database every 1 second**
✅ **Must have same env vars** as backend
✅ **Can run multiple workers** for scaling
✅ **Auto-restarts** if crashes (Render handles this)

## Summary

1. ✅ Worker Dockerfile created
2. ✅ render.yaml updated
3. ⏳ **Push to GitHub** (deploys automatically)
4. ⏳ **Set environment variables** in Render dashboard
5. ⏳ **Verify worker is running** (check logs)
6. ⏳ **Test workflow execution** end-to-end

**Once deployed, your workflows will execute in production!** 🎉
