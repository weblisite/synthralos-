# Production Worker - How It Works for Your Users

## The Problem Your Users Face

When a user clicks "Run" on a workflow in your production platform:

```
User clicks "Run" button
    ↓
Frontend sends request to API
    ↓
API creates execution record in database
    ↓
❌ WITHOUT WORKER: Execution sits in database, never runs
    ↓
User sees execution stuck at "running" status forever
```

**Without the worker, workflows don't execute!**

## The Solution: Background Worker

The **WorkflowWorker** is a separate service that runs continuously in production:

```
User clicks "Run" button
    ↓
API creates execution (status="running")
    ↓
Worker polls database every 1 second
    ↓
Worker finds running execution
    ↓
Worker executes workflow nodes step-by-step
    ↓
Worker updates execution status
    ↓
User sees execution complete successfully ✅
```

## How It Works in Production (Render)

### Architecture

```
┌─────────────────────┐
│   Render Platform   │
│                     │
│  ┌───────────────┐  │
│  │  Web Service  │  │  ← Your API Server
│  │  (Backend)    │  │     Handles HTTP requests
│  └───────┬───────┘  │
│          │           │
│          │ Creates   │
│          │ execution │
│          ▼           │
│  ┌───────────────┐  │
│  │   Database    │  │  ← Supabase PostgreSQL
│  │  (Supabase)   │  │     Stores executions
│  └───────┬───────┘  │
│          │           │
│          │ Polls     │
│          │ every 1s  │
│          ▼           │
│  ┌───────────────┐  │
│  │ Background    │  │  ← Worker Service
│  │ Worker        │  │     Processes executions
│  └───────────────┘  │
└─────────────────────┘
```

### Polling Mechanism

The worker uses **polling** (checking database every second):

```python
while True:
    # 1. Query database for running executions
    executions = database.query("SELECT * FROM workflow_executions WHERE status='running'")

    # 2. Process each execution
    for execution in executions:
        execute_workflow(execution)

    # 3. Wait 1 second
    sleep(1.0)

    # 4. Repeat forever
```

**Why polling?**
- ✅ Simple - no message queues needed
- ✅ Reliable - database is source of truth
- ✅ Durable - executions survive worker restarts
- ✅ Scalable - multiple workers can poll safely

**Trade-off**: Up to 1 second delay (acceptable for workflows)

### What Happens When User Runs Workflow

1. **User Action**: Clicks "Run" in frontend
2. **API Call**: `POST /api/v1/workflows/{id}/run`
3. **Execution Created**: Database record with `status="running"`
4. **Worker Polls**: Checks database (happens every second)
5. **Worker Finds**: Discovers new running execution
6. **Worker Executes**: Runs workflow nodes step-by-step
7. **Status Updates**: Execution status updated after each node
8. **Completion**: Execution marked as "completed"
9. **User Sees**: Execution appears in Executions tab with results

### Processing Flow

```
Worker Cycle (every 1 second):
    ↓
1. Check for timeouts
    ↓
2. Process scheduled executions (cron)
    ↓
3. Process retry executions (failed → retry)
    ↓
4. Process signal-waiting (human approval)
    ↓
5. Process running executions ← Main work happens here
    ↓
   For each running execution:
   - Get workflow state (nodes from graph_config)
   - Determine next node to execute
   - Execute node via activity handler
   - Save result to execution state
   - Determine next nodes
   - Continue until workflow completes
    ↓
Wait 1 second, repeat
```

## Production Deployment (Render)

### Current Setup

You have:
- ✅ Backend API service (handles HTTP requests)
- ✅ Frontend service (serves UI)
- ✅ Database (Supabase PostgreSQL)
- ❌ **Missing**: Worker service (needed for execution)

### Adding Worker Service

**Option 1: Using render.yaml (Recommended)**

The `render.yaml` file has been updated to include the worker service. When you push to GitHub, Render will automatically create it.

**Option 2: Manual Creation**

1. Go to Render Dashboard → New → Background Worker
2. Configure:
   - Name: `synthralos-workflow-worker`
   - Dockerfile: `./backend/Dockerfile.worker`
   - Start Command: `python -m app.workflows.worker`
3. Copy all environment variables from backend service
4. Deploy

### Environment Variables

The worker needs **the same environment variables** as your backend:

**Required:**
- `SUPABASE_DB_URL` - Database connection
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_ANON_KEY` - Supabase API key
- `ENVIRONMENT=production`
- `SECRET_KEY` - Same as backend

**Optional:**
- `WORKFLOW_WORKER_CONCURRENCY=10` - How many executions to process concurrently
- All other backend env vars (NANGO_SECRET_KEY, etc.)

### Cost

- **Render Background Worker**: ~$7/month (Starter plan)
- **Can upgrade**: To Standard ($25/month) for more CPU/memory
- **Worth it**: Without worker, workflows don't execute!

## Monitoring Production Workers

### Check Worker Status

**Render Dashboard:**
- Go to Worker Service → Status
- Should show "Running"
- Check Logs for activity

### Worker Logs

Look for:
```
🚀 Workflow worker started (poll_interval=1.0s)
📝 Executing node: trigger-node-1
✅ Node trigger-node-1 completed successfully
✅ Execution completed: exec-abc123
```

### User-Facing Monitoring

Users can see execution status in:
- **Executions Tab**: Shows all executions with status
- **Execution Panel**: Live view of running execution
- **Execution Timeline**: Step-by-step execution history

## Scaling for Production

### Single Worker

- **Handles**: ~10 concurrent executions (default)
- **Good for**: Small to medium usage
- **Cost**: $7/month

### Multiple Workers

You can run **multiple worker instances**:

- **Render**: Create additional worker services
- **Kubernetes**: Increase replicas
- **Docker**: Run multiple containers

**Why it's safe:**
- Each worker polls independently
- Database handles concurrency
- Workers won't process same execution twice

### Scaling Strategy

- **Low usage**: 1 worker (10 concurrent executions)
- **Medium usage**: 2-3 workers (20-30 concurrent executions)
- **High usage**: 5+ workers (50+ concurrent executions)

## Reliability

### Auto-Restart

- **Render**: Automatically restarts worker if it crashes
- **Supervisor/systemd**: Configured with `restart=always`
- **Kubernetes**: Pod restart policy

### Execution Persistence

- **Executions stored in database**: Survive worker restarts
- **State persisted**: After each node execution
- **No data loss**: If worker crashes, executions resume when worker restarts

### Error Handling

- **Node failures**: Marked as failed, retry scheduled
- **Worker errors**: Logged, worker continues
- **Database errors**: Logged, worker retries

## User Experience

### Without Worker

```
User clicks "Run"
    ↓
Execution created ✅
    ↓
Execution stuck at "running" ❌
    ↓
User confused - workflow never completes
```

### With Worker

```
User clicks "Run"
    ↓
Execution created ✅
    ↓
Worker processes execution ✅
    ↓
Execution completes ✅
    ↓
User sees results ✅
```

## Summary

**For Your Production Platform:**

1. ✅ **Worker is separate service** from API
2. ✅ **Polls database every 1 second** for executions
3. ✅ **Processes workflows step-by-step**
4. ✅ **Updates execution status** after each step
5. ✅ **Users see executions complete** in real-time

**Deployment Steps:**

1. ✅ Worker Dockerfile created (`backend/Dockerfile.worker`)
2. ✅ render.yaml updated (includes worker service)
3. ⏳ **Push to GitHub** (auto-deploys on Render)
4. ⏳ **Set environment variables** in Render dashboard
5. ⏳ **Verify worker running** (check logs)
6. ⏳ **Test workflow execution** end-to-end

**Once deployed, your users' workflows will execute in production!** 🎉
