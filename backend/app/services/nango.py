"""
Nango Integration Service

Handles OAuth flows via Nango for connector authentication.
Nango provides unified OAuth management for 100+ SaaS integrations.
"""

import uuid
from typing import Any

import httpx
from sqlmodel import Session

from app.core.config import settings


# Lazy import to avoid circular dependency
def _get_pkce_generator():
    from app.connectors.pkce import generate_pkce_pair

    return generate_pkce_pair


# Lazy import NangoError to avoid circular dependency
def _get_nango_error():
    from app.services.exceptions import NangoError

    return NangoError


class NangoService:
    """
    Nango service for unified OAuth management.

    Handles:
    - OAuth authorization URL generation via Nango
    - OAuth callback processing via Nango
    - Token retrieval from Nango
    - Token refresh via Nango
    """

    def __init__(self):
        """Initialize Nango service."""
        # Use NANGO_BASE_URL if available, fallback to NANGO_URL for backward compatibility
        base_url = (
            getattr(settings, "NANGO_BASE_URL", None)
            or getattr(settings, "NANGO_URL", None)
            or "https://api.nango.dev"
        )
        self.base_url = str(base_url).rstrip("/")
        self.secret_key = getattr(settings, "NANGO_SECRET_KEY", "")
        self.enabled = getattr(settings, "NANGO_ENABLED", True) and bool(
            self.secret_key
        )
        self._registry = None  # Lazy load to avoid circular import

    def _get_registry(self):
        """Get connector registry (lazy import to avoid circular dependency)."""
        if self._registry is None:
            from app.connectors.registry import default_connector_registry

            self._registry = default_connector_registry
        return self._registry

    def _get_headers(self) -> dict[str, str]:
        """Get Nango API headers."""
        return {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json",
        }

    def generate_authorization_url(
        self,
        session: Session,
        connector_slug: str,
        user_id: uuid.UUID,
        redirect_uri: str,
        scopes: list[str] | None = None,
    ) -> dict[str, str]:
        """
        Generate OAuth authorization URL via Nango.

        Args:
            session: Database session
            connector_slug: Connector slug (must match Nango provider key)
            user_id: User ID requesting authorization
            redirect_uri: Callback redirect URI
            scopes: Optional list of OAuth scopes

        Returns:
            Dictionary with 'authorization_url', 'state', and 'connection_id'

        Raises:
            NangoError: If Nango request fails
        """
        if not self.enabled:
            NangoError = _get_nango_error()
            raise NangoError("Nango integration is not enabled or configured")

        # Get connector to verify it exists
        try:
            from app.connectors.registry import ConnectorNotFoundError

            connector_version = self._get_registry().get_connector(
                session, connector_slug
            )
        except ConnectorNotFoundError:
            NangoError = _get_nango_error()
            raise NangoError(f"Connector '{connector_slug}' not found")

        # Get Nango provider key from manifest (defaults to slug)
        manifest = connector_version.manifest
        nango_config = manifest.get("nango", {})
        provider_key = nango_config.get("provider_key", connector_slug)

        # Prepare Nango authorization request
        # Nango uses connection_id to identify unique user connections
        connection_id = f"{user_id}_{connector_slug}"

        # Map scopes if provided in manifest
        requested_scopes = scopes or []
        if not requested_scopes:
            # Get default scopes from manifest
            oauth_config = manifest.get("oauth", {})
            requested_scopes = oauth_config.get("default_scopes", [])

        # Generate PKCE code verifier and challenge for enhanced security
        generate_pkce_pair = _get_pkce_generator()
        code_verifier, code_challenge = generate_pkce_pair()

        # Build Nango authorization URL
        # Format: {NANGO_URL}/oauth/{provider_key}?connection_id={connection_id}&redirect_uri={redirect_uri}
        # Note: Nango may support PKCE parameters - include them for providers that support it
        params = {
            "connection_id": connection_id,
            "redirect_uri": redirect_uri,
        }

        if requested_scopes:
            params["scopes"] = ",".join(requested_scopes)

        # Add PKCE parameters (if Nango/provider supports it)
        # Some OAuth providers require PKCE, so we include it
        params["code_challenge"] = code_challenge
        params["code_challenge_method"] = "S256"

        from urllib.parse import urlencode

        auth_url = f"{self.base_url}/oauth/{provider_key}?{urlencode(params)}"

        # Generate state token for CSRF protection
        import secrets

        state_token = secrets.token_urlsafe(32)

        return {
            "authorization_url": auth_url,
            "state": state_token,
            "connection_id": connection_id,
            "code_verifier": code_verifier,  # Store for validation (if needed)
        }

    def handle_callback(
        self,
        session: Session,
        connector_slug: str,
        user_id: uuid.UUID,
        connection_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Handle OAuth callback and retrieve tokens from Nango.

        Args:
            session: Database session
            connector_slug: Connector slug
            user_id: User ID
            connection_id: Nango connection ID (if not provided, constructs from user_id and slug)

        Returns:
            Dictionary with authorization result including tokens

        Raises:
            NangoError: If token retrieval fails
        """
        if not self.enabled:
            NangoError = _get_nango_error()
            raise NangoError("Nango integration is not enabled or configured")

        # Get connector
        try:
            from app.connectors.registry import ConnectorNotFoundError

            connector_version = self._get_registry().get_connector(
                session, connector_slug
            )
        except ConnectorNotFoundError:
            NangoError = _get_nango_error()
            raise NangoError(f"Connector '{connector_slug}' not found")

        # Get Nango provider key
        manifest = connector_version.manifest
        nango_config = manifest.get("nango", {})
        provider_key = nango_config.get("provider_key", connector_slug)

        # Construct connection_id if not provided
        if not connection_id:
            connection_id = f"{user_id}_{connector_slug}"

        # Retrieve connection/tokens from Nango
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(
                    f"{self.base_url}/connection/{connection_id}",
                    headers=self._get_headers(),
                )
                response.raise_for_status()
                connection_data = response.json()

                # Extract tokens from Nango response
                # Nango returns connection data with credentials
                credentials = connection_data.get("credentials", {})

                tokens = {
                    "access_token": credentials.get("access_token"),
                    "refresh_token": credentials.get("refresh_token"),
                    "expires_at": credentials.get("expires_at"),
                    "token_type": credentials.get("token_type", "Bearer"),
                }

                # Calculate expires_in if expires_at is provided
                if tokens.get("expires_at"):
                    from datetime import datetime

                    try:
                        expires_at = datetime.fromisoformat(
                            tokens["expires_at"].replace("Z", "+00:00")
                        )
                        expires_in = int(
                            (
                                expires_at - datetime.utcnow().replace(tzinfo=None)
                            ).total_seconds()
                        )
                        tokens["expires_in"] = max(0, expires_in)
                    except (ValueError, AttributeError):
                        # If parsing fails, set a default or skip
                        tokens["expires_in"] = None

                return {
                    "success": True,
                    "connector_slug": connector_slug,
                    "user_id": str(user_id),
                    "connection_id": connection_id,
                    "tokens": tokens,
                }
        except httpx.HTTPStatusError as e:
            NangoError = _get_nango_error()
            if e.response.status_code == 404:
                raise NangoError(f"Connection '{connection_id}' not found in Nango")
            raise NangoError(
                f"Failed to retrieve connection from Nango: {e.response.text}"
            )
        except httpx.HTTPError as e:
            NangoError = _get_nango_error()
            raise NangoError(f"Failed to retrieve connection from Nango: {e}")

    def get_tokens(
        self,
        connector_slug: str,
        user_id: uuid.UUID,
        connection_id: str | None = None,
    ) -> dict[str, Any] | None:
        """
        Retrieve OAuth tokens from Nango.

        Args:
            connector_slug: Connector slug
            user_id: User ID
            connection_id: Nango connection ID (optional)

        Returns:
            Token dictionary or None if not found
        """
        if not self.enabled:
            return None

        try:
            # Get connector to find provider key
            connector_version = self._get_registry().get_connector(
                session=None,  # We don't need DB for this
                slug=connector_slug,
            )
            manifest = connector_version.manifest
            nango_config = manifest.get("nango", {})

            if not nango_config.get("enabled", False):
                return None

            if not connection_id:
                connection_id = f"{user_id}_{connector_slug}"

            with httpx.Client(timeout=30.0) as client:
                response = client.get(
                    f"{self.base_url}/connection/{connection_id}",
                    headers=self._get_headers(),
                )
                response.raise_for_status()
                connection_data = response.json()

                credentials = connection_data.get("credentials", {})
                if not credentials.get("access_token"):
                    return None

                return {
                    "access_token": credentials.get("access_token"),
                    "refresh_token": credentials.get("refresh_token"),
                    "expires_at": credentials.get("expires_at"),
                    "token_type": credentials.get("token_type", "Bearer"),
                }
        except Exception:
            return None

    def refresh_tokens(
        self,
        connector_slug: str,
        user_id: uuid.UUID,
        connection_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Refresh OAuth tokens via Nango.

        Args:
            connector_slug: Connector slug
            user_id: User ID
            connection_id: Nango connection ID (optional)

        Returns:
            New token dictionary

        Raises:
            NangoError: If refresh fails
        """
        if not self.enabled:
            NangoError = _get_nango_error()
            raise NangoError("Nango integration is not enabled or configured")

        try:
            connector_version = self._get_registry().get_connector(
                session=None,
                slug=connector_slug,
            )
            manifest = connector_version.manifest
            nango_config = manifest.get("nango", {})
            provider_key = nango_config.get("provider_key", connector_slug)

            if not connection_id:
                connection_id = f"{user_id}_{connector_slug}"

            # Nango automatically refreshes tokens, but we can trigger a refresh
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    f"{self.base_url}/connection/{connection_id}/refresh",
                    headers=self._get_headers(),
                )
                response.raise_for_status()
                connection_data = response.json()

                credentials = connection_data.get("credentials", {})
                return {
                    "access_token": credentials.get("access_token"),
                    "refresh_token": credentials.get("refresh_token"),
                    "expires_at": credentials.get("expires_at"),
                    "token_type": credentials.get("token_type", "Bearer"),
                }
        except httpx.HTTPStatusError as e:
            NangoError = _get_nango_error()
            if e.response.status_code == 404:
                raise NangoError(f"Connection '{connection_id}' not found in Nango")
            raise NangoError(f"Failed to refresh tokens via Nango: {e.response.text}")
        except httpx.HTTPError as e:
            NangoError = _get_nango_error()
            raise NangoError(f"Failed to refresh tokens via Nango: {e}")


# Default Nango service instance (lazy initialization to avoid startup errors)
# Only create if Nango is enabled and configured
_default_nango_service: NangoService | None = None


def _create_nango_service() -> NangoService | None:
    """Create Nango service instance if configured."""
    try:
        # Use NANGO_BASE_URL if available, fallback to NANGO_URL for backward compatibility
        base_url = getattr(settings, "NANGO_BASE_URL", None) or getattr(
            settings, "NANGO_URL", None
        )
        secret_key = getattr(settings, "NANGO_SECRET_KEY", "")
        enabled = getattr(settings, "NANGO_ENABLED", True)

        if enabled and base_url and secret_key:
            return NangoService()
    except Exception:
        # If initialization fails, return None (Nango not available)
        pass
    return None


def get_default_nango_service() -> NangoService | None:
    """Get or create default Nango service instance."""
    global _default_nango_service
    if _default_nango_service is None:
        _default_nango_service = _create_nango_service()
    return _default_nango_service


# For backward compatibility, create a proxy object that handles None gracefully
class _DefaultNangoService:
    """Wrapper to maintain backward compatibility with existing code."""

    def __getattr__(self, name):
        # Lazy import to avoid circular dependency
        from app.services.exceptions import NangoError

        service = get_default_nango_service()
        if service is None:
            NangoError = _get_nango_error()
            raise NangoError(
                "Nango service is not configured. Set NANGO_SECRET_KEY and NANGO_BASE_URL environment variables."
            )
        return getattr(service, name)


# Create a proxy that lazily initializes to avoid circular imports
class _DefaultNangoServiceProxy:
    """Proxy for default_nango_service to avoid circular imports."""

    _instance: _DefaultNangoService | None = None

    def __getattr__(self, name):
        if self._instance is None:
            self._instance = _DefaultNangoService()
        return getattr(self._instance, name)


# Export proxy instead of direct instance
default_nango_service = _DefaultNangoServiceProxy()
