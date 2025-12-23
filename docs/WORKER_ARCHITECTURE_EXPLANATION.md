# Workflow Worker Architecture Explanation

## Overview

Your platform uses a **distributed architecture** with three separate services that communicate through **Supabase PostgreSQL** as the shared database:

1. **Frontend** (React/Vite) - User interface
2. **Backend** (FastAPI) - API server
3. **Worker** (Background Process) - Workflow execution engine

All three services connect to the **same Supabase database**, which acts as the **shared state/communication layer**.

---

## Architecture Diagram

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│                 │         │                 │         │                 │
│    FRONTEND     │────────▶│     BACKEND     │────────▶│   SUPABASE DB   │
│   (React/Vite)  │  HTTP   │    (FastAPI)    │  SQL    │  (PostgreSQL)   │
│                 │         │                 │         │                 │
└─────────────────┘         └─────────────────┘         └─────────────────┘
                                                                    ▲
                                                                    │
                                                                    │ SQL
                                                                    │
                                                          ┌─────────┴─────────┐
                                                          │                   │
                                                          │      WORKER       │
                                                          │  (Background)     │
                                                          │                   │
                                                          └───────────────────┘
```

---

## How It Works

### 1. **Frontend → Backend Communication**

**Flow:**
```
User Action (Frontend)
    ↓
HTTP Request (REST API)
    ↓
Backend API Endpoint
    ↓
Database Query/Update (Supabase)
    ↓
Response to Frontend
```

**Example: Creating a Workflow**
1. User clicks "Save Workflow" in the frontend
2. Frontend sends `POST /api/v1/workflows/` to backend
3. Backend creates a `Workflow` record in Supabase database
4. Backend returns the created workflow to frontend
5. Frontend displays success message

**Example: Running a Workflow**
1. User clicks "Run" button in the frontend
2. Frontend sends `POST /api/v1/workflows/{id}/run` to backend
3. Backend creates a `WorkflowExecution` record with status `"pending"` or `"running"` in Supabase database
4. Backend returns execution ID to frontend
5. Frontend shows "Workflow started" message

---

### 2. **Worker → Database Communication**

**Flow:**
```
Worker Polls Database (every 1 second)
    ↓
Finds WorkflowExecutions with status="running" or "pending"
    ↓
Processes Each Execution
    ↓
Updates Execution Status in Database
    ↓
Executes Workflow Nodes
    ↓
Updates Node Results in Database
```

**Example: Worker Processing a Workflow**
1. Worker polls database: `SELECT * FROM workflow_executions WHERE status = 'running'`
2. Finds execution with ID `abc-123`
3. Worker loads workflow definition from `workflows` table
4. Worker executes each node sequentially:
   - Updates `current_node_id` in execution record
   - Executes node (e.g., HTTP request, AI prompt, etc.)
   - Stores node result in execution state
   - Updates execution status
5. When workflow completes, sets status to `"completed"` or `"failed"`

---

### 3. **Backend → Worker Communication (via Database)**

**The backend and worker NEVER directly communicate.** They communicate through the database:

**Backend Creates Work:**
```python
# Backend API endpoint
@router.post("/{workflow_id}/run")
def run_workflow(...):
    # Create execution record in database
    execution = WorkflowExecution(
        workflow_id=workflow_id,
        status="running",  # Worker will pick this up
        ...
    )
    session.add(execution)
    session.commit()
    # Backend returns immediately - doesn't wait for execution
    return {"execution_id": execution.id}
```

**Worker Picks Up Work:**
```python
# Worker polling loop
def _process_cycle(self):
    with Session(engine) as session:
        # Find executions that need processing
        query = select(WorkflowExecution).where(
            WorkflowExecution.status == "running"
        )
        executions = session.exec(query).all()

        # Process each execution
        for execution in executions:
            self.workflow_engine.execute_workflow(session, execution.id)
```

---

## Database Tables Used

### `workflows` Table
- Stores workflow definitions (nodes, edges, configuration)
- **Written by:** Backend (when user saves workflow)
- **Read by:** Backend (API endpoints), Worker (to execute workflows)

### `workflow_executions` Table
- Stores execution state and status
- **Written by:** Backend (creates execution), Worker (updates status/results)
- **Read by:** Backend (API endpoints), Frontend (displays execution history), Worker (polls for work)

### `workflow_execution_states` Table (if exists)
- Stores detailed execution state (current node, variables, etc.)
- **Written by:** Worker (during execution)
- **Read by:** Backend (API endpoints), Frontend (execution details)

---

## Complete Workflow Execution Flow

### Step 1: User Creates Workflow
```
Frontend → Backend API → Supabase Database
  User saves workflow → POST /workflows → INSERT INTO workflows
```

### Step 2: User Runs Workflow
```
Frontend → Backend API → Supabase Database
  User clicks "Run" → POST /workflows/{id}/run → INSERT INTO workflow_executions (status='running')
```

### Step 3: Worker Picks Up Execution
```
Worker → Supabase Database
  Polls every 1 second → SELECT * FROM workflow_executions WHERE status='running'
  Finds execution → Starts processing
```

### Step 4: Worker Executes Workflow
```
Worker → Supabase Database (multiple times)
  Updates execution status → UPDATE workflow_executions SET current_node_id='node-1'
  Executes node → Stores result in execution state
  Moves to next node → Updates current_node_id='node-2'
  ... continues until complete ...
```

### Step 5: User Views Execution Status
```
Frontend → Backend API → Supabase Database
  User views executions → GET /workflows/{id}/executions → SELECT * FROM workflow_executions
  Frontend displays real-time status
```

---

## Why This Architecture?

### ✅ **Separation of Concerns**
- **Frontend:** Handles UI and user interactions
- **Backend:** Handles API requests, authentication, validation
- **Worker:** Handles long-running, CPU-intensive workflow execution

### ✅ **Scalability**
- Frontend can scale independently (multiple instances)
- Backend can scale independently (load balancer)
- Worker can scale independently (multiple workers for high throughput)

### ✅ **Reliability**
- If backend crashes, worker continues processing
- If worker crashes, backend can still create executions (worker picks up when restarted)
- Database is the single source of truth

### ✅ **Performance**
- Backend returns immediately (doesn't block on workflow execution)
- Worker processes workflows asynchronously
- Users can continue using the UI while workflows run

---

## Environment Variables

All three services need **the same database connection**:

### Backend & Worker Share:
- `SUPABASE_DB_URL` - Database connection string
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_ANON_KEY` - Supabase anonymous key
- `SECRET_KEY` - Application secret

### Frontend Uses:
- `VITE_SUPABASE_URL` - For authentication
- `VITE_SUPABASE_ANON_KEY` - For authentication
- `VITE_API_URL` - Backend API URL

---

## Worker Polling Behavior

The worker runs a **continuous loop**:

```python
while self.running:
    try:
        # 1. Check for timeouts
        self._check_timeouts(session)

        # 2. Process scheduled executions
        self._process_scheduled_executions(session)

        # 3. Process retry executions
        self._process_retry_executions(session)

        # 4. Process signal-waiting executions
        self._process_signal_executions(session)

        # 5. Process running executions
        self._process_running_executions(session)

        # 6. Process pending executions
        self._process_pending_executions(session)

    except Exception as e:
        print(f"❌ Worker error: {e}")

    time.sleep(1.0)  # Wait 1 second before next poll
```

**Poll Interval:** 1 second (configurable via `WORKFLOW_WORKER_CONCURRENCY`)

---

## Key Points

1. **No Direct Communication:** Backend and Worker never talk directly - only through database
2. **Database as Message Queue:** The `workflow_executions` table acts like a message queue
3. **Idempotent Operations:** Worker can safely retry failed operations
4. **State Persistence:** All execution state is stored in database (survives crashes)
5. **Real-time Updates:** Frontend polls backend API to show execution status

---

## Troubleshooting

### Worker Not Processing Executions
- Check worker logs: `🚀 Workflow worker started`
- Verify `SUPABASE_DB_URL` is set correctly
- Check database connectivity

### Executions Stuck in "Running"
- Check worker logs for errors
- Verify worker is running (Render dashboard)
- Check database for execution records

### Frontend Can't See Executions
- Verify backend API is responding
- Check `VITE_API_URL` is set correctly
- Check backend logs for API errors

---

## Summary

**The worker is a background service that:**
1. Polls Supabase database every 1 second
2. Finds workflow executions that need processing
3. Executes workflow nodes sequentially
4. Updates execution status in database
5. Never directly communicates with backend or frontend

**The backend:**
1. Receives API requests from frontend
2. Creates/updates records in Supabase database
3. Returns responses to frontend
4. Never directly communicates with worker

**The frontend:**
1. Sends HTTP requests to backend API
2. Displays data from backend API responses
3. Never directly communicates with worker or database

**Supabase Database:**
- Acts as the shared state/communication layer
- All three services read/write to the same database
- Ensures consistency and persistence
