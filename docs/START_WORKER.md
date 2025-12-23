# How to Start the Workflow Worker

## Quick Start

### Development (Local)

```bash
# Navigate to backend directory
cd backend

# Start the worker
python -m app.workflows.worker
```

Or use the startup script:

```bash
python backend/scripts/start_worker.py
```

### Production

The worker should run as a **separate process** from the API server.

#### Option 1: Separate Terminal/Process

```bash
# Terminal 1: Start API server
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Terminal 2: Start worker
cd backend
python -m app.workflows.worker
```

#### Option 2: Background Process

```bash
# Start worker in background
nohup python -m app.workflows.worker > worker.log 2>&1 &

# Check if running
ps aux | grep worker

# View logs
tail -f worker.log
```

#### Option 3: Using PM2

```bash
# Install PM2
npm install -g pm2

# Start worker
pm2 start "python -m app.workflows.worker" --name workflow-worker

# Monitor
pm2 status
pm2 logs workflow-worker
```

#### Option 4: Using Supervisor

Create `/etc/supervisor/conf.d/workflow-worker.conf`:

```ini
[program:workflow-worker]
command=/usr/bin/python3 -m app.workflows.worker
directory=/path/to/backend
user=your-user
autostart=true
autorestart=true
stderr_logfile=/var/log/workflow-worker.err.log
stdout_logfile=/var/log/workflow-worker.out.log
```

Then:

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start workflow-worker
```

#### Option 5: Docker

Create `Dockerfile.worker`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "app.workflows.worker"]
```

Build and run:

```bash
docker build -f Dockerfile.worker -t workflow-worker .
docker run -d --name worker workflow-worker
```

#### Option 6: Kubernetes

Create `worker-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: workflow-worker
spec:
  replicas: 1
  selector:
    matchLabels:
      app: workflow-worker
  template:
    metadata:
      labels:
        app: workflow-worker
    spec:
      containers:
      - name: worker
        image: your-registry/workflow-worker:latest
        command: ["python", "-m", "app.workflows.worker"]
        env:
        - name: SUPABASE_DB_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
```

## Verification

### Check Worker is Running

Look for this output:

```
🚀 Workflow worker started (poll_interval=1.0s)
```

### Test Execution

1. Create a workflow in the frontend
2. Click "Run"
3. Check worker logs - you should see execution processing messages

### Monitor Activity

The worker prints activity:

```
📅 Triggered 2 scheduled executions
🔄 Retrying execution: exec-abc123
✅ Execution completed: exec-def456
```

## Stopping the Worker

### Development

Press `Ctrl+C` in the terminal where worker is running

### Background Process

```bash
# Find process
ps aux | grep worker

# Kill process
kill <PID>

# Or if using PM2
pm2 stop workflow-worker
```

## Troubleshooting

### Worker Not Starting

1. **Check Python path**: Ensure you're in the backend directory
2. **Check dependencies**: Run `pip install -r requirements.txt`
3. **Check database**: Ensure database connection is configured
4. **Check imports**: Run `python -c "from app.workflows.worker import WorkflowWorker"`

### Worker Not Processing Executions

1. **Check worker is running**: Look for startup message
2. **Check database connection**: Worker needs database access
3. **Check execution status**: Executions must have `status="running"`
4. **Check logs**: Look for error messages

### High Resource Usage

1. **Reduce concurrency**: Set `WORKFLOW_WORKER_CONCURRENCY` lower
2. **Increase poll interval**: Change `poll_interval` to 2.0 or higher
3. **Check for errors**: Review logs for stuck executions

## Important Notes

- **Worker must run separately** from API server
- **Worker polls database every 1 second** (configurable)
- **Multiple workers can run** for scaling (database handles concurrency)
- **Worker is stateless** - can restart without losing executions
- **Executions persist** in database even if worker stops
