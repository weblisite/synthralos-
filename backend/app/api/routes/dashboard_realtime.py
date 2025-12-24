"""
Dashboard Real-Time WebSocket Routes

Event-driven WebSocket endpoint for dashboard updates.
Replaces polling with real-time event broadcasting.
"""

import json
from typing import Any

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from supabase import Client, create_client

from app.core.config import settings
from app.workflows.websocket import default_websocket_manager

router = APIRouter(prefix="/realtime", tags=["realtime"])


async def verify_websocket_token(
    websocket: WebSocket, token: str | None = None
) -> dict[str, Any] | None:
    """
    Verify JWT token from WebSocket connection.

    Args:
        websocket: WebSocket connection
        token: JWT token from query parameter

    Returns:
        Decoded token payload or None if invalid
    """
    import logging

    logger = logging.getLogger(__name__)

    if not token:
        logger.warning("WebSocket connection missing authentication token")
        await websocket.close(code=1008, reason="Missing authentication token")
        return None

    try:
        # Use Supabase to verify the token
        supabase: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_ANON_KEY,
        )

        # Verify token with Supabase
        # Note: get_user() expects an access token, not a refresh token
        user_response = supabase.auth.get_user(token)
        if not user_response.user:
            logger.warning(f"WebSocket token verification failed: no user in response")
            await websocket.close(code=1008, reason="Invalid authentication token")
            return None

        logger.info(
            f"WebSocket token verified for user: {user_response.user.id} ({user_response.user.email})"
        )

        return {
            "user_id": user_response.user.id,
            "email": user_response.user.email,
        }
    except Exception as e:
        logger.error(f"WebSocket token verification error: {str(e)}", exc_info=True)
        await websocket.close(code=1008, reason="Authentication failed")
        return None


@router.websocket("/dashboard")
async def dashboard_realtime_websocket(
    websocket: WebSocket,
    token: str | None = Query(None),
):
    """
    WebSocket endpoint for real-time dashboard updates.

    Event-driven updates (not polling):
    - Receives events when workflow executions change
    - Receives events when dashboard stats change
    - Receives events when system metrics change (admin)

    Query Parameters:
    - token: JWT authentication token

    Protocol:
    - Server sends: {"type": "event-type", "data": {...}}
    - Client sends: {"type": "ping"} for heartbeat
    - Client sends: {"type": "subscribe", "events": ["dashboard-stats", ...]}
    """
    await websocket.accept()

    try:
        # Verify authentication
        user_info = await verify_websocket_token(websocket, token)
        if not user_info:
            return

        user_id = user_info["user_id"]

        # Register connection with WebSocket manager
        if user_id not in default_websocket_manager.user_connections:
            default_websocket_manager.user_connections[user_id] = []
        default_websocket_manager.user_connections[user_id].append(websocket)

        # Send connection confirmation
        from datetime import datetime

        await websocket.send_json(
            {
                "type": "connection",
                "status": "connected",
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        # Handle client messages
        try:
            while True:
                # Wait for client message
                data = await websocket.receive_text()
                try:
                    message = json.loads(data)
                    message_type = message.get("type")

                    if message_type == "ping":
                        # Heartbeat
                        await websocket.send_json({"type": "pong"})
                    elif message_type == "subscribe":
                        # Client subscribes to specific events
                        events = message.get("events", [])
                        # Store subscription info (could be enhanced)
                        await websocket.send_json(
                            {
                                "type": "subscribed",
                                "events": events,
                            }
                        )
                    elif message_type == "refresh":
                        # Client requests immediate refresh
                        # Trigger stats update
                        await default_websocket_manager.broadcast_to_user(
                            user_id,
                            "dashboard-stats-refresh",
                            {"requested": True},
                        )
                except json.JSONDecodeError:
                    pass

        except WebSocketDisconnect:
            # Client disconnected
            pass
        finally:
            # Remove connection
            if user_id in default_websocket_manager.user_connections:
                if websocket in default_websocket_manager.user_connections[user_id]:
                    default_websocket_manager.user_connections[user_id].remove(
                        websocket
                    )

    except Exception as e:
        try:
            await websocket.send_json(
                {
                    "type": "error",
                    "error": str(e),
                }
            )
            await websocket.close()
        except Exception:
            pass
