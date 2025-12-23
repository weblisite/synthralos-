# Workflow Worker - How It Works

## Overview

The **WorkflowWorker** is a background process that continuously polls the database for workflow executions and processes them. It's essential for the workflow execution system to function - without it, workflows will be created but never executed.

## How It Works

### 1. Polling Mechanism

The worker runs in an infinite loop, polling the database every **1 second** (configurable via `poll_interval`):

```python
while self.running:
    try:
        self._process_cycle()  # Process one cycle of work
        time.sleep(self.poll_interval)  # Wait 1 second before next poll
    except KeyboardInterrupt:
        self.stop()
        break
    except Exception as e:
        print(f"❌ Worker error: {e}")
        time.sleep(self.poll_interval)  # Continue even on errors
```

### 2. Processing Cycle

Each cycle (`_process_cycle()`) performs these steps in order:

1. **Check for timeouts** - Marks timed-out executions as failed
2. **Process scheduled executions** - Triggers workflows scheduled via cron
3. **Process retry executions** - Retries failed executions that are due
4. **Process signal-waiting executions** - Resumes executions waiting for signals (e.g., human approval)
5. **Process running executions** - Executes workflow steps for running workflows

### 3. Execution Processing

When processing running executions:

```python
def _process_running_executions(self, session: Session) -> None:
    # Get prioritized executions (up to WORKFLOW_WORKER_CONCURRENCY limit)
    executions = default_prioritization_manager.get_prioritized_executions(
        session,
        status="running",
        limit=settings.WORKFLOW_WORKER_CONCURRENCY,  # Default: 10
    )

    for execution in executions:
        try:
            self._execute_workflow_step(session, execution.id)
        except Exception as e:
            # Mark as failed and schedule retry
            self.workflow_engine.fail_execution(...)
```

### 4. Workflow Step Execution

For each execution, the worker:

1. Gets execution state from database
2. Gets workflow state (nodes and edges from `graph_config`)
3. Determines next node to execute
4. Gets node configuration
5. Calls `workflow_engine.execute_node()` to execute the node
6. Updates execution state with results
7. Determines next nodes and continues

### 5. Node Execution Flow

```
Worker → _execute_workflow_step()
    ↓
Get execution state
    ↓
Get workflow state (nodes from graph_config)
    ↓
Get node config
    ↓
Call workflow_engine.execute_node()
    ↓
Get activity handler for node_type
    ↓
Handler executes node logic
    ↓
Result saved to execution state
    ↓
Worker determines next nodes
    ↓
Repeat until workflow completes
```

## Why Polling?

**Polling** (checking database every second) is used instead of event-driven processing because:

1. **Simplicity** - No need for message queues or event systems
2. **Reliability** - Database is the source of truth
3. **Durability** - Executions persist even if worker restarts
4. **Scalability** - Multiple workers can poll safely (database handles concurrency)

**Trade-off**: Slight delay (up to 1 second) between execution creation and processing, which is acceptable for most workflow use cases.

## Configuration

### Poll Interval

Default: `1.0` seconds

To change:
```python
worker = WorkflowWorker(poll_interval=0.5)  # Poll every 0.5 seconds
```

### Concurrency

Default: `10` concurrent executions per worker (via `WORKFLOW_WORKER_CONCURRENCY` setting)

To scale: Run multiple worker processes/instances

## Starting the Worker

### Development

```bash
# Option 1: Direct Python execution
python -m app.workflows.worker

# Option 2: Using startup script
python backend/scripts/start_worker.py

# Option 3: Python module
cd backend
python -m scripts.start_worker
```

### Production

Run as a separate service/process:

```bash
# Using systemd (Linux)
[Unit]
Description=Workflow Worker
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/backend
ExecStart=/usr/bin/python3 -m scripts.start_worker
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Or use a process manager like:
- **Supervisor** - `supervisord` with worker config
- **PM2** - `pm2 start scripts/start_worker.py`
- **Docker** - Separate container for worker
- **Kubernetes** - Separate deployment for worker

## Worker Lifecycle

### Startup
1. Initialize `WorkflowEngine`, `WorkflowScheduler`, `SignalHandler`
2. Set `running = True`
3. Enter polling loop

### Running
- Continuously polls database
- Processes executions
- Handles errors gracefully (continues on errors)
- Logs activity to console

### Shutdown
- `Ctrl+C` sends `KeyboardInterrupt`
- Sets `running = False`
- Exits loop gracefully
- Prints confirmation message

## Monitoring

The worker prints status messages:

```
🚀 Workflow worker started (poll_interval=1.0s)
📅 Triggered 2 scheduled executions
🔄 Retrying execution: exec-abc123
📨 Processed signal for execution: exec-xyz789
✅ Execution completed: exec-def456
⚠️  Error processing execution abc123: Node not found
```

## Error Handling

The worker is designed to be resilient:

- **Node execution errors**: Marked as failed, retry scheduled
- **Database errors**: Logged, worker continues
- **Handler errors**: Caught, execution marked as failed
- **Worker errors**: Logged, worker continues polling

## Performance Considerations

### Database Load

- Polls every 1 second
- Queries for running executions (indexed on `status`)
- Updates execution state after each node
- **Impact**: Minimal - queries are simple and indexed

### Memory Usage

- Keeps execution state in memory during processing
- Releases after each cycle
- **Impact**: Low - state is small per execution

### CPU Usage

- Most time spent sleeping (1 second between polls)
- Active processing only when executions exist
- **Impact**: Very low when idle, scales with execution count

## Scaling

To handle more executions:

1. **Increase concurrency**: Set `WORKFLOW_WORKER_CONCURRENCY` higher
2. **Run multiple workers**: Start multiple worker processes
3. **Reduce poll interval**: Poll more frequently (e.g., 0.5s)
4. **Optimize handlers**: Make node handlers faster

## Troubleshooting

### Worker Not Processing Executions

1. **Check worker is running**: Look for "🚀 Workflow worker started" message
2. **Check database connection**: Worker needs database access
3. **Check execution status**: Executions must have `status="running"`
4. **Check logs**: Look for error messages

### Executions Stuck

1. **Check worker logs**: See if errors occurred
2. **Check execution state**: Query database for execution status
3. **Check node config**: Verify nodes have valid configurations
4. **Check handlers**: Ensure activity handlers exist for node types

### High CPU/Memory

1. **Reduce concurrency**: Lower `WORKFLOW_WORKER_CONCURRENCY`
2. **Increase poll interval**: Poll less frequently
3. **Check for infinite loops**: Review node handlers
4. **Monitor execution count**: Too many concurrent executions

## Example: Complete Flow

```
1. User clicks "Run" in frontend
   ↓
2. API creates execution (status="running")
   ↓
3. Worker polls database (every 1 second)
   ↓
4. Worker finds execution with status="running"
   ↓
5. Worker gets workflow state (nodes from graph_config)
   ↓
6. Worker executes first node (trigger)
   ↓
7. Handler executes node logic
   ↓
8. Result saved to execution state
   ↓
9. Worker determines next node
   ↓
10. Worker executes next node
   ↓
11. Repeat until workflow completes
   ↓
12. Execution marked as "completed"
```

## Summary

- **Worker polls database every 1 second**
- **Processes running executions sequentially**
- **Executes nodes via activity handlers**
- **Updates execution state after each step**
- **Continues until workflow completes**
- **Must be running for workflows to execute**

The worker is the **heart** of the workflow execution system - without it, workflows are created but never run!
