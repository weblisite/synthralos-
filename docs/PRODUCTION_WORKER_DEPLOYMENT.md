# Production Worker Deployment Guide

## Overview

In production, the **WorkflowWorker** must run as a **separate service** from your API server. This guide covers deployment strategies for various platforms.

## Why Separate Service?

- **API Server**: Handles HTTP requests (stateless, can scale horizontally)
- **Worker**: Processes workflow executions (stateful polling, needs to run continuously)

**They serve different purposes and should be deployed separately.**

## Deployment Options

### Option 1: Render (Current Platform) ⭐ RECOMMENDED

Since you're using Render, this is the easiest option.

#### Step 1: Create Worker Service

1. Go to **Render Dashboard** → **New** → **Background Worker**
2. Configure:
   - **Name**: `synthralos-workflow-worker`
   - **Environment**: `Docker`
   - **Dockerfile Path**: `./backend/Dockerfile.worker` (we'll create this)
   - **Docker Context**: `./backend`
   - **Start Command**: `python -m app.workflows.worker`

#### Step 2: Environment Variables

Copy all environment variables from your backend service:
- `SUPABASE_DB_URL` (or `POSTGRES_*` variables)
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `ENVIRONMENT=production`
- `WORKFLOW_WORKER_CONCURRENCY=10`
- All other backend env vars

#### Step 3: Update render.yaml

Add worker service to your `render.yaml`:

```yaml
services:
  # ... existing backend and frontend services ...

  - type: worker
    name: synthralos-workflow-worker
    env: docker
    dockerfilePath: ./backend/Dockerfile.worker
    dockerContext: ./backend
    dockerCommand: python -m app.workflows.worker
    envVars:
      - key: ENVIRONMENT
        value: production
      - key: SUPABASE_DB_URL
        fromDatabase:
          name: synthralos-db
          property: connectionString
      # Copy other env vars from backend service
```

#### Step 4: Create Worker Dockerfile

Create `backend/Dockerfile.worker`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run worker
CMD ["python", "-m", "app.workflows.worker"]
```

#### Step 5: Deploy

- If using Blueprint: Push changes, Render will auto-deploy
- If manual: Create worker service in dashboard

**Cost**: Background workers on Render start at ~$7/month (Starter plan)

---

### Option 2: Same Server, Separate Process

If you're on a VPS or single server:

#### Using Supervisor (Recommended)

1. **Install Supervisor**:
```bash
sudo apt-get install supervisor
```

2. **Create config** `/etc/supervisor/conf.d/workflow-worker.conf`:
```ini
[program:workflow-worker]
command=/usr/bin/python3 -m app.workflows.worker
directory=/path/to/backend
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/workflow-worker.err.log
stdout_logfile=/var/log/workflow-worker.out.log
environment=ENVIRONMENT="production"
```

3. **Start**:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start workflow-worker
```

4. **Monitor**:
```bash
sudo supervisorctl status workflow-worker
sudo supervisorctl tail -f workflow-worker
```

#### Using systemd

1. **Create service** `/etc/systemd/system/workflow-worker.service`:
```ini
[Unit]
Description=Workflow Worker
After=network.target postgresql.service

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/backend
Environment="ENVIRONMENT=production"
ExecStart=/usr/bin/python3 -m app.workflows.worker
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

2. **Enable and start**:
```bash
sudo systemctl enable workflow-worker
sudo systemctl start workflow-worker
sudo systemctl status workflow-worker
```

---

### Option 3: Docker Compose

If using Docker Compose:

```yaml
version: '3.8'

services:
  api:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
    # ... other config

  worker:
    build:
      context: ./backend
      dockerfile: Dockerfile.worker
    environment:
      - ENVIRONMENT=production
      - SUPABASE_DB_URL=${SUPABASE_DB_URL}
      # ... other env vars (same as api)
    depends_on:
      - db
    restart: unless-stopped
    # No ports needed - worker doesn't serve HTTP

  db:
    # ... database config
```

Run:
```bash
docker-compose up -d worker
```

---

### Option 4: Kubernetes

Create `worker-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: workflow-worker
spec:
  replicas: 2  # Run 2 workers for redundancy
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
        image: your-registry/synthralos-worker:latest
        command: ["python", "-m", "app.workflows.worker"]
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: SUPABASE_DB_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

Deploy:
```bash
kubectl apply -f worker-deployment.yaml
kubectl get pods -l app=workflow-worker
```

---

### Option 5: Cloud Functions / Serverless

**Not Recommended** - Workers need to run continuously, serverless functions have execution time limits.

However, if you must:
- **AWS Lambda**: Use scheduled CloudWatch Events (runs every minute)
- **Google Cloud Functions**: Use Cloud Scheduler (runs every minute)
- **Azure Functions**: Use Timer Trigger

**Limitation**: Maximum execution time limits (15 minutes on most platforms)

---

## Recommended: Render Background Worker

For your current Render setup, here's the complete configuration:

### 1. Create `backend/Dockerfile.worker`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run worker
CMD ["python", "-m", "app.workflows.worker"]
```

### 2. Update `render.yaml`

Add to your existing `render.yaml`:

```yaml
services:
  # ... your existing backend service ...

  - type: worker
    name: synthralos-workflow-worker
    env: docker
    dockerfilePath: ./backend/Dockerfile.worker
    dockerContext: ./backend
    plan: starter  # $7/month - can upgrade for more resources
    envVars:
      - key: ENVIRONMENT
        value: production
      - key: SUPABASE_DB_URL
        fromDatabase:
          name: synthralos-db
          property: connectionString
      # Copy all other env vars from backend service
      - key: SUPABASE_URL
        sync: false  # Set manually in dashboard
      - key: SUPABASE_ANON_KEY
        sync: false  # Set manually in dashboard
      - key: WORKFLOW_WORKER_CONCURRENCY
        value: 10
```

### 3. Deploy

1. **Push changes** to GitHub
2. **Render will auto-deploy** the worker service
3. **Set environment variables** in Render dashboard (same as backend)
4. **Verify** worker is running (check logs)

### 4. Monitor

- **Logs**: Render Dashboard → Worker Service → Logs
- **Status**: Should show "Running"
- **Activity**: Look for "🚀 Workflow worker started" message

---

## Scaling Workers

### Multiple Workers

You can run **multiple worker instances** safely:

- **Render**: Increase `replicas` or create multiple worker services
- **Kubernetes**: Increase `replicas` in deployment
- **Docker**: Run multiple containers: `docker-compose up -d --scale worker=3`

**Why it's safe**: Database handles concurrency, workers won't process the same execution twice.

### Load Distribution

Workers automatically distribute load:
- Each worker polls independently
- Database queries return different executions
- No coordination needed

### Recommended Scaling

- **Small**: 1 worker (handles ~10 concurrent executions)
- **Medium**: 2-3 workers (handles ~20-30 concurrent executions)
- **Large**: 5+ workers (handles 50+ concurrent executions)

---

## Monitoring Production Workers

### Health Checks

Workers don't serve HTTP, so health checks are different:

1. **Database Query**: Check if worker is processing executions
2. **Log Monitoring**: Ensure logs show activity
3. **Execution Status**: Monitor execution completion rates

### Metrics to Monitor

- **Execution Queue**: Number of `status='running'` executions
- **Processing Rate**: Executions completed per minute
- **Error Rate**: Failed executions percentage
- **Worker Uptime**: Worker process uptime
- **Database Connections**: Active connections from workers

### Alerting

Set up alerts for:
- Worker process down
- Execution queue growing (>100 running executions)
- High error rate (>10% failures)
- Worker memory/CPU spikes

---

## Production Checklist

- [ ] Worker service created and running
- [ ] Environment variables configured (same as backend)
- [ ] Worker logs showing activity
- [ ] Test workflow execution end-to-end
- [ ] Monitor execution completion rates
- [ ] Set up alerts for worker failures
- [ ] Document worker restart procedures
- [ ] Plan for scaling (multiple workers)

---

## Troubleshooting Production

### Worker Not Processing

1. **Check worker is running**: Render Dashboard → Logs
2. **Check database connection**: Worker needs DB access
3. **Check environment variables**: Must match backend
4. **Check logs**: Look for error messages

### High Execution Queue

1. **Scale workers**: Add more worker instances
2. **Increase concurrency**: Set `WORKFLOW_WORKER_CONCURRENCY` higher
3. **Check for stuck executions**: Query database for long-running executions
4. **Optimize handlers**: Make node handlers faster

### Worker Crashes

1. **Check logs**: Find error that caused crash
2. **Check resources**: Worker may be out of memory
3. **Check database**: Connection issues?
4. **Auto-restart**: Ensure restart policy is enabled

---

## Cost Considerations

### Render

- **Background Worker**: ~$7/month (Starter plan)
- **Can upgrade**: For more CPU/memory if needed
- **Scaling**: Each additional worker = additional cost

### Self-Hosted

- **VPS**: $5-20/month (DigitalOcean, Linode, etc.)
- **Can run multiple workers** on same server
- **More control**, but need to manage yourself

### Kubernetes

- **Resource-based**: Pay for CPU/memory used
- **Can scale**: Automatically based on load
- **More complex**: Requires Kubernetes expertise

---

## Summary

**For Render (Your Current Platform)**:

1. ✅ Create `backend/Dockerfile.worker`
2. ✅ Add worker service to `render.yaml`
3. ✅ Deploy (auto-deploys on push)
4. ✅ Set environment variables
5. ✅ Monitor logs and execution activity

**The worker is critical** - without it, workflows won't execute in production!
