"""
Connector OAuth Service

Handles OAuth 2.0 flows for connector authentication.
Manages authorization URLs, callbacks, and token storage in Infisical.
"""

import secrets
import uuid
from typing import Any
from urllib.parse import urlencode

import httpx
from sqlmodel import Session

from app.connectors.registry import default_connector_registry
from app.core.config import settings
from app.services.nango import NangoError, default_nango_service
from app.services.secrets import SecretsService, default_secrets_service


class OAuthError(Exception):
    """Base exception for OAuth errors."""

    pass


class InvalidOAuthStateError(OAuthError):
    """Invalid OAuth state."""

    pass


class OAuthTokenError(OAuthError):
    """Failed to exchange OAuth token."""

    pass


class ConnectorOAuthService:
    """
    OAuth service for connector authentication.

    Handles:
    - OAuth authorization URL generation
    - OAuth callback processing
    - Token exchange
    - Token storage in Infisical
    - Token refresh
    """

    def __init__(self, secrets_service: SecretsService | None = None):
        """
        Initialize OAuth service.

        Args:
            secrets_service: SecretsService instance for token storage
        """
        self.secrets_service = secrets_service or default_secrets_service
        self.registry = default_connector_registry
        self.nango_service = default_nango_service
        # In-memory state storage (in production, use Redis or database)
        self._oauth_states: dict[str, dict[str, Any]] = {}

    def generate_authorization_url(
        self,
        session: Session,
        connector_slug: str,
        user_id: uuid.UUID,
        redirect_uri: str,
        scopes: list[str] | None = None,
    ) -> dict[str, str]:
        """
        Generate OAuth authorization URL for a connector.

        Uses Nango if enabled and connector supports it, otherwise falls back to direct OAuth.

        Args:
            session: Database session
            connector_slug: Connector slug
            user_id: User ID requesting authorization
            redirect_uri: Callback redirect URI
            scopes: Optional list of OAuth scopes

        Returns:
            Dictionary with 'authorization_url' and 'state'

        Raises:
            ConnectorNotFoundError: If connector not found
            OAuthError: If OAuth configuration invalid
        """
        # Get connector
        connector_version = self.registry.get_connector(session, connector_slug)
        manifest = connector_version.manifest

        # Check if connector uses Nango
        nango_config = manifest.get("nango", {})
        use_nango = settings.NANGO_ENABLED and nango_config.get("enabled", False)

        if use_nango:
            # Use Nango for OAuth
            try:
                result = self.nango_service.generate_authorization_url(
                    session=session,
                    connector_slug=connector_slug,
                    user_id=user_id,
                    redirect_uri=redirect_uri,
                    scopes=scopes,
                )
                # Store state with Nango connection_id
                state_token = result["state"]
                self._oauth_states[state_token] = {
                    "connector_slug": connector_slug,
                    "connector_version_id": str(connector_version.id),
                    "user_id": str(user_id),
                    "redirect_uri": redirect_uri,
                    "scopes": scopes or [],
                    "use_nango": True,
                    "connection_id": result.get("connection_id"),
                }
                return {
                    "authorization_url": result["authorization_url"],
                    "state": state_token,
                }
            except NangoError as e:
                # Fall back to direct OAuth if Nango fails
                # Log warning but continue with direct OAuth
                import logging

                logger = logging.getLogger(__name__)
                logger.warning(
                    f"Nango OAuth failed for {connector_slug}, falling back to direct OAuth: {e}"
                )

        # Fall back to direct OAuth (existing implementation)
        # Get OAuth configuration from manifest
        oauth_config = manifest.get("oauth", {})
        if not oauth_config:
            raise OAuthError(f"Connector '{connector_slug}' does not support OAuth")

        auth_url = oauth_config.get("authorization_url")
        client_id = oauth_config.get("client_id")

        if not auth_url or not client_id:
            raise OAuthError(
                f"Connector '{connector_slug}' missing OAuth configuration (authorization_url or client_id)"
            )

        # Generate state token for CSRF protection
        state_token = secrets.token_urlsafe(32)

        # Store state with metadata
        self._oauth_states[state_token] = {
            "connector_slug": connector_slug,
            "connector_version_id": str(connector_version.id),
            "user_id": str(user_id),
            "redirect_uri": redirect_uri,
            "scopes": scopes or [],
            "use_nango": False,
        }

        # Build authorization URL
        default_scopes = oauth_config.get("default_scopes", [])
        requested_scopes = scopes or default_scopes
        scope_string = " ".join(requested_scopes)

        params = {
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "state": state_token,
            "scope": scope_string,
        }

        # Add any additional OAuth parameters from manifest
        additional_params = oauth_config.get("authorization_params", {})
        params.update(additional_params)

        authorization_url = f"{auth_url}?{urlencode(params)}"

        return {
            "authorization_url": authorization_url,
            "state": state_token,
        }

    def handle_callback(
        self,
        session: Session,
        state: str,
        code: str | None = None,
        error: str | None = None,
    ) -> dict[str, Any]:
        """
        Handle OAuth callback and exchange code for tokens.

        Supports both Nango and direct OAuth flows.

        Args:
            session: Database session
            state: OAuth state token
            code: Authorization code (if successful, for direct OAuth)
            error: Error message (if failed)

        Returns:
            Dictionary with authorization result

        Raises:
            InvalidOAuthStateError: If state is invalid
            OAuthTokenError: If token exchange fails
        """
        # Validate state
        if state not in self._oauth_states:
            raise InvalidOAuthStateError("Invalid OAuth state token")

        state_data = self._oauth_states[state]
        connector_slug = state_data["connector_slug"]
        user_id = uuid.UUID(state_data["user_id"])
        use_nango = state_data.get("use_nango", False)
        connection_id = state_data.get("connection_id")

        # Check for error in callback
        if error:
            del self._oauth_states[state]
            raise OAuthError(f"OAuth authorization failed: {error}")

        if use_nango:
            # Handle Nango callback
            try:
                result = self.nango_service.handle_callback(
                    session=session,
                    connector_slug=connector_slug,
                    user_id=user_id,
                    connection_id=connection_id,
                )

                # Store tokens in Infisical (for compatibility)
                tokens = result.get("tokens", {})
                self._store_tokens(
                    connector_slug=connector_slug,
                    user_id=user_id,
                    tokens=tokens,
                )

                del self._oauth_states[state]
                return {
                    "success": True,
                    "connector_slug": connector_slug,
                    "user_id": str(user_id),
                    "connection_id": connection_id,
                    "access_token": tokens.get("access_token", "")[:10] + "..."
                    if tokens.get("access_token")
                    else None,
                    "expires_in": tokens.get("expires_in"),
                }
            except NangoError as e:
                del self._oauth_states[state]
                raise OAuthError(f"Nango callback failed: {e}")

        # Direct OAuth flow (existing implementation)
        redirect_uri = state_data["redirect_uri"]

        if not code:
            del self._oauth_states[state]
            raise OAuthError("No authorization code provided")

        # Get connector
        connector_version = self.registry.get_connector(session, connector_slug)
        manifest = connector_version.manifest
        oauth_config = manifest.get("oauth", {})

        # Exchange code for tokens
        tokens = self._exchange_code_for_tokens(
            oauth_config,
            code,
            redirect_uri,
        )

        # Store tokens in Infisical
        self._store_tokens(
            connector_slug=connector_slug,
            user_id=user_id,
            tokens=tokens,
        )

        # Clean up state
        del self._oauth_states[state]

        return {
            "success": True,
            "connector_slug": connector_slug,
            "user_id": str(user_id),
            "access_token": tokens.get("access_token", "")[:10] + "..."
            if tokens.get("access_token")
            else None,
            "expires_in": tokens.get("expires_in"),
        }

    def _exchange_code_for_tokens(
        self,
        oauth_config: dict[str, Any],
        code: str,
        redirect_uri: str,
    ) -> dict[str, Any]:
        """
        Exchange authorization code for access tokens.

        Args:
            oauth_config: OAuth configuration from manifest
            code: Authorization code
            redirect_uri: Redirect URI used in authorization

        Returns:
            Token response dictionary

        Raises:
            OAuthTokenError: If token exchange fails
        """
        token_url = oauth_config.get("token_url")
        client_id = oauth_config.get("client_id")
        client_secret = oauth_config.get("client_secret")

        if not token_url:
            raise OAuthTokenError("Token URL not configured in connector manifest")

        # Prepare token request
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": client_id,
        }

        # Add client secret if provided
        if client_secret:
            data["client_secret"] = client_secret

        # Add any additional token request parameters
        additional_params = oauth_config.get("token_params", {})
        data.update(additional_params)

        # Make token request
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        # Some providers use JSON
        if oauth_config.get("token_request_format") == "json":
            headers = {"Content-Type": "application/json"}

        try:
            with httpx.Client(timeout=30.0) as client:
                if headers["Content-Type"] == "application/json":
                    response = client.post(token_url, json=data, headers=headers)
                else:
                    response = client.post(token_url, data=data, headers=headers)

                response.raise_for_status()
                token_response = response.json()

                return token_response
        except httpx.HTTPError as e:
            raise OAuthTokenError(f"Failed to exchange code for tokens: {e}")
        except Exception as e:
            raise OAuthTokenError(f"Unexpected error during token exchange: {e}")

    def _store_tokens(
        self,
        connector_slug: str,
        user_id: uuid.UUID,
        tokens: dict[str, Any],
    ) -> None:
        """
        Store OAuth tokens in Infisical.

        Args:
            connector_slug: Connector slug
            user_id: User ID
            tokens: Token dictionary
        """
        # Store each token as a separate secret
        # Format: connector_{slug}_user_{user_id}_{token_type}

        access_token = tokens.get("access_token")
        refresh_token = tokens.get("refresh_token")
        expires_in = tokens.get("expires_in")

        if access_token:
            secret_key = f"connector_{connector_slug}_user_{user_id}_access_token"
            self.secrets_service.store_secret(
                secret_key=secret_key,
                secret_value=access_token,
                environment="prod",  # TODO: Make configurable
                path=f"/connectors/{connector_slug}/users/{user_id}",
            )

        if refresh_token:
            secret_key = f"connector_{connector_slug}_user_{user_id}_refresh_token"
            self.secrets_service.store_secret(
                secret_key=secret_key,
                secret_value=refresh_token,
                environment="prod",
                path=f"/connectors/{connector_slug}/users/{user_id}",
            )

        # Store token metadata (expires_in, token_type, etc.)
        if expires_in:
            secret_key = f"connector_{connector_slug}_user_{user_id}_token_metadata"
            metadata = {
                "expires_in": expires_in,
                "token_type": tokens.get("token_type", "Bearer"),
                "scope": tokens.get("scope", ""),
            }
            import json

            self.secrets_service.store_secret(
                secret_key=secret_key,
                secret_value=json.dumps(metadata),
                environment="prod",
                path=f"/connectors/{connector_slug}/users/{user_id}",
            )

    def get_tokens(
        self,
        connector_slug: str,
        user_id: uuid.UUID,
    ) -> dict[str, Any] | None:
        """
        Retrieve OAuth tokens.

        Tries Nango first if enabled, then falls back to Infisical.

        Args:
            connector_slug: Connector slug
            user_id: User ID

        Returns:
            Token dictionary or None if not found
        """
        # Try Nango first
        if self.nango_service.enabled:
            try:
                connector_version = self.registry.get_connector(
                    session=None,
                    slug=connector_slug,
                )
                manifest = connector_version.manifest
                nango_config = manifest.get("nango", {})

                if nango_config.get("enabled", False):
                    tokens = self.nango_service.get_tokens(
                        connector_slug=connector_slug,
                        user_id=user_id,
                    )
                    if tokens:
                        return tokens
            except Exception:
                # Fall back to Infisical
                pass

        # Fall back to Infisical (existing implementation)
        try:
            access_token = self.secrets_service.get_secret(
                secret_key=f"connector_{connector_slug}_user_{user_id}_access_token",
                environment="prod",
                path=f"/connectors/{connector_slug}/users/{user_id}",
            )

            if not access_token:
                return None

            tokens = {
                "access_token": access_token,
            }

            # Try to get refresh token
            try:
                refresh_token = self.secrets_service.get_secret(
                    secret_key=f"connector_{connector_slug}_user_{user_id}_refresh_token",
                    environment="prod",
                    path=f"/connectors/{connector_slug}/users/{user_id}",
                )
                if refresh_token:
                    tokens["refresh_token"] = refresh_token
            except Exception:
                pass

            # Try to get metadata
            try:
                metadata_str = self.secrets_service.get_secret(
                    secret_key=f"connector_{connector_slug}_user_{user_id}_token_metadata",
                    environment="prod",
                    path=f"/connectors/{connector_slug}/users/{user_id}",
                )
                if metadata_str:
                    import json

                    metadata = json.loads(metadata_str)
                    tokens.update(metadata)
            except Exception:
                pass

            return tokens
        except Exception:
            return None

    def refresh_tokens(
        self,
        session: Session,
        connector_slug: str,
        user_id: uuid.UUID,
    ) -> dict[str, Any]:
        """
        Refresh OAuth tokens.

        Uses Nango if enabled, otherwise direct OAuth refresh.

        Args:
            session: Database session
            connector_slug: Connector slug
            user_id: User ID

        Returns:
            New token dictionary

        Raises:
            OAuthTokenError: If refresh fails
        """
        # Try Nango first
        if self.nango_service.enabled:
            try:
                connector_version = self.registry.get_connector(session, connector_slug)
                manifest = connector_version.manifest
                nango_config = manifest.get("nango", {})

                if nango_config.get("enabled", False):
                    tokens = self.nango_service.refresh_tokens(
                        connector_slug=connector_slug,
                        user_id=user_id,
                    )
                    # Store in Infisical for compatibility
                    self._store_tokens(connector_slug, user_id, tokens)
                    return tokens
            except Exception:
                # Fall back to direct OAuth
                pass

        # Direct OAuth refresh (existing implementation)
        # Get current tokens
        tokens = self.get_tokens(connector_slug, user_id)
        if not tokens or "refresh_token" not in tokens:
            raise OAuthTokenError("No refresh token available")

        # Get connector OAuth config
        connector_version = self.registry.get_connector(session, connector_slug)
        manifest = connector_version.manifest
        oauth_config = manifest.get("oauth", {})

        token_url = oauth_config.get("token_url")
        client_id = oauth_config.get("client_id")
        client_secret = oauth_config.get("client_secret")

        if not token_url:
            raise OAuthTokenError("Token URL not configured")

        # Prepare refresh request
        data = {
            "grant_type": "refresh_token",
            "refresh_token": tokens["refresh_token"],
            "client_id": client_id,
        }

        if client_secret:
            data["client_secret"] = client_secret

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        if oauth_config.get("token_request_format") == "json":
            headers = {"Content-Type": "application/json"}

        try:
            with httpx.Client(timeout=30.0) as client:
                if headers["Content-Type"] == "application/json":
                    response = client.post(token_url, json=data, headers=headers)
                else:
                    response = client.post(token_url, data=data, headers=headers)

                response.raise_for_status()
                new_tokens = response.json()

                # Store new tokens
                self._store_tokens(connector_slug, user_id, new_tokens)

                return new_tokens
        except httpx.HTTPError as e:
            raise OAuthTokenError(f"Failed to refresh tokens: {e}")


# Default OAuth service instance
default_oauth_service = ConnectorOAuthService()
