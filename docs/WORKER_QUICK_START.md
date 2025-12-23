# Workflow Worker - Quick Start Guide

## What is the Workflow Worker?

The **WorkflowWorker** is a background process that:
- **Polls the database every 1 second** for workflow executions
- **Processes running executions** by executing workflow nodes
- **Handles retries, signals, and scheduled executions**
- **Must be running** for workflows to execute

## Why Do We Need It?

When you click "Run" in the frontend:
1. ✅ API creates an execution record in the database
2. ❌ **Without worker**: Execution stays in database, never runs
3. ✅ **With worker**: Worker picks it up and executes it

**The worker is the execution engine** - it's what actually runs your workflows!

## How It Works (Simple Explanation)

```
┌─────────────────┐
│   Frontend      │
│  Click "Run"    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   API Server    │
│ Creates exec    │
│ status="running"│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Database     │
│  Execution      │
│  Record Saved   │
└────────┬────────┘
         │
         │ (Worker polls every 1 second)
         │
         ▼
┌─────────────────┐
│  Worker Process │
│  Finds exec     │
│  Executes nodes │
│  Updates state  │
└─────────────────┘
```

## Starting the Worker

### Development (Easiest)

Open a **new terminal** and run:

```bash
cd backend
python3 -m app.workflows.worker
```

You should see:
```
🚀 Workflow worker started (poll_interval=1.0s)
```

**Keep this terminal open** - the worker runs continuously.

### Using the Startup Script

```bash
python3 backend/scripts/start_worker.py
```

## Testing End-to-End

### Step 1: Start the Worker

```bash
# Terminal 1: Start API server (if not already running)
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Terminal 2: Start worker
cd backend
python3 -m app.workflows.worker
```

### Step 2: Create and Run a Workflow

1. Open frontend: `http://localhost:5173/workflows`
2. Create a simple workflow:
   - Add a **Trigger** node
   - Add a **Code** node (connect from trigger)
   - Configure Code node with: `print("Hello from workflow!")`
3. Click **Save Workflow**
4. Click **Run**

### Step 3: Watch the Worker

In the worker terminal, you should see:
```
✅ Execution started: exec-abc123
📝 Executing node: trigger-node-1
✅ Node trigger-node-1 completed successfully
📝 Executing node: code-node-2
✅ Node code-node-2 completed successfully
✅ Execution completed: exec-abc123
```

### Step 4: Check Execution History

1. Go to **Executions** tab in workflows page
2. You should see your execution with status "completed"

## Understanding the Polling Mechanism

### Why Polling?

The worker uses **polling** (checking database every second) instead of events:

✅ **Pros:**
- Simple - no message queues needed
- Reliable - database is source of truth
- Durable - executions survive worker restarts
- Scalable - multiple workers can poll safely

❌ **Cons:**
- Slight delay (up to 1 second) between creation and processing
- Constant database queries (minimal impact)

### How Polling Works

```python
while running:
    # 1. Check database for work
    executions = get_running_executions()

    # 2. Process each execution
    for execution in executions:
        execute_workflow_step(execution)

    # 3. Wait 1 second
    sleep(1.0)

    # 4. Repeat
```

### What Gets Polled?

Each cycle checks for:
1. **Running executions** - Workflows currently executing
2. **Failed executions** - Due for retry
3. **Signal-waiting** - Waiting for human approval/signals
4. **Scheduled** - Cron-triggered workflows due to run
5. **Timeouts** - Executions that exceeded time limits

## Configuration

### Poll Interval

Default: `1.0` seconds

To change:
```python
worker = WorkflowWorker(poll_interval=0.5)  # Poll every 0.5 seconds
```

### Concurrency

Default: `10` executions processed concurrently

Set via environment variable:
```bash
export WORKFLOW_WORKER_CONCURRENCY=20
```

## Production Deployment

### Option 1: Separate Process

Run worker as separate process from API:

```bash
# API server
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Worker (separate terminal/process)
python3 -m app.workflows.worker
```

### Option 2: Background Service

```bash
# Start in background
nohup python3 -m app.workflows.worker > worker.log 2>&1 &

# Check status
ps aux | grep worker

# View logs
tail -f worker.log
```

### Option 3: Docker

```dockerfile
# Dockerfile.worker
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "-m", "app.workflows.worker"]
```

```bash
docker build -f Dockerfile.worker -t worker .
docker run -d --name workflow-worker worker
```

### Option 4: Systemd Service

Create `/etc/systemd/system/workflow-worker.service`:

```ini
[Unit]
Description=Workflow Worker
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/backend
ExecStart=/usr/bin/python3 -m app.workflows.worker
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable workflow-worker
sudo systemctl start workflow-worker
sudo systemctl status workflow-worker
```

## Monitoring

### Check Worker Status

Look for startup message:
```
🚀 Workflow worker started (poll_interval=1.0s)
```

### Monitor Activity

Worker prints activity:
```
📅 Triggered 2 scheduled executions
🔄 Retrying execution: exec-abc123
📝 Executing node: node-1
✅ Node node-1 completed successfully
✅ Execution completed: exec-def456
```

### Check Database

Query running executions:
```sql
SELECT * FROM workflow_executions
WHERE status = 'running'
ORDER BY started_at DESC;
```

## Troubleshooting

### Worker Not Starting

1. **Check Python**: `python3 --version`
2. **Check dependencies**: `pip install -r requirements.txt`
3. **Check database**: Ensure `SUPABASE_DB_URL` is set
4. **Check imports**: `python3 -c "from app.workflows.worker import WorkflowWorker"`

### Worker Not Processing

1. **Is worker running?** Look for startup message
2. **Check database connection**: Worker needs DB access
3. **Check execution status**: Must be `status='running'`
4. **Check logs**: Look for error messages

### Executions Stuck

1. **Check worker logs**: See if errors occurred
2. **Check execution state**: Query database
3. **Check node config**: Verify nodes have valid configs
4. **Restart worker**: Sometimes helps clear stuck state

## Key Points

✅ **Worker must run separately** from API server
✅ **Polls database every 1 second** (configurable)
✅ **Multiple workers can run** for scaling
✅ **Stateless** - can restart without losing executions
✅ **Executions persist** in database

## Summary

- **Start worker**: `python3 -m app.workflows.worker`
- **Keep running**: Worker runs continuously
- **Watch logs**: See execution activity
- **Check executions**: View in frontend Executions tab

**Without the worker, workflows won't execute!**
