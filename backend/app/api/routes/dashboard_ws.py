"""
Dashboard WebSocket Routes

Real-time dashboard statistics updates via WebSocket.
"""

import json
from typing import Any

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from sqlmodel import Session
from supabase import Client, create_client

from app.api.deps import get_db
from app.core.config import settings

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


async def verify_websocket_token(
    websocket: WebSocket, token: str | None = None
) -> dict[str, Any]:
    """
    Verify JWT token from WebSocket connection.

    Args:
        websocket: WebSocket connection
        token: JWT token from query parameter

    Returns:
        Decoded token payload

    Raises:
        HTTPException: If token is invalid
    """
    if not token:
        await websocket.close(code=1008, reason="Missing authentication token")
        return None

    try:
        # Use Supabase to verify the token
        supabase: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_ANON_KEY,
        )

        # Verify token with Supabase
        user_response = supabase.auth.get_user(token)
        if not user_response.user:
            await websocket.close(code=1008, reason="Invalid authentication token")
            return None

        return {
            "user_id": user_response.user.id,
            "email": user_response.user.email,
        }
    except Exception:
        await websocket.close(code=1008, reason="Authentication failed")
        return None


@router.websocket("/stats/ws")
async def dashboard_stats_websocket(
    websocket: WebSocket,
    token: str | None = Query(None),
):
    """
    WebSocket endpoint for real-time dashboard statistics.

    Sends dashboard statistics updates every 30 seconds.
    Client can also request immediate updates by sending {"type": "refresh"}.

    Query Parameters:
    - token: JWT authentication token

    Protocol:
    - Server sends: {"type": "stats", "data": {...dashboard stats...}}
    - Client sends: {"type": "refresh"} to request immediate update
    """
    await websocket.accept()

    try:
        # Verify authentication
        user_info = await verify_websocket_token(websocket, token)
        if not user_info:
            return

        user_id = user_info["user_id"]

        # Send connection confirmation
        await websocket.send_json(
            {
                "type": "connection",
                "status": "connected",
                "user_id": user_id,
            }
        )

        # Get database session
        db_gen = get_db()
        db: Session = next(db_gen)

        import asyncio

        try:
            # Send initial stats
            stats = await get_dashboard_stats_async(db, user_id)
            await websocket.send_json(
                {
                    "type": "stats",
                    "data": stats,
                }
            )

            # Keep connection alive and send periodic updates
            while True:
                # Wait for either:
                # 1. Client message (refresh request)
                # 2. 30 seconds timeout (periodic update)
                try:
                    # Wait for client message with timeout
                    message = await asyncio.wait_for(
                        websocket.receive_text(), timeout=30.0
                    )

                    # Parse client message
                    try:
                        data = json.loads(message)
                        if data.get("type") == "refresh":
                            # Client requested refresh
                            stats = await get_dashboard_stats_async(db, user_id)
                            await websocket.send_json(
                                {
                                    "type": "stats",
                                    "data": stats,
                                }
                            )
                    except json.JSONDecodeError:
                        pass

                except asyncio.TimeoutError:
                    # Timeout - send periodic update
                    stats = await get_dashboard_stats_async(db, user_id)
                    await websocket.send_json(
                        {
                            "type": "stats",
                            "data": stats,
                        }
                    )

        except WebSocketDisconnect:
            # Client disconnected
            pass
        finally:
            db.close()

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


async def get_dashboard_stats_async(session: Session, user_id: str) -> dict[str, Any]:
    """
    Get dashboard stats asynchronously.

    This is a wrapper around the synchronous get_dashboard_stats function.
    """
    import asyncio

    from app.api.deps import CurrentUser
    from app.models import User

    # Get user object
    user = session.get(User, user_id)
    if not user:
        return {}

    # Create a CurrentUser-like object
    current_user = CurrentUser(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_superuser=user.is_superuser,
    )

    # Import the actual function
    from app.api.routes.stats import get_dashboard_stats

    # Run the synchronous function in executor
    loop = asyncio.get_event_loop()
    stats = await loop.run_in_executor(
        None,
        lambda: get_dashboard_stats(session, current_user),
    )

    # Convert to dict
    if hasattr(stats, "model_dump"):
        return stats.model_dump()
    return stats
