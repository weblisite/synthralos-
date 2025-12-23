# Local Workflow Worker Setup

This guide explains how to run the workflow worker locally for development and testing.

## ⚠️ Important: Development vs Production

- **Local Development**: Use this guide to run the worker manually for testing
- **Production (Render)**: The worker runs automatically as a Render Background Worker service
  - Defined in `render.yaml` as `synthralos-workflow-worker`
  - Deployed alongside backend and frontend via Render Blueprint
  - Uses the same codebase but runs in Render's infrastructure

**Note**: When making changes to worker code (`backend/app/workflows/worker.py`), those changes will apply to both local development and production. Only the deployment/running mechanism differs.

## Overview

The workflow worker is a background process that:
- Polls the database every 1 second for workflow executions
- Processes running executions
- Handles retries, signals, and scheduled executions
- Executes workflow nodes via activity handlers

## Prerequisites

1. Backend server must be running (the worker connects to the same database)
2. Database must be configured (same environment variables as backend)
3. All backend dependencies must be installed

## Running the Worker

### Option 1: Using the Startup Script (Recommended)

```bash
cd backend
source .venv/bin/activate  # or activate your virtual environment
python -m scripts.start_worker
```

Or directly:

```bash
cd backend
source .venv/bin/activate
python scripts/start_worker.py
```

### Option 2: Using Python Module

```bash
cd backend
source .venv/bin/activate
python -m app.workflows.worker
```

### Option 3: Direct Python Execution

```bash
cd backend
source .venv/bin/activate
python -c "from app.workflows.worker import WorkflowWorker; worker = WorkflowWorker(poll_interval=1.0); worker.start()"
```

## Environment Variables

The worker uses the same database configuration as the backend. Make sure these are set:

```bash
# Supabase Database (preferred)
export SUPABASE_DB_URL="postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres"
# OR
export SUPABASE_URL="https://[PROJECT_REF].supabase.co"
export SUPABASE_DB_PASSWORD="[PASSWORD]"

# Legacy PostgreSQL (if not using Supabase)
export POSTGRES_HOST="localhost"
export POSTGRES_PORT="5432"
export POSTGRES_USER="postgres"
export POSTGRES_PASSWORD="password"
export POSTGRES_DB="synthralos"
```

## Running Both Backend and Worker

### Terminal 1: Backend Server
```bash
cd backend
source .venv/bin/activate
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Terminal 2: Workflow Worker
```bash
cd backend
source .venv/bin/activate
python -m scripts.start_worker
```

## Development Workflow

1. **Start the backend server** in one terminal
2. **Start the workflow worker** in another terminal
3. **Create/run workflows** via the frontend or API
4. **Monitor worker logs** to see execution progress

## Worker Output

The worker will display:
- Startup information
- Polling status
- Execution processing logs
- Error messages (if any)
- Statistics (executions processed, errors, etc.)

Example output:
```
============================================================
🚀 Starting Workflow Worker
============================================================

The worker will:
  • Poll database every 1 second for workflow executions
  • Process running executions
  • Handle retries, signals, and scheduled executions
  • Execute workflow nodes via activity handlers

Press Ctrl+C to stop the worker
============================================================

🚀 Workflow worker started (poll_interval=1.0s)
✅ Worker running...
```

## Stopping the Worker

Press `Ctrl+C` in the terminal where the worker is running. The worker will gracefully shut down.

## Troubleshooting

### Worker not processing executions

1. **Check database connection**: Ensure database environment variables are set correctly
2. **Check backend is running**: The worker needs the database to be accessible
3. **Check execution status**: Verify executions are in "running" or "pending" status
4. **Check logs**: Look for error messages in the worker output

### Database connection errors

```bash
# Test database connection
cd backend
source .venv/bin/activate
python -c "from app.core.db import engine; from sqlmodel import text; with engine.connect() as conn: result = conn.execute(text('SELECT 1')); print('✅ Database connected')"
```

### Worker not finding executions

- Ensure executions are created with status "running" or "pending"
- Check that `workflow_id` matches an existing workflow
- Verify the database has the correct schema (run migrations if needed)

## Production vs Development

### Development (Local)
- Run worker manually in a terminal using `python -m scripts.start_worker`
- Connects to your local database (same as backend)
- Useful for testing workflow execution locally
- Stop/start as needed during development

### Production (Render)
- Worker runs automatically as a Render Background Worker service
- Defined in `render.yaml` as `synthralos-workflow-worker`
- Deployed via Render Blueprint alongside backend and frontend
- Uses production database (Supabase)
- Runs continuously in Render's infrastructure
- Environment variables configured in Render dashboard

**Important**: The worker code (`backend/app/workflows/worker.py`) is shared between both environments. Changes to the worker code will affect both local development and production after deployment.

## Integration with Frontend

When testing locally:
1. Frontend → Backend API → Creates workflow execution
2. Backend → Database → Stores execution with status "running"
3. Worker → Database → Polls and finds execution
4. Worker → Processes execution → Updates status
5. Frontend → Backend API → Polls for execution updates

All components work together seamlessly in local development.
