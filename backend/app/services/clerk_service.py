"""
Clerk Authentication Service

Handles Clerk token verification and user management.
"""
import logging
from typing import Any

import jwt
from jwt import PyJWKClient

from app.core.config import settings

logger = logging.getLogger(__name__)

# Try to import Clerk SDK, but make it optional
try:
    from clerk_sdk_python import Clerk

    CLERK_SDK_AVAILABLE = True
except ImportError:
    CLERK_SDK_AVAILABLE = False
    logger.warning("clerk-sdk-python not installed. Using REST API directly.")
    Clerk = None  # type: ignore

# Global Clerk client instance
clerk_client: Any = None
jwks_client: PyJWKClient | None = None


def get_clerk_client() -> Any:
    """Get or create Clerk client instance."""
    global clerk_client
    if clerk_client is None:
        if not settings.CLERK_SECRET_KEY:
            raise ValueError("CLERK_SECRET_KEY not configured")
        if not CLERK_SDK_AVAILABLE or Clerk is None:
            # Fallback: Use REST API directly instead of SDK
            logger.warning("Clerk SDK not available, using REST API directly")
            clerk_client = None  # Will use REST API in verify_clerk_token
        else:
            clerk_client = Clerk(api_key=settings.CLERK_SECRET_KEY)
    return clerk_client


def get_jwks_client() -> PyJWKClient:
    """Get or create JWKS client for token verification."""
    global jwks_client
    if jwks_client is None:
        jwks_url = (
            settings.CLERK_JWKS_URL
            or "https://ethical-hare-79.clerk.accounts.dev/.well-known/jwks.json"
        )
        jwks_client = PyJWKClient(jwks_url)
    return jwks_client


def verify_clerk_token(token: str) -> dict[str, Any]:
    """
    Verify Clerk JWT token and return user information.

    Uses JWKS (JSON Web Key Set) for proper token signature verification.

    Args:
        token: Clerk JWT token

    Returns:
        Dictionary with user information:
        {
            "user_id": str,
            "email": str,
            "email_verified": bool,
            "first_name": str | None,
            "last_name": str | None,
            "full_name": str | None,
            "image_url": str | None,
            "metadata": dict[str, Any],
        }

    Raises:
        ValueError: If token is invalid
    """
    try:
        # Get JWKS client for token verification
        jwks = get_jwks_client()

        # Get the signing key from JWKS
        signing_key = jwks.get_signing_key_from_jwt(token)

        # Verify and decode the token
        # Add leeway for clock skew (60 seconds) to handle "iat" validation issues
        decoded_token = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_iat": True,
            },
            leeway=60,  # 60 seconds leeway for clock skew
        )

        user_id = decoded_token.get("sub")
        if not user_id:
            raise ValueError("Token does not contain user ID (sub)")

        # Get user details from Clerk API for additional info
        # Note: Token already contains basic info, but we fetch from API for complete data
        try:
            clerk = get_clerk_client()
            if clerk is None:
                # Use REST API directly if SDK not available
                import httpx

                headers = {
                    "Authorization": f"Bearer {settings.CLERK_SECRET_KEY}",
                    "Content-Type": "application/json",
                }
                response = httpx.get(
                    f"https://api.clerk.com/v1/users/{user_id}",
                    headers=headers,
                    timeout=10.0,
                )
                response.raise_for_status()
                user_data = response.json()
                # Ensure user_data is a dict
                if not isinstance(user_data, dict):
                    raise ValueError(
                        f"Invalid response format from Clerk API: {type(user_data)}"
                    )
                user = user_data
                logger.info(
                    f"Clerk API response for user {user_id}: keys={list(user.keys())}"
                )
                if "email_addresses" in user:
                    logger.info(
                        f"Email addresses structure: type={type(user['email_addresses'])}, length={len(user['email_addresses']) if isinstance(user['email_addresses'], list) else 'N/A'}"
                    )
                    if (
                        isinstance(user["email_addresses"], list)
                        and len(user["email_addresses"]) > 0
                    ):
                        first_email = user["email_addresses"][0]
                        logger.info(
                            f"First email address: type={type(first_email)}, is_dict={isinstance(first_email, dict)}"
                        )
                        if isinstance(first_email, dict):
                            logger.info(
                                f"First email address keys: {list(first_email.keys())}"
                            )
            else:
                user_obj = clerk.users.get(user_id)
                if user_obj is None:
                    raise ValueError(f"User {user_id} not found in Clerk")
                # Convert Clerk SDK object to dict if needed
                if hasattr(user_obj, "model_dump"):
                    user = user_obj.model_dump()
                elif hasattr(user_obj, "dict"):
                    user = user_obj.dict()
                elif isinstance(user_obj, dict):
                    user = user_obj
                else:
                    # Try to access as object attributes
                    user = {
                        "id": getattr(user_obj, "id", None),
                        "email_addresses": getattr(user_obj, "email_addresses", []),
                        "primary_email_address_id": getattr(
                            user_obj, "primary_email_address_id", None
                        ),
                        "first_name": getattr(user_obj, "first_name", None),
                        "last_name": getattr(user_obj, "last_name", None),
                        "username": getattr(user_obj, "username", None),
                        "image_url": getattr(user_obj, "image_url", None),
                        "public_metadata": getattr(user_obj, "public_metadata", {}),
                    }

            if not user or not isinstance(user, dict):
                raise ValueError(f"User {user_id} not found in Clerk or invalid format")

            # Extract user information from API response
            primary_email = None
            email_verified = False

            # Get primary email address
            email_addresses = user.get("email_addresses", [])
            if email_addresses and isinstance(email_addresses, list):
                for email_obj in email_addresses:
                    if not isinstance(email_obj, dict):
                        continue
                    if email_obj.get("id") == user.get("primary_email_address_id"):
                        primary_email = email_obj.get("email_address")
                        verification = email_obj.get("verification")
                        if isinstance(verification, dict):
                            email_verified = verification.get("status") == "verified"
                        break

                # Fallback to first email if primary not found
                if not primary_email and email_addresses:
                    first_email = email_addresses[0]
                    if isinstance(first_email, dict):
                        primary_email = first_email.get("email_address")
                        verification = first_email.get("verification")
                        if isinstance(verification, dict):
                            email_verified = verification.get("status") == "verified"

            # Fallback to token email if API doesn't have it
            if not primary_email:
                primary_email = decoded_token.get("email")
                email_verified = decoded_token.get("email_verified", False)

            if not primary_email:
                raise ValueError("No email address found for user")

            # Get user names
            first_name = user.get("first_name") or decoded_token.get("first_name")
            last_name = user.get("last_name") or decoded_token.get("last_name")
            full_name = user.get("username") or (
                f"{first_name} {last_name}".strip() if first_name or last_name else None
            )

            return {
                "user_id": user.get("id") or user_id,
                "email": primary_email,
                "email_verified": email_verified,
                "first_name": first_name,
                "last_name": last_name,
                "full_name": full_name,
                "image_url": user.get("image_url"),
                "metadata": user.get("public_metadata", {}),
            }
        except Exception as api_error:
            # If API call fails, use token data as fallback
            logger.warning(
                f"Failed to fetch user from Clerk API, using token data: {str(api_error)}",
                exc_info=True,
            )

            # Extract email from token - Clerk tokens may have email in different fields
            email = decoded_token.get("email")

            # Try alternative email fields in token
            if not email:
                email_addresses = decoded_token.get("email_addresses", [])
                if (
                    email_addresses
                    and isinstance(email_addresses, list)
                    and len(email_addresses) > 0
                ):
                    first_email_obj = email_addresses[0]
                    if isinstance(first_email_obj, dict):
                        email = first_email_obj.get("email_address")
                    elif isinstance(first_email_obj, str):
                        email = first_email_obj

            # If still no email, try to get from primary_email_address_id
            if not email:
                primary_email_id = decoded_token.get("primary_email_address_id")
                if primary_email_id:
                    email_addresses = decoded_token.get("email_addresses", [])
                    if email_addresses:
                        for email_obj in email_addresses:
                            if (
                                isinstance(email_obj, dict)
                                and email_obj.get("id") == primary_email_id
                            ):
                                email = email_obj.get("email_address")
                                break

            if not email:
                # Log the token contents for debugging (without sensitive data)
                logger.error(
                    f"Email not found in Clerk token. Token keys: {list(decoded_token.keys())}"
                )
                raise ValueError(
                    "Email not found in Clerk token and API fetch failed. User must have an email address."
                )

            return {
                "user_id": user_id,
                "email": email,
                "email_verified": decoded_token.get("email_verified", False),
                "first_name": decoded_token.get("first_name"),
                "last_name": decoded_token.get("last_name"),
                "full_name": decoded_token.get("name")
                or (
                    f"{decoded_token.get('first_name', '')} {decoded_token.get('last_name', '')}".strip()
                    or None
                ),
                "image_url": decoded_token.get("image_url"),
                "metadata": decoded_token.get("metadata", {}),
            }
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid token: {str(e)}", exc_info=True)
        raise ValueError(f"Invalid token: {str(e)}")
    except Exception as e:
        logger.error(f"Error verifying Clerk token: {str(e)}", exc_info=True)
        raise ValueError(f"Token verification failed: {str(e)}")
