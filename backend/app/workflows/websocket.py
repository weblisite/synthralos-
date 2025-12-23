"""
WebSocket Real-Time Updates for Workflow Execution

Provides real-time updates for workflow execution progress:
- Execution status updates
- Node completion events
- Log streaming
- Connection management
"""

import json
from datetime import datetime
from typing import Any

from fastapi import WebSocket, WebSocketDisconnect

from app.workflows.engine import WorkflowEngine


class WebSocketManager:
    """
    Manages WebSocket connections for real-time workflow updates.
    """

    def __init__(self):
        """Initialize WebSocket manager."""
        self.active_connections: dict[
            str, list[WebSocket]
        ] = {}  # execution_id -> [websockets]
        self.user_connections: dict[
            str, list[WebSocket]
        ] = {}  # user_id -> [websockets]

    async def connect(
        self, websocket: WebSocket, execution_id: str | None = None
    ) -> None:
        """
        Accept WebSocket connection.

        Args:
            websocket: WebSocket connection
            execution_id: Optional execution ID to subscribe to
        """
        await websocket.accept()

        if execution_id:
            if execution_id not in self.active_connections:
                self.active_connections[execution_id] = []
            self.active_connections[execution_id].append(websocket)

    async def disconnect(
        self, websocket: WebSocket, execution_id: str | None = None
    ) -> None:
        """
        Remove WebSocket connection.

        Args:
            websocket: WebSocket connection
            execution_id: Optional execution ID
        """
        if execution_id and execution_id in self.active_connections:
            if websocket in self.active_connections[execution_id]:
                self.active_connections[execution_id].remove(websocket)

        # Remove from user connections
        for user_id, connections in self.user_connections.items():
            if websocket in connections:
                connections.remove(websocket)

    async def send_execution_update(
        self, execution_id: str, event_type: str, data: dict[str, Any]
    ) -> None:
        """
        Send execution update to subscribed clients.

        Args:
            execution_id: Execution ID
            event_type: Event type (e.g., "execution_started", "node_completed")
            data: Event data
        """
        message = {
            "type": "execution_update",
            "execution_id": execution_id,
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Send to execution-specific connections
        if execution_id in self.active_connections:
            disconnected = []
            for websocket in self.active_connections[execution_id]:
                try:
                    await websocket.send_json(message)
                except Exception:
                    disconnected.append(websocket)

            # Remove disconnected websockets
            for ws in disconnected:
                self.active_connections[execution_id].remove(ws)

    async def send_node_update(
        self,
        execution_id: str,
        node_id: str,
        event_type: str,
        data: dict[str, Any],
    ) -> None:
        """
        Send node update to subscribed clients.

        Args:
            execution_id: Execution ID
            node_id: Node ID
            event_type: Event type (e.g., "node_started", "node_completed")
            data: Event data
        """
        await self.send_execution_update(
            execution_id,
            event_type,
            {
                "node_id": node_id,
                **data,
            },
        )

    async def send_log_update(
        self,
        execution_id: str,
        node_id: str | None,
        level: str,
        message: str,
    ) -> None:
        """
        Send log update to subscribed clients.

        Args:
            execution_id: Execution ID
            node_id: Optional node ID
            level: Log level (info, error, warning, debug)
            message: Log message
        """
        await self.send_execution_update(
            execution_id,
            "log",
            {
                "node_id": node_id,
                "level": level,
                "message": message,
            },
        )

    async def broadcast_to_user(
        self, user_id: str, event_type: str, data: dict[str, Any]
    ) -> None:
        """
        Broadcast message to all connections for a user.

        Args:
            user_id: User ID
            event_type: Event type
            data: Event data
        """
        message = {
            "type": "user_update",
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
        }

        if user_id in self.user_connections:
            disconnected = []
            for websocket in self.user_connections[user_id]:
                try:
                    await websocket.send_json(message)
                except Exception:
                    disconnected.append(websocket)

            # Remove disconnected websockets
            for ws in disconnected:
                self.user_connections[user_id].remove(ws)


# Global WebSocket manager instance
default_websocket_manager = WebSocketManager()


async def websocket_endpoint(
    websocket: WebSocket,
    execution_id: str | None = None,
    user_id: str | None = None,
) -> None:
    """
    WebSocket endpoint for workflow execution updates.

    Args:
        websocket: WebSocket connection
        execution_id: Optional execution ID to subscribe to
        user_id: Optional user ID for user-specific updates
    """
    await default_websocket_manager.connect(websocket, execution_id)

    if user_id:
        if user_id not in default_websocket_manager.user_connections:
            default_websocket_manager.user_connections[user_id] = []
        default_websocket_manager.user_connections[user_id].append(websocket)

    try:
        while True:
            # Keep connection alive and handle client messages
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                # Handle client messages (e.g., subscribe/unsubscribe)
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        await default_websocket_manager.disconnect(websocket, execution_id)
        if user_id and user_id in default_websocket_manager.user_connections:
            if websocket in default_websocket_manager.user_connections[user_id]:
                default_websocket_manager.user_connections[user_id].remove(websocket)


# Hook into workflow engine to emit WebSocket events
def setup_websocket_hooks(workflow_engine: WorkflowEngine) -> None:
    """
    Setup WebSocket event hooks for workflow engine.

    Args:
        workflow_engine: WorkflowEngine instance
    """
    # This would be called during engine initialization
    # For now, we'll emit events manually in the engine
    pass
