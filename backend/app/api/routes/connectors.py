"""
Connector API Routes

Endpoints for connector registration, discovery, and management.
"""

import logging
from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, status
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.connectors.loader import (
    ConnectorLoaderError,
    MethodNotFoundError,
    default_connector_loader,
)
from app.connectors.oauth import (
    InvalidOAuthStateError,
    OAuthError,
    OAuthTokenError,
    default_oauth_service,
)
from app.connectors.registry import (
    ConnectorNotFoundError,
    ConnectorRegistryError,
    InvalidManifestError,
    default_connector_registry,
)
from app.connectors.webhook import (
    InvalidWebhookSignatureError,
    WebhookError,
    WebhookNotFoundError,
    default_webhook_service,
)
from app.core.config import settings
from app.models import Connector, ConnectorVersion, UserConnectorConnection
from app.services.nango_service import get_nango_service

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/connectors", tags=["connectors"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_connector(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    manifest: dict[str, Any],
    wheel_url: str | None = None,
    is_platform: bool = False,
) -> Any:
    """
    Register a new connector version (user custom connector).

    This endpoint is for users to register their own custom connectors.
    Platform connectors should be registered via /admin/connectors/register.

    Requires:
    - Valid connector manifest
    - Optional wheel file URL

    Query Parameters:
    - is_platform: Must be False (users cannot register platform connectors)

    Returns:
    - ConnectorVersion details
    """
    # Users cannot register platform connectors via this endpoint
    if is_platform:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can register platform connectors. Use /admin/connectors/register",
        )

    registry = default_connector_registry

    try:
        connector_version = registry.register_connector(
            session=session,
            manifest=manifest,
            wheel_url=wheel_url,
            owner_id=current_user.id,
            is_platform=False,
            created_by=current_user.id,
        )

        return {
            "id": str(connector_version.id),
            "connector_id": str(connector_version.connector_id),
            "version": connector_version.version,
            "slug": manifest.get("slug"),
            "name": manifest.get("name"),
            "is_platform": False,
            "owner_id": str(current_user.id),
            "created_at": connector_version.created_at.isoformat(),
        }
    except InvalidManifestError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid manifest: {str(e)}",
        )
    except ConnectorRegistryError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/list")
def list_connectors(
    session: SessionDep,
    current_user: CurrentUser,
    status_filter: str | None = None,
    category: str | None = None,
    include_custom: bool = True,
) -> Any:
    """
    List available connectors for the current user.

    Returns:
    - Platform connectors (available to all users)
    - User's custom connectors (if include_custom=True)

    Query Parameters:
    - status_filter: Optional filter by status (draft, beta, stable, deprecated)
    - category: Optional filter by category (e.g., "Communication & Collaboration")
    - include_custom: Include user's custom connectors (default: True)

    Returns:
    - List of connectors with metadata including Nango status and category
    """
    registry = default_connector_registry

    connectors = registry.list_connectors(
        session=session,
        status=status_filter,
        include_user_connectors=include_custom,
        user_id=current_user.id,
    )

    # Optimize: Load all versions in a single query to avoid N+1
    connector_ids = [c.id for c in connectors]
    latest_version_ids = [
        c.latest_version_id for c in connectors if c.latest_version_id
    ]

    # Bulk load all versions in one query
    versions_map = {}
    if latest_version_ids:
        versions = session.exec(
            select(ConnectorVersion).where(ConnectorVersion.id.in_(latest_version_ids))
        ).all()
        versions_map = {v.id: v for v in versions}

    result = []
    for connector in connectors:
        # Get latest version from pre-loaded map
        latest_version = None
        if connector.latest_version_id:
            latest_version = versions_map.get(connector.latest_version_id)

        # Extract metadata from manifest
        manifest = latest_version.manifest if latest_version else {}
        nango_config = manifest.get("nango", {})
        nango_enabled = nango_config.get("enabled", False)
        connector_category = manifest.get("category", "Uncategorized")
        description = manifest.get("description", "")

        # Filter by category if specified
        if category and connector_category != category:
            continue

        result.append(
            {
                "id": str(connector.id),
                "slug": connector.slug,
                "name": connector.name,
                "status": connector.status,
                "category": connector_category,
                "description": description,
                "latest_version": latest_version.version if latest_version else None,
                "is_platform": connector.is_platform,
                "owner_id": str(connector.owner_id) if connector.owner_id else None,
                "nango_enabled": nango_enabled,
                "nango_provider_key": nango_config.get("provider_key")
                if nango_enabled
                else None,
                "created_at": connector.created_at.isoformat(),
            }
        )

    return {
        "connectors": result,
        "total_count": len(result),
    }


@router.get("/{slug}")
def get_connector(
    slug: str,
    session: SessionDep,
    current_user: CurrentUser,
    version: str | None = None,
) -> Any:
    """
    Get connector details.

    Path Parameters:
    - slug: Connector slug

    Query Parameters:
    - version: Optional version string (uses latest if not specified)

    Returns:
    - Connector details with manifest
    """
    registry = default_connector_registry

    try:
        connector_version = registry.get_connector(
            session=session,
            slug=slug,
            version=version,
        )

        connector = session.get(Connector, connector_version.connector_id)

        return {
            "id": str(connector_version.id),
            "connector_id": str(connector_version.connector_id),
            "slug": connector.slug if connector else slug,
            "name": connector.name
            if connector
            else connector_version.manifest.get("name"),
            "status": connector.status if connector else "unknown",
            "version": connector_version.version,
            "manifest": connector_version.manifest,
            "wheel_url": connector_version.wheel_url,
            "created_at": connector_version.created_at.isoformat(),
        }
    except ConnectorNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/{slug}/actions")
def get_connector_actions(
    slug: str,
    session: SessionDep,
    current_user: CurrentUser,
    version: str | None = None,
) -> Any:
    """
    Get available actions for a connector.

    Path Parameters:
    - slug: Connector slug

    Query Parameters:
    - version: Optional version string (uses latest if not specified)

    Returns:
    - Dictionary of action_id -> action_config
    """
    registry = default_connector_registry

    try:
        actions = registry.get_connector_actions(
            session=session,
            slug=slug,
            version=version,
        )
        return {"actions": actions}
    except ConnectorNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/{slug}/triggers")
def get_connector_triggers(
    slug: str,
    session: SessionDep,
    current_user: CurrentUser,
    version: str | None = None,
) -> Any:
    """
    Get available triggers for a connector.

    Path Parameters:
    - slug: Connector slug

    Query Parameters:
    - version: Optional version string (uses latest if not specified)

    Returns:
    - Dictionary of trigger_id -> trigger_config
    """
    registry = default_connector_registry

    try:
        triggers = registry.get_connector_triggers(
            session=session,
            slug=slug,
            version=version,
        )
        return {"triggers": triggers}
    except ConnectorNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.patch("/{slug}/status")
def update_connector_status(
    slug: str,
    session: SessionDep,
    current_user: CurrentUser,
    new_status: str,
) -> Any:
    """
    Update connector status.

    Path Parameters:
    - slug: Connector slug

    Request Body:
    - new_status: New status (draft, beta, stable, deprecated)

    Returns:
    - Updated connector details
    """
    # TODO: Add authorization check (only superusers can update status)

    registry = default_connector_registry

    try:
        connector = registry.update_connector_status(
            session=session,
            slug=slug,
            status=new_status,
        )

        return {
            "id": str(connector.id),
            "slug": connector.slug,
            "name": connector.name,
            "status": connector.status,
            "updated_at": connector.created_at.isoformat(),  # TODO: Add updated_at field
        }
    except ConnectorNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except ConnectorRegistryError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{slug}/versions")
def list_connector_versions(
    slug: str,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    List all versions of a connector.

    Path Parameters:
    - slug: Connector slug

    Returns:
    - List of connector versions
    """
    connector = session.exec(select(Connector).where(Connector.slug == slug)).first()

    if not connector:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connector '{slug}' not found",
        )

    versions = session.exec(
        select(ConnectorVersion)
        .where(ConnectorVersion.connector_id == connector.id)
        .order_by(ConnectorVersion.created_at.desc())
    ).all()

    return [
        {
            "id": str(version.id),
            "version": version.version,
            "created_at": version.created_at.isoformat(),
            "is_latest": version.id == connector.latest_version_id,
        }
        for version in versions
    ]


@router.post("/{slug}/authorize")
def authorize_connector(
    slug: str,
    session: SessionDep,
    current_user: CurrentUser,
    redirect_uri: str,
    scopes: list[str] | None = None,
) -> Any:
    """
    Initiate OAuth authorization flow for a connector.

    Supports both Nango and direct OAuth flows.

    Path Parameters:
    - slug: Connector slug

    Request Body:
    - redirect_uri: OAuth callback redirect URI
    - scopes: Optional list of OAuth scopes

    Returns:
    - Authorization URL and state token
    - oauth_method: "nango" or "direct" indicating which method is used
    """
    oauth_service = default_oauth_service

    try:
        # Check if connector uses Nango
        connector_version = default_connector_registry.get_connector(session, slug)
        manifest = connector_version.manifest
        nango_config = manifest.get("nango", {})
        use_nango = settings.NANGO_ENABLED and nango_config.get("enabled", False)

        result = oauth_service.generate_authorization_url(
            session=session,
            connector_slug=slug,
            user_id=current_user.id,
            redirect_uri=redirect_uri,
            scopes=scopes,
        )

        # Add OAuth method indicator
        result["oauth_method"] = "nango" if use_nango else "direct"

        return result
    except ConnectorNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except OAuthError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{slug}/callback")
def oauth_callback(
    slug: str,
    session: SessionDep,
    current_user: CurrentUser,
    state: str,
    code: str | None = None,
    error: str | None = None,
) -> Any:
    """
    Handle OAuth callback and exchange code for tokens.

    Supports both Nango and direct OAuth flows.

    Path Parameters:
    - slug: Connector slug

    Query Parameters:
    - state: OAuth state token
    - code: Authorization code (if successful, for direct OAuth)
    - error: Error message (if failed)

    Returns:
    - Authorization result with oauth_method indicator
    """
    oauth_service = default_oauth_service

    try:
        # Check if connector uses Nango (from state or connector manifest)
        connector_version = default_connector_registry.get_connector(session, slug)
        manifest = connector_version.manifest
        nango_config = manifest.get("nango", {})
        use_nango = settings.NANGO_ENABLED and nango_config.get("enabled", False)

        result = oauth_service.handle_callback(
            session=session,
            state=state,
            code=code,
            error=error,
        )

        # Add OAuth method indicator
        result["oauth_method"] = "nango" if use_nango else "direct"

        return result
    except InvalidOAuthStateError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except (OAuthError, OAuthTokenError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/{slug}/refresh")
def refresh_connector_tokens(
    slug: str,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Refresh OAuth tokens for a connector.

    Supports both Nango and direct OAuth refresh.

    Path Parameters:
    - slug: Connector slug

    Returns:
    - New token information with oauth_method indicator
    """
    oauth_service = default_oauth_service

    try:
        # Check if connector uses Nango
        connector_version = default_connector_registry.get_connector(session, slug)
        manifest = connector_version.manifest
        nango_config = manifest.get("nango", {})
        use_nango = settings.NANGO_ENABLED and nango_config.get("enabled", False)

        tokens = oauth_service.refresh_tokens(
            session=session,
            connector_slug=slug,
            user_id=current_user.id,
        )
        return {
            "success": True,
            "connector_slug": slug,
            "expires_in": tokens.get("expires_in"),
            "oauth_method": "nango" if use_nango else "direct",
        }
    except OAuthTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except ConnectorNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/{slug}/auth-status")
def get_connector_auth_status(
    slug: str,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Check if connector is authorized for the current user.

    Path Parameters:
    - slug: Connector slug

    Returns:
    - Authorization status with token expiration info
    """
    oauth_service = default_oauth_service

    try:
        # Check if connector exists
        connector_version = default_connector_registry.get_connector(session, slug)

        # Check if connector requires OAuth
        manifest = connector_version.manifest
        oauth_config = manifest.get("oauth", {})

        if not oauth_config:
            return {
                "authorized": False,
                "requires_oauth": False,
                "message": "Connector does not require OAuth authorization",
            }

        # Get tokens for this user
        tokens = oauth_service.get_tokens(
            connector_slug=slug,
            user_id=current_user.id,
        )

        if not tokens:
            return {
                "authorized": False,
                "requires_oauth": True,
                "expires_at": None,
                "token_type": None,
            }

        # Calculate expiration info
        expires_at = tokens.get("expires_at")
        expires_in = None
        if expires_at:
            from datetime import datetime

            try:
                expires_at_dt = datetime.fromisoformat(
                    expires_at.replace("Z", "+00:00")
                )
                expires_in = int(
                    (
                        expires_at_dt - datetime.utcnow().replace(tzinfo=None)
                    ).total_seconds()
                )
            except (ValueError, AttributeError):
                pass

        return {
            "authorized": True,
            "requires_oauth": True,
            "expires_at": expires_at,
            "expires_in": expires_in,
            "token_type": tokens.get("token_type", "Bearer"),
        }
    except ConnectorNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete("/{slug}/authorization")
def revoke_connector_authorization(
    slug: str,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Revoke OAuth authorization for a connector.

    Path Parameters:
    - slug: Connector slug

    Returns:
    - Success status
    """
    oauth_service = default_oauth_service

    try:
        # Check if connector exists
        connector_version = default_connector_registry.get_connector(session, slug)

        # Check if connector requires OAuth
        manifest = connector_version.manifest
        oauth_config = manifest.get("oauth", {})

        if not oauth_config:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Connector '{slug}' does not require OAuth authorization",
            )

        # Revoke tokens
        # Note: This depends on how tokens are stored (Nango vs direct)
        # For now, we'll delete from secrets service
        from app.services.secrets import default_secrets_service

        # Delete tokens from secrets service
        secret_key = f"connector:{slug}:user:{current_user.id}:oauth_tokens"
        try:
            default_secrets_service.delete_secret(secret_key)
        except Exception:
            # If secret doesn't exist, that's fine
            pass

        # If using Nango, we might need to delete the connection
        # This would require Nango API call to delete connection

        return {
            "success": True,
            "message": f"Authorization revoked for connector '{slug}'",
        }
    except ConnectorNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post("/{slug}/{action}")
def invoke_connector_action(
    slug: str,
    action: str,
    session: SessionDep,
    current_user: CurrentUser,
    input_data: dict[str, Any],
    version: str | None = None,
) -> Any:
    """
    Invoke a connector action.

    Path Parameters:
    - slug: Connector slug
    - action: Action ID from connector manifest

    Query Parameters:
    - version: Optional connector version (uses latest if not specified)

    Request Body:
    - input_data: Action input data

    Returns:
    - Action output data
    """
    registry = default_connector_registry
    loader = default_connector_loader
    oauth_service = default_oauth_service

    try:
        # Get connector version
        connector_version = registry.get_connector(
            session=session,
            slug=slug,
            version=version,
        )

        # Verify action exists
        actions = registry.get_connector_actions(
            session=session,
            slug=slug,
            version=version,
        )

        if action not in actions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Action '{action}' not found in connector '{slug}'",
            )

        # Get OAuth tokens if connector requires OAuth
        credentials = None
        manifest = connector_version.manifest
        oauth_config = manifest.get("oauth", {})

        if oauth_config:
            # Connector requires OAuth, get tokens
            tokens = oauth_service.get_tokens(
                connector_slug=slug,
                user_id=current_user.id,
            )

            if not tokens:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Connector '{slug}' requires OAuth authorization. Please authorize first.",
                )

            # Prepare credentials dictionary
            credentials = {
                "access_token": tokens.get("access_token"),
                "refresh_token": tokens.get("refresh_token"),
                "token_type": tokens.get("token_type", "Bearer"),
            }

            # Add any additional credential fields from manifest
            credential_fields = oauth_config.get("credential_fields", {})
            for field_name, field_config in credential_fields.items():
                if field_config.get("source") == "infisical":
                    # Get from Infisical
                    secret_key = field_config.get(
                        "secret_key",
                        f"connector_{slug}_user_{current_user.id}_{field_name}",
                    )
                    try:
                        from app.services.secrets import default_secrets_service

                        value = default_secrets_service.get_secret(
                            secret_key=secret_key,
                            environment="prod",
                            path=f"/connectors/{slug}/users/{current_user.id}",
                        )
                        credentials[field_name] = value
                    except Exception:
                        # Field not found, skip
                        pass

        # Invoke connector action
        try:
            result = loader.invoke_action(
                connector_version=connector_version,
                action_id=action,
                input_data=input_data,
                credentials=credentials,
            )

            return {
                "success": True,
                "connector_slug": slug,
                "action": action,
                "result": result,
            }
        except MethodNotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            )
        except ConnectorLoaderError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to invoke connector action: {str(e)}",
            )

    except ConnectorNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post("/{slug}/rotate", status_code=status.HTTP_200_OK)
def rotate_connector_credentials(
    slug: str,
    session: SessionDep,
    current_user: CurrentUser,
    credential_type: str | None = None,  # "oauth" or "api_key" or None (all)
) -> Any:
    """
    Rotate connector credentials.

    For OAuth connectors, refreshes the access token.
    For API key connectors, rotates the API key (if supported).

    Path Parameters:
    - slug: Connector slug

    Query Parameters:
    - credential_type: Type of credential to rotate ("oauth", "api_key", or None for all)

    Returns:
    - Rotation result with status
    """
    registry = default_connector_registry
    oauth_service = default_oauth_service

    try:
        # Get connector
        connector_version = registry.get_connector(
            session=session,
            slug=slug,
        )

        manifest = connector_version.manifest
        oauth_config = manifest.get("oauth", {})

        if not oauth_config and credential_type == "oauth":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Connector '{slug}' does not support OAuth",
            )

        rotation_results = {}

        # Rotate OAuth tokens if applicable
        if not credential_type or credential_type == "oauth":
            if oauth_config:
                try:
                    # Try to refresh the token (this will get a new access token)
                    tokens = oauth_service.refresh_tokens(
                        session=session,
                        connector_slug=slug,
                        user_id=current_user.id,
                    )

                    if tokens:
                        rotation_results["oauth"] = {
                            "status": "rotated",
                            "message": "OAuth tokens refreshed successfully",
                        }
                    else:
                        rotation_results["oauth"] = {
                            "status": "skipped",
                            "message": "No existing tokens to rotate",
                        }
                except Exception as e:
                    rotation_results["oauth"] = {
                        "status": "failed",
                        "message": f"Failed to rotate OAuth tokens: {str(e)}",
                    }

        # Rotate API keys if applicable
        if not credential_type or credential_type == "api_key":
            credential_fields = oauth_config.get("credential_fields", {})
            api_key_fields = {
                k: v
                for k, v in credential_fields.items()
                if v.get("type") == "api_key" or "api_key" in k.lower()
            }

            if api_key_fields:
                for field_name, field_config in api_key_fields.items():
                    secret_key = field_config.get(
                        "secret_key",
                        f"connector_{slug}_user_{current_user.id}_{field_name}",
                    )
                    path = f"/connectors/{slug}/users/{current_user.id}"

                    try:
                        # For API keys, we would typically generate a new key
                        # For now, we'll just mark it as rotated (actual rotation depends on connector)
                        rotation_results[field_name] = {
                            "status": "rotated",
                            "message": f"API key '{field_name}' marked for rotation",
                            "note": "Please regenerate the API key in the connector's dashboard",
                        }
                    except Exception as e:
                        rotation_results[field_name] = {
                            "status": "failed",
                            "message": f"Failed to rotate API key '{field_name}': {str(e)}",
                        }

        if not rotation_results:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No credentials found to rotate for connector '{slug}'",
            )

        return {
            "connector_slug": slug,
            "rotation_results": rotation_results,
            "rotated_at": datetime.utcnow().isoformat(),
        }

    except ConnectorNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to rotate credentials: {str(e)}",
        )


@router.post("/{slug}/webhook")
def webhook_ingress(
    slug: str,
    session: SessionDep,
    payload: dict[str, Any],
    trigger_id: str,
    x_hub_signature_256: str | None = Header(None, alias="X-Hub-Signature-256"),
    x_signature: str | None = Header(None, alias="X-Signature"),
) -> Any:
    """
    Webhook ingress endpoint for connector webhooks.

    Validates webhook signature, maps payload, and emits workflow signals.

    Path Parameters:
    - slug: Connector slug

    Query Parameters:
    - trigger_id: Trigger ID from connector manifest

    Headers:
    - X-Hub-Signature-256: Webhook signature (GitHub-style)
    - X-Signature: Generic webhook signature

    Request Body:
    - payload: Webhook payload (JSON)

    Returns:
    - Webhook processing result
    """
    webhook_service = default_webhook_service

    # Get signature from headers (try multiple common header names)
    signature = x_hub_signature_256 or x_signature

    # If signature is in format "sha256=...", extract just the hash
    if signature and "=" in signature:
        signature = signature.split("=", 1)[1]

    try:
        result = webhook_service.process_webhook(
            session=session,
            connector_slug=slug,
            trigger_id=trigger_id,
            payload=payload,
            signature=signature,
        )
        return result
    except WebhookNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except InvalidWebhookSignatureError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except ConnectorNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except WebhookError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# ============================================================================
# Nango OAuth Connection Endpoints
# ============================================================================


@router.post("/{connector_id}/connect")
async def connect_connector(
    connector_id: str,
    current_user: CurrentUser,
    session: SessionDep,
    instance_id: str | None = None,
) -> Any:
    """
    Initiate OAuth connection to a connector via Nango.
    Opens popup window with Nango OAuth URL.

    Path Parameters:
    - connector_id: Connector UUID or slug

    Query Parameters:
    - instance_id: Optional instance identifier for multiple accounts (e.g., "work@gmail.com")

    Returns:
    - oauth_url: URL to open in popup window
    - connection_id: Connection identifier for tracking
    - popup: Boolean indicating popup should be used
    """
    if not settings.NANGO_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Nango integration is not enabled",
        )

    # Get connector (try by ID first, then by slug)
    try:
        connector_uuid = UUID(connector_id)
        connector = session.get(Connector, connector_uuid)
    except ValueError:
        # Not a UUID, try by slug
        connector = session.exec(
            select(Connector).where(Connector.slug == connector_id)
        ).first()

    if not connector:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connector '{connector_id}' not found",
        )

    # Get connector version to check Nango config
    connector_version = session.get(ConnectorVersion, connector.latest_version_id)
    if not connector_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connector version not found for '{connector.slug}'",
        )

    manifest = connector_version.manifest
    nango_config = manifest.get("nango", {})

    if not nango_config.get("enabled", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Connector '{connector.slug}' does not support Nango OAuth",
        )

    provider_key = nango_config.get("provider_key", connector.slug)

    # Generate connection ID
    connection_id = f"{current_user.id}_{connector.id}"
    if instance_id:
        connection_id += f"_{instance_id}"

    # Check if connection already exists
    existing = session.exec(
        select(UserConnectorConnection).where(
            UserConnectorConnection.user_id == current_user.id,
            UserConnectorConnection.connector_id == connector.id,
            UserConnectorConnection.nango_connection_id == connection_id,
        )
    ).first()

    if existing and existing.status == "connected":
        # Return existing connection info
        return {
            "oauth_url": None,
            "connection_id": str(existing.id),
            "popup": False,
            "already_connected": True,
            "message": "Already connected",
        }

    # Create or update connection record
    if existing:
        connection = existing
        connection.status = "pending"
    else:
        connection = UserConnectorConnection(
            user_id=current_user.id,
            connector_id=connector.id,
            nango_connection_id=connection_id,
            status="pending",
            config={"instance_id": instance_id} if instance_id else None,
        )
        session.add(connection)

    session.commit()

    # Get OAuth URL from Nango
    return_url = (
        f"{settings.FRONTEND_HOST}/connectors/callback?connection_id={connection_id}"
    )

    try:
        nango_service = get_nango_service()
        oauth_data = await nango_service.create_connection(
            user_id=str(current_user.id),
            connector_slug=connector.slug,
            connection_id=connection_id,
            return_url=return_url,
            provider_key=provider_key,
        )

        # Track connector connection initiation in PostHog
        from app.observability.posthog import default_posthog_client

        default_posthog_client.capture(
            distinct_id=str(current_user.id),
            event="connector_connection_initiated",
            properties={
                "connector_id": str(connector.id),
                "connector_slug": connector.slug,
                "connection_id": str(connection.id),
                "has_instance_id": bool(instance_id),
            },
        )

        return {
            "oauth_url": oauth_data["oauth_url"],
            "connection_id": str(connection.id),
            "nango_connection_id": connection_id,
            "popup": True,
            "already_connected": False,
        }
    except Exception as e:
        connection.status = "error"
        connection.last_error = str(e)
        connection.error_count += 1
        session.commit()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initiate OAuth connection: {str(e)}",
        )


@router.get("/callback")
async def nango_oauth_callback(
    connection_id: str,
    session: SessionDep,
    provider_config_key: str | None = None,
) -> Any:
    """
    Handle OAuth callback from Nango.
    Called by Nango after successful OAuth.
    Updates connection status in database.

    Query Parameters:
    - connection_id: Nango connection identifier
    - provider_config_key: Nango provider key (optional)

    Returns:
    - Success message with connection details
    """
    # Find connection by nango_connection_id
    connection = session.exec(
        select(UserConnectorConnection).where(
            UserConnectorConnection.nango_connection_id == connection_id
        )
    ).first()

    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connection '{connection_id}' not found",
        )

    # Verify connection status with Nango
    try:
        connector = session.get(Connector, connection.connector_id)
        connector_version = session.get(ConnectorVersion, connector.latest_version_id)
        manifest = connector_version.manifest
        nango_config = manifest.get("nango", {})
        provider_key = provider_config_key or nango_config.get(
            "provider_key", connector.slug
        )

        nango_service = get_nango_service()
        # Verify connection exists in Nango
        nango_status = await nango_service.get_connection_status(
            connection_id=connection_id, provider_key=provider_key
        )

        # Update connection status
        connection.status = "connected"
        connection.connected_at = datetime.utcnow()
        connection.last_synced_at = datetime.utcnow()
        connection.last_error = None
        connection.error_count = 0
        session.commit()

        # Track successful connector connection in PostHog
        from app.observability.posthog import default_posthog_client

        default_posthog_client.capture(
            distinct_id=str(connection.user_id),
            event="connector_connected",
            properties={
                "connector_id": str(connection.connector_id),
                "connector_slug": connector.slug,
                "connection_id": str(connection.id),
            },
        )

        return {
            "success": True,
            "connection_id": str(connection.id),
            "nango_connection_id": connection_id,
            "connector_id": str(connection.connector_id),
            "connector_slug": connector.slug,
            "status": "connected",
            "message": "Successfully connected",
        }
    except Exception as e:
        connection.status = "error"
        connection.last_error = str(e)
        connection.error_count += 1
        session.commit()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify connection: {str(e)}",
        )


@router.get("/connections")
def list_connections(
    current_user: CurrentUser,
    session: SessionDep,
    connector_id: str | None = None,
) -> Any:
    """
    List all user's connector connections.

    Query Parameters:
    - connector_id: Optional filter by connector ID or slug

    Returns:
    - List of connections with status and metadata
    """
    query = select(UserConnectorConnection).where(
        UserConnectorConnection.user_id == current_user.id
    )

    if connector_id:
        try:
            connector_uuid = UUID(connector_id)
            query = query.where(UserConnectorConnection.connector_id == connector_uuid)
        except ValueError:
            # Not a UUID, try by slug
            connector = session.exec(
                select(Connector).where(Connector.slug == connector_id)
            ).first()
            if connector:
                query = query.where(
                    UserConnectorConnection.connector_id == connector.id
                )
            else:
                return {"connections": [], "total_count": 0}

    connections = session.exec(query).all()

    # Load connectors in bulk
    connector_ids = {c.connector_id for c in connections}
    connectors_map = {}
    if connector_ids:
        connectors = session.exec(
            select(Connector).where(Connector.id.in_(connector_ids))
        ).all()
        connectors_map = {c.id: c for c in connectors}

    result = []
    for conn in connections:
        connector = connectors_map.get(conn.connector_id)
        result.append(
            {
                "id": str(conn.id),
                "connector_id": str(conn.connector_id),
                "connector_slug": connector.slug if connector else None,
                "connector_name": connector.name if connector else None,
                "nango_connection_id": conn.nango_connection_id,
                "status": conn.status,
                "connected_at": conn.connected_at.isoformat()
                if conn.connected_at
                else None,
                "disconnected_at": conn.disconnected_at.isoformat()
                if conn.disconnected_at
                else None,
                "last_synced_at": conn.last_synced_at.isoformat()
                if conn.last_synced_at
                else None,
                "config": conn.config,
                "error_count": conn.error_count,
                "last_error": conn.last_error,
            }
        )

    return {
        "connections": result,
        "total_count": len(result),
    }


@router.delete("/{connector_id}/disconnect")
async def disconnect_connector(
    connector_id: str,
    connection_id: str,
    current_user: CurrentUser,
    session: SessionDep,
) -> Any:
    """
    Disconnect a connector connection.

    Path Parameters:
    - connector_id: Connector UUID or slug

    Query Parameters:
    - connection_id: Connection UUID to disconnect

    Returns:
    - Success message
    """
    if not settings.NANGO_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Nango integration is not enabled",
        )

    # Get connector
    try:
        connector_uuid = UUID(connector_id)
        connector = session.get(Connector, connector_uuid)
    except ValueError:
        connector = session.exec(
            select(Connector).where(Connector.slug == connector_id)
        ).first()

    if not connector:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Connector '{connector_id}' not found",
        )

    # Get connection
    try:
        connection_uuid = UUID(connection_id)
        connection = session.get(UserConnectorConnection, connection_uuid)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid connection_id format",
        )

    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found",
        )

    if connection.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to disconnect this connection",
        )

    if connection.connector_id != connector.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Connection does not belong to this connector",
        )

    # Delete from Nango
    try:
        connector_version = session.get(ConnectorVersion, connector.latest_version_id)
        manifest = connector_version.manifest
        nango_config = manifest.get("nango", {})
        provider_key = nango_config.get("provider_key", connector.slug)

        nango_service = get_nango_service()
        await nango_service.delete_connection(
            connection_id=connection.nango_connection_id, provider_key=provider_key
        )
    except Exception as e:
        # Log error but continue with database update
        logger.warning(f"Failed to delete connection from Nango: {e}")

    # Update status
    connection.status = "disconnected"
    connection.disconnected_at = datetime.utcnow()
    session.commit()

    # Track connector disconnection in PostHog
    from app.observability.posthog import default_posthog_client

    default_posthog_client.capture(
        distinct_id=str(current_user.id),
        event="connector_disconnected",
        properties={
            "connector_id": str(connector.id),
            "connector_slug": connector.slug,
            "connection_id": str(connection.id),
        },
    )

    return {
        "success": True,
        "message": "Disconnected successfully",
        "connection_id": str(connection.id),
    }
