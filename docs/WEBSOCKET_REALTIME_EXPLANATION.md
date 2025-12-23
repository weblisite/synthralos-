# Real-Time Dashboard Updates: WebSocket Implementation Explanation

**Status:** Explanation Only (Not Implemented)
**Priority:** Medium
**Current State:** Polling-based updates (with partial WebSocket infrastructure)
**Proposed State:** Full WebSocket-based real-time updates

---

## Executive Summary

Currently, dashboard components use **polling** (periodic API requests) to refresh data. However, the codebase **already has partial WebSocket infrastructure**:
- ✅ `backend/app/api/routes/dashboard_ws.py` - WebSocket endpoint exists (`/api/v1/stats/ws`)
- ✅ `backend/app/workflows/websocket.py` - WebSocket manager for workflow execution updates
- ✅ `frontend/src/components/Chat/AgUIProvider.tsx` - Chat uses WebSocket successfully

**This document explains how to fully integrate WebSocket** for all dashboard components, replacing polling with event-driven real-time updates.

---

## 1. Current Implementation (Polling)

### How It Works Now

**Frontend Components:**
- `DashboardStats.tsx`: Polls every **30 seconds** (`refetchInterval: 30000`)
- `SystemMetrics.tsx`: Polls every **60 seconds** (`refetchInterval: 60000`)
- `CostAnalytics.tsx`: Manual refresh on mount
- `AnalyticsPanel.tsx`: Manual refresh on query

**Backend:**
- Standard REST API endpoints return current state
- **Partial WebSocket infrastructure exists** (`dashboard_ws.py`) but **not used by frontend**
- Each request is independent
- WebSocket endpoint `/api/v1/stats/ws` exists but dashboard components don't connect to it

### Current Flow

```
┌─────────────┐                    ┌─────────────┐
│  Frontend   │                    │   Backend   │
│  Component  │                    │     API     │
└──────┬──────┘                    └──────┬──────┘
       │                                   │
       │  GET /api/v1/stats/dashboard      │
       │──────────────────────────────────>│
       │                                   │ Query DB
       │                                   │ Process
       │  { stats: {...} }                │
       │<──────────────────────────────────│
       │                                   │
       │  [Wait 30 seconds]                │
       │                                   │
       │  GET /api/v1/stats/dashboard      │
       │──────────────────────────────────>│
       │                                   │ Query DB
       │                                   │ Process
       │  { stats: {...} }                │
       │<──────────────────────────────────│
       │                                   │
       │  [Repeat forever...]              │
       └───────────────────────────────────┘
```

### Problems with Polling

1. **Delayed Updates**: Up to 30-60 seconds delay before users see changes
2. **Unnecessary Load**: Constant requests even when nothing changed
3. **Battery Drain**: Mobile devices constantly polling
4. **Network Overhead**: HTTP headers, connection setup for each request
5. **Race Conditions**: Multiple components polling simultaneously
6. **No Event Context**: Can't tell what changed, only that data is different

---

## 2. Proposed Implementation (WebSocket)

### How It Would Work

**Frontend:**
- Single WebSocket connection per user session
- Subscribe to specific event types (dashboard updates, execution events, etc.)
- Receive push notifications when data changes
- Update UI reactively using React Query mutations

**Backend:**
- WebSocket server endpoint (e.g., `/ws/dashboard`)
- Event-driven architecture
- Broadcast updates when relevant data changes
- Connection management (reconnect, authentication)

### Proposed Flow

```
┌─────────────┐                    ┌─────────────┐
│  Frontend   │                    │   Backend   │
│  Component  │                    │  WebSocket  │
└──────┬──────┘                    │   Server    │
       │                           └──────┬──────┘
       │  WS Connection                   │
       │─────────────────────────────────>│
       │  Authenticate (JWT)              │
       │<─────────────────────────────────│
       │  Subscribe: dashboard-updates    │
       │─────────────────────────────────>│
       │                                  │
       │  [Connection Established]        │
       │                                  │
       │                                  │ [Workflow Execution Completes]
       │                                  │ [Event Triggered]
       │                                  │
       │  { type: "dashboard-update",     │
       │    data: { executions: {...} } } │
       │<─────────────────────────────────│
       │                                  │
       │  [React Query Updates UI]        │
       │                                  │
       │  { type: "execution-started",   │
       │    execution_id: "..." }         │
       │<─────────────────────────────────│
       │                                  │
       │  [UI Updates Instantly]          │
       └──────────────────────────────────┘
```

---

## 3. Architecture Design

### 3.1 Backend Architecture

#### WebSocket Server Setup

**Technology Options:**
1. **FastAPI WebSocket** (Recommended)
   - Native FastAPI support
   - Easy integration with existing codebase
   - Built-in async support

2. **Socket.IO** (Alternative)
   - More features (rooms, namespaces)
   - Better browser compatibility
   - Requires separate server

**Recommended: FastAPI WebSocket**

```python
# backend/app/api/routes/websocket.py (Proposed)

from fastapi import WebSocket, WebSocketDisconnect
from app.api.deps import get_current_user_from_token

class ConnectionManager:
    """Manages WebSocket connections"""

    def __init__(self):
        # Map: user_id -> list of WebSocket connections
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    async def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)

    async def send_personal_message(self, message: dict, user_id: str):
        """Send message to specific user"""
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except:
                    # Connection closed, remove it
                    self.active_connections[user_id].remove(connection)

    async def broadcast(self, message: dict, user_ids: list[str] | None = None):
        """Broadcast to specific users or all users"""
        targets = user_ids or self.active_connections.keys()
        for user_id in targets:
            await self.send_personal_message(message, user_id)

manager = ConnectionManager()

@router.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    """WebSocket endpoint for dashboard updates"""
    # Authenticate user from token in query params
    token = websocket.query_params.get("token")
    user = await get_current_user_from_token(token)

    await manager.connect(websocket, str(user.id))

    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            # Handle client messages (subscriptions, pings, etc.)
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(websocket, str(user.id))
```

#### Event Broadcasting

**Where to Trigger Events:**

1. **Workflow Execution Events**
   ```python
   # backend/app/workflows/engine.py

   async def create_execution(...):
       execution = WorkflowExecution(...)
       session.add(execution)
       session.commit()

       # Broadcast event
       await manager.broadcast({
           "type": "execution-started",
           "user_id": str(workflow.owner_id),
           "data": {
               "execution_id": str(execution.id),
               "workflow_id": str(execution.workflow_id),
               "status": "running"
           }
       }, user_ids=[str(workflow.owner_id)])
   ```

2. **Dashboard Stats Changes**
   ```python
   # backend/app/api/routes/stats.py

   # When stats change, broadcast update
   await manager.broadcast({
       "type": "dashboard-stats-update",
       "user_id": str(user_id),
       "data": {
           "executions": {...},
           "agents": {...},
           # ... updated stats
       }
   }, user_ids=[str(user_id)])
   ```

3. **System Metrics Updates**
   ```python
   # backend/app/api/routes/admin_system.py

   # Periodic broadcast for admins
   async def broadcast_system_metrics():
       metrics = get_system_metrics(...)
       admin_user_ids = get_all_admin_user_ids()

       await manager.broadcast({
           "type": "system-metrics-update",
           "data": metrics
       }, user_ids=admin_user_ids)
   ```

#### Event Types

**Proposed Event Schema:**

```typescript
// frontend/src/types/websocket.ts (Proposed)

interface WebSocketMessage {
  type: string
  timestamp: string
  user_id?: string
  data: any
}

// Event Types:
// - "dashboard-stats-update" - Dashboard statistics changed
// - "execution-started" - Workflow execution started
// - "execution-completed" - Workflow execution completed
// - "execution-failed" - Workflow execution failed
// - "agent-task-update" - Agent task status changed
// - "system-metrics-update" - System metrics updated (admin)
// - "cost-analytics-update" - Cost data updated (admin)
// - "connector-stats-update" - Connector statistics updated (admin)
// - "error" - Error occurred
// - "pong" - Response to ping
```

---

### 3.2 Frontend Architecture

#### WebSocket Hook

**Proposed Hook:**

```typescript
// frontend/src/hooks/useWebSocket.ts (Proposed)

import { useEffect, useRef, useState } from "react"
import { useQueryClient } from "@tanstack/react-query"
import { supabase } from "@/lib/supabase"

interface WebSocketMessage {
  type: string
  timestamp: string
  data: any
}

export function useWebSocket() {
  const [isConnected, setIsConnected] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)
  const queryClient = useQueryClient()
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>()

  useEffect(() => {
    const connect = async () => {
      // Get auth token
      const { data: { session } } = await supabase.auth.getSession()
      if (!session) return

      const wsUrl = `${getWebSocketUrl()}/ws/dashboard?token=${session.access_token}`
      const ws = new WebSocket(wsUrl)

      ws.onopen = () => {
        setIsConnected(true)
        console.log("WebSocket connected")
      }

      ws.onmessage = (event) => {
        const message: WebSocketMessage = JSON.parse(event.data)
        handleMessage(message)
      }

      ws.onerror = (error) => {
        console.error("WebSocket error:", error)
        setIsConnected(false)
      }

      ws.onclose = () => {
        setIsConnected(false)
        // Reconnect after 3 seconds
        reconnectTimeoutRef.current = setTimeout(connect, 3000)
      }

      wsRef.current = ws
    }

    const handleMessage = (message: WebSocketMessage) => {
      switch (message.type) {
        case "dashboard-stats-update":
          // Invalidate and refetch dashboard stats
          queryClient.invalidateQueries({ queryKey: ["dashboardStats"] })
          break

        case "execution-started":
        case "execution-completed":
        case "execution-failed":
          // Invalidate execution-related queries
          queryClient.invalidateQueries({ queryKey: ["workflowExecutions"] })
          queryClient.invalidateQueries({ queryKey: ["dashboardStats"] })
          break

        case "system-metrics-update":
          queryClient.invalidateQueries({ queryKey: ["systemMetrics"] })
          break

        case "cost-analytics-update":
          queryClient.invalidateQueries({ queryKey: ["costAnalytics"] })
          break

        case "pong":
          // Heartbeat response
          break

        default:
          console.log("Unknown message type:", message.type)
      }
    }

    connect()

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [])

  return { isConnected }
}
```

#### Component Integration

**Update Dashboard Components:**

```typescript
// frontend/src/components/Dashboard/DashboardStats.tsx

import { useWebSocket } from "@/hooks/useWebSocket"

export function DashboardStats() {
  // Establish WebSocket connection
  const { isConnected } = useWebSocket()

  // Remove refetchInterval - updates come via WebSocket
  const { data: stats, isLoading } = useQuery({
    queryKey: ["dashboardStats"],
    queryFn: fetchDashboardStats,
    // refetchInterval: 30000, // REMOVED - WebSocket handles updates
  })

  // Show connection status indicator
  return (
    <div className="space-y-6">
      {!isConnected && (
        <Alert>
          <AlertDescription>
            Real-time updates disconnected. Using polling fallback.
          </AlertDescription>
        </Alert>
      )}
      {/* ... rest of component */}
    </div>
  )
}
```

---

## 4. Implementation Steps

### Phase 1: Backend WebSocket Server

1. **Install Dependencies**
   ```bash
   # FastAPI already supports WebSocket, no extra packages needed
   ```

2. **Create WebSocket Router**
   - `backend/app/api/routes/websocket.py`
   - Connection manager class
   - Authentication middleware
   - Event broadcasting functions

3. **Integrate with Existing Code**
   - Add broadcast calls in workflow engine
   - Add broadcast calls in stats endpoints
   - Add broadcast calls in admin endpoints

4. **Add WebSocket Endpoint**
   - Register router in `backend/app/api/main.py`
   - Test connection with Postman/WebSocket client

### Phase 2: Frontend WebSocket Client

1. **Create WebSocket Hook**
   - `frontend/src/hooks/useWebSocket.ts`
   - Connection management
   - Message handling
   - Reconnection logic

2. **Update Components**
   - Remove `refetchInterval` from React Query
   - Add `useWebSocket()` hook
   - Handle WebSocket messages
   - Add connection status indicator

3. **Add Fallback**
   - Keep polling as fallback if WebSocket fails
   - Show user when using fallback mode

### Phase 3: Testing & Optimization

1. **Test Scenarios**
   - Multiple browser tabs
   - Connection drops
   - Authentication expiry
   - High-frequency updates

2. **Performance Optimization**
   - Throttle updates (max 1 per second)
   - Batch multiple events
   - Compress large payloads

3. **Monitoring**
   - Track connection count
   - Monitor message throughput
   - Alert on connection failures

---

## 5. Benefits & Trade-offs

### Benefits

1. **Real-Time Updates**: Instant feedback (< 100ms latency)
2. **Reduced Server Load**: No constant polling requests
3. **Better UX**: Users see changes immediately
4. **Event Context**: Know what changed, not just that it changed
5. **Battery Efficient**: Mobile devices don't constantly poll
6. **Scalable**: One connection vs. many HTTP requests

### Trade-offs

1. **Complexity**: More moving parts to manage
2. **Connection Management**: Handle reconnects, timeouts
3. **State Synchronization**: Ensure UI stays in sync
4. **Debugging**: Harder to debug than REST endpoints
5. **Infrastructure**: Need WebSocket support in deployment (Render supports this)

---

## 6. Technical Considerations

### Authentication

**Option 1: Token in Query String**
```
ws://backend/ws/dashboard?token=JWT_TOKEN
```
- Simple
- Token visible in logs
- Works with Supabase JWT

**Option 2: Token in Subprotocol**
```
new WebSocket(url, ["bearer", token])
```
- More secure
- Requires backend subprotocol handling

**Recommended: Option 1** (simpler, sufficient security)

### Connection Lifecycle

1. **Connect**: On app mount or user login
2. **Authenticate**: Verify JWT token
3. **Subscribe**: Send subscription messages
4. **Receive**: Handle incoming events
5. **Reconnect**: Auto-reconnect on disconnect
6. **Disconnect**: On logout or app unmount

### Error Handling

- **Connection Failed**: Fall back to polling
- **Authentication Failed**: Redirect to login
- **Message Parse Error**: Log and ignore
- **Rate Limiting**: Throttle reconnection attempts

### Scaling Considerations

**Single Server (Current):**
- All connections on one server
- Works for < 1000 concurrent users

**Multiple Servers (Future):**
- Need Redis pub/sub for cross-server messaging
- Sticky sessions or shared state
- More complex but scales horizontally

---

## 7. Migration Strategy

### Gradual Rollout

1. **Phase 1**: Deploy WebSocket server alongside REST API
2. **Phase 2**: Add WebSocket client with polling fallback
3. **Phase 3**: Monitor WebSocket usage and performance
4. **Phase 4**: Remove polling once WebSocket is stable
5. **Phase 5**: Optimize and scale

### Backward Compatibility

- Keep REST endpoints for non-WebSocket clients
- Support both polling and WebSocket simultaneously
- Allow users to toggle between modes (for debugging)

---

## 8. Example Implementation Flow

### Scenario: Workflow Execution Completes

```
1. User runs workflow
   ↓
2. Backend: Workflow execution completes
   ↓
3. Backend: Broadcast WebSocket event
   {
     type: "execution-completed",
     user_id: "user-123",
     data: { execution_id: "...", status: "completed" }
   }
   ↓
4. Frontend: WebSocket receives message
   ↓
5. Frontend: React Query invalidates cache
   queryClient.invalidateQueries({ queryKey: ["dashboardStats"] })
   ↓
6. Frontend: React Query refetches data
   ↓
7. Frontend: UI updates automatically
   ↓
8. User sees updated execution count instantly (< 100ms)
```

**Without WebSocket:**
- User waits up to 30 seconds
- Multiple unnecessary API calls
- Higher server load

---

## 9. Monitoring & Debugging

### Metrics to Track

- **Connection Count**: Active WebSocket connections
- **Message Rate**: Messages per second
- **Reconnection Rate**: How often connections drop
- **Latency**: Time from event to UI update
- **Error Rate**: Failed messages or connections

### Debugging Tools

- Browser DevTools: Network → WS tab
- Backend Logs: Connection events
- React Query DevTools: Query invalidation tracking

---

## 10. Security Considerations

1. **Authentication**: Verify JWT on connection
2. **Authorization**: Only send user's own data
3. **Rate Limiting**: Prevent message spam
4. **Input Validation**: Validate all WebSocket messages
5. **CORS**: Configure WebSocket CORS properly

---

## Summary

**Current State:**
- Polling every 30-60 seconds
- Delayed updates
- Higher server load

**Proposed State:**
- WebSocket connection per user
- Real-time updates (< 100ms)
- Event-driven architecture
- Reduced server load

**Implementation Effort:**
- Backend: ~2-3 days
- Frontend: ~1-2 days
- Testing: ~1 day
- **Total: ~4-6 days**

**Recommendation:**
Implement WebSocket for better UX and scalability, but keep polling as fallback for reliability.

---

**Next Steps (When Ready):**
1. Review this explanation
2. Approve architecture
3. Implement backend WebSocket server
4. Implement frontend WebSocket client
5. Test and deploy
6. Monitor and optimize
