"""
Chat API Routes

Endpoints for chat interface and WebSocket bridge.
"""

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlmodel import Session
from supabase import Client, create_client

from app.api.deps import CurrentUser, SessionDep, get_db
from app.core.config import settings
from app.services.chat_processor import default_chat_processor
from app.workflows.engine import WorkflowEngine

router = APIRouter(prefix="/chat", tags=["chat"])

# WebSocket router (no prefix, will be mounted at /api/v1/agws)
ws_router = APIRouter()

# Initialize workflow engine
workflow_engine = WorkflowEngine()


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
        raise HTTPException(status_code=401, detail="Missing authentication token")

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
            raise HTTPException(status_code=401, detail="Invalid authentication token")

        return {
            "user_id": user_response.user.id,
            "email": user_response.user.email,
        }
    except Exception as e:
        await websocket.close(code=1008, reason="Authentication failed")
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")


@ws_router.websocket("/agws")
async def websocket_bridge(
    websocket: WebSocket,
    token: str | None = Query(None),
):
    """
    WebSocket bridge for ag-ui protocol.

    Translates LangGraph events to ag-ui protocol format.
    Handles real-time streaming of workflow execution events.

    Query Parameters:
    - token: JWT authentication token

    Protocol:
    - Client sends: {"type": "message", "content": "...", "mode": "..."}
    - Server sends: {"type": "message", "role": "assistant", "content": "...", "tool_calls": [...]}
    """
    await websocket.accept()

    try:
        # Verify authentication
        user_info = await verify_websocket_token(websocket, token)
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

        try:
            while True:
                # Receive message from client
                data = await websocket.receive_json()

                message_type = data.get("type")

                if message_type == "message":
                    # Handle chat message
                    content = data.get("content", "")
                    mode = data.get("mode", "automation")

                    # Process message based on mode
                    response = await process_chat_message(
                        db,
                        user_id,
                        content,
                        mode,
                        websocket,
                    )

                    # Send response
                    await websocket.send_json(
                        {
                            "type": "message",
                            "id": str(uuid.uuid4()),
                            "role": "assistant",
                            "content": response.get("content", ""),
                            "tool_calls": response.get("tool_calls", []),
                            "timestamp": response.get("timestamp"),
                        }
                    )

                elif message_type == "ping":
                    # Handle ping/pong
                    await websocket.send_json({"type": "pong"})

                else:
                    await websocket.send_json(
                        {
                            "type": "error",
                            "error": f"Unknown message type: {message_type}",
                        }
                    )

        except WebSocketDisconnect:
            # Client disconnected
            pass
        finally:
            db.close()

    except HTTPException:
        # Authentication failed, connection already closed
        pass
    except Exception as e:
        try:
            await websocket.send_json(
                {
                    "type": "error",
                    "error": f"Server error: {str(e)}",
                }
            )
            await websocket.close(code=1011, reason="Internal server error")
        except:
            pass


async def process_chat_message(
    db: Session,
    user_id: str,
    content: str,
    mode: str,
    websocket: WebSocket | None = None,
) -> dict[str, Any]:
    """
    Process a chat message and return response.

    Args:
        db: Database session
        user_id: User ID
        content: Message content
        mode: Chat mode (automation, agent, agent_flow, code)
        websocket: Optional WebSocket connection for streaming

    Returns:
        Response dictionary with content and tool_calls
    """
    # Use chat processor to handle the message
    processor = default_chat_processor
    response = await processor.process_message(
        session=db,
        user_id=user_id,
        content=content,
        mode=mode,
    )

    # If WebSocket is available, stream tool calls as they happen
    if websocket and response.get("tool_calls"):
        for tool_call in response["tool_calls"]:
            await websocket.send_json(
                {
                    "type": "tool_call",
                    "message_id": response.get("id", ""),
                    "tool_call": tool_call,
                }
            )

    return response


@router.post("/")
async def chat_endpoint(
    message: dict[str, Any],
    session: SessionDep,
    current_user: CurrentUser,
) -> dict[str, Any]:
    """
    HTTP fallback endpoint for chat.

    This endpoint is used when WebSocket is not available.
    It processes chat messages and returns responses.

    Request Body:
    {
        "message": "User message",
        "mode": "automation|agent|agent_flow|code"
    }

    Returns:
    {
        "id": "message-id",
        "message": "Response message",
        "tool_calls": [...]
    }
    """
    content = message.get("message", "")
    mode = message.get("mode", "automation")

    # Process message (same logic as WebSocket)
    response = await process_chat_message(
        session,
        str(current_user.id),
        content,
        mode,
        None,  # No WebSocket for HTTP endpoint
    )

    return {
        "id": str(uuid.uuid4()),
        "message": response.get("content", ""),
        "tool_calls": response.get("tool_calls", []),
    }
