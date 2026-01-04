"""
Supabase Realtime Sync Service

Publishes user updates to Supabase Realtime for frontend subscriptions.
"""
import logging
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)

# Try to import Supabase client
try:
    from supabase import create_client

    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logger.warning("supabase-py not installed. Real-time sync will be disabled.")


def get_supabase_client() -> Any | None:
    """Get or create Supabase client for Realtime."""
    if not SUPABASE_AVAILABLE:
        return None

    if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
        logger.warning(
            "SUPABASE_URL or SUPABASE_ANON_KEY not configured. "
            "Real-time sync will be disabled."
        )
        return None

    try:
        client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
        return client
    except Exception as e:
        logger.error(f"Failed to create Supabase client: {str(e)}", exc_info=True)
        return None


def publish_user_update(user_id: str, event_type: str, data: dict[str, Any]) -> None:
    """
    Publish user update event to Supabase Realtime.

    Args:
        user_id: UUID of the user in database
        event_type: Type of event (created, updated, deleted)
        data: User data to broadcast
    """
    client = get_supabase_client()
    if not client:
        return

    try:
        # Use Supabase Realtime to broadcast the update
        # Note: Supabase Realtime works via PostgreSQL NOTIFY/LISTEN
        # We'll use a channel-based approach
        channel = client.realtime.channel(f"user_updates:{user_id}")

        # Publish the event
        channel.send(
            {
                "type": "broadcast",
                "event": f"user_{event_type}",
                "payload": {
                    "user_id": user_id,
                    "event_type": event_type,
                    "data": data,
                },
            }
        )

        logger.info(f"Published user {event_type} event for user {user_id}")
    except Exception as e:
        logger.error(
            f"Failed to publish user update to Realtime: {str(e)}",
            exc_info=True,
        )


def publish_user_created(user_id: str, user_data: dict[str, Any]) -> None:
    """Publish user.created event."""
    publish_user_update(user_id, "created", user_data)


def publish_user_updated(user_id: str, user_data: dict[str, Any]) -> None:
    """Publish user.updated event."""
    publish_user_update(user_id, "updated", user_data)


def publish_user_deleted(user_id: str) -> None:
    """Publish user.deleted event."""
    publish_user_update(user_id, "deleted", {"user_id": user_id})
