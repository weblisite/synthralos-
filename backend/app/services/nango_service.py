"""
Nango Service

Wrapper around Nango SDK for OAuth connection management.
"""

import logging
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)

try:
    from nango import Nango

    NANGO_AVAILABLE = True
except ImportError:
    NANGO_AVAILABLE = False
    logger.warning("Nango SDK not installed. Install with: pip install nango")


class NangoService:
    """Service for managing OAuth connections via Nango"""

    def __init__(self):
        if not NANGO_AVAILABLE:
            raise ImportError(
                "Nango SDK not installed. Install with: pip install nango"
            )

        if not hasattr(settings, "NANGO_SECRET_KEY") or not settings.NANGO_SECRET_KEY:
            raise ValueError("NANGO_SECRET_KEY not configured in environment variables")

        self.client = Nango(
            secret_key=settings.NANGO_SECRET_KEY,
            base_url=getattr(settings, "NANGO_BASE_URL", "https://api.nango.dev"),
        )
        logger.info("Nango service initialized")

    async def create_connection(
        self,
        user_id: str,
        connector_slug: str,
        connection_id: str,
        return_url: str,
        provider_key: str | None = None,
    ) -> dict[str, Any]:
        """
        Initiate OAuth connection via Nango.

        Args:
            user_id: Your platform's user ID
            connector_slug: Connector slug (e.g., 'gmail', 'slack')
            connection_id: Unique connection identifier
            return_url: URL to redirect after OAuth completion
            provider_key: Nango provider key (if different from connector_slug)

        Returns:
            Dict with oauth_url and connection_id
        """
        try:
            # Use provider_key if provided, otherwise use connector_slug
            provider_config_key = provider_key or connector_slug

            logger.info(
                f"Creating Nango connection: user={user_id}, "
                f"provider={provider_config_key}, connection_id={connection_id}"
            )

            # Create connection in Nango
            # Note: Nango SDK may be sync or async - handle both
            import asyncio

            try:
                # Try async version first
                if hasattr(self.client.auth, "create_async"):
                    response = await self.client.auth.create_async(
                        provider_config_key=provider_config_key,
                        connection_id=connection_id,
                        return_url=return_url,
                        user_id=user_id,
                    )
                else:
                    # Run sync version in thread pool
                    response = await asyncio.to_thread(
                        self.client.auth.create,
                        provider_config_key=provider_config_key,
                        connection_id=connection_id,
                        return_url=return_url,
                        user_id=user_id,
                    )
            except AttributeError:
                # Fallback: direct sync call (if already in sync context)
                response = self.client.auth.create(
                    provider_config_key=provider_config_key,
                    connection_id=connection_id,
                    return_url=return_url,
                    user_id=user_id,
                )

            return {
                "oauth_url": response.get("url") or response.get("oauth_url"),
                "connection_id": connection_id,
            }
        except Exception as e:
            logger.error(f"Failed to create Nango connection: {e}", exc_info=True)
            raise

    async def get_access_token(self, connection_id: str, provider_key: str) -> str:
        """
        Get access token for a connection.

        Args:
            connection_id: Nango connection ID
            provider_key: Nango provider key

        Returns:
            Access token string
        """
        try:
            logger.debug(f"Getting access token for connection: {connection_id}")

            # Get connection from Nango (may be sync or async)
            import asyncio

            try:
                if hasattr(self.client.auth, "get_async"):
                    response = await self.client.auth.get_async(
                        provider_config_key=provider_key, connection_id=connection_id
                    )
                else:
                    response = await asyncio.to_thread(
                        self.client.auth.get,
                        provider_config_key=provider_key,
                        connection_id=connection_id,
                    )
            except AttributeError:
                response = self.client.auth.get(
                    provider_config_key=provider_key, connection_id=connection_id
                )

            # Extract access token from response
            # Adjust based on your Nango SDK version
            credentials = response.get("credentials") or response
            access_token = credentials.get("access_token") or credentials.get("token")

            if not access_token:
                raise ValueError("Access token not found in Nango response")

            return access_token
        except Exception as e:
            logger.error(f"Failed to get access token: {e}", exc_info=True)
            raise

    async def delete_connection(self, connection_id: str, provider_key: str) -> None:
        """
        Delete/disconnect a connection.

        Args:
            connection_id: Nango connection ID
            provider_key: Nango provider key
        """
        try:
            logger.info(f"Deleting Nango connection: {connection_id}")

            # Try async first, fallback to sync
            try:
                if hasattr(self.client.auth, "delete_async"):
                    await self.client.auth.delete_async(
                        provider_config_key=provider_key, connection_id=connection_id
                    )
                else:
                    import asyncio

                    await asyncio.to_thread(
                        self.client.auth.delete,
                        provider_config_key=provider_key,
                        connection_id=connection_id,
                    )
            except AttributeError:
                self.client.auth.delete(
                    provider_config_key=provider_key, connection_id=connection_id
                )

            logger.info(f"Successfully deleted connection: {connection_id}")
        except Exception as e:
            logger.error(f"Failed to delete connection: {e}", exc_info=True)
            raise

    async def get_connection_status(
        self, connection_id: str, provider_key: str
    ) -> dict[str, Any]:
        """
        Get connection status from Nango.

        Args:
            connection_id: Nango connection ID
            provider_key: Nango provider key

        Returns:
            Connection status information
        """
        try:
            import asyncio

            try:
                if hasattr(self.client.auth, "get_async"):
                    response = await self.client.auth.get_async(
                        provider_config_key=provider_key, connection_id=connection_id
                    )
                else:
                    response = await asyncio.to_thread(
                        self.client.auth.get,
                        provider_config_key=provider_key,
                        connection_id=connection_id,
                    )
            except AttributeError:
                response = self.client.auth.get(
                    provider_config_key=provider_key, connection_id=connection_id
                )
            return response
        except Exception as e:
            logger.error(f"Failed to get connection status: {e}", exc_info=True)
            raise


# Singleton instance
_nango_service: NangoService | None = None


def get_nango_service() -> NangoService:
    """Get or create Nango service instance"""
    global _nango_service
    if _nango_service is None:
        _nango_service = NangoService()
    return _nango_service
