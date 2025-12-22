"""
CSRF Protection Middleware

Implements CSRF token validation for state-changing HTTP requests.
"""

import logging
import secrets
import time
from collections.abc import Callable
from typing import Any

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)

# In-memory token storage (in production, use Redis or database)
# Format: {token: {"expires_at": timestamp, "user_id": user_id}}
_csrf_tokens: dict[str, dict[str, Any]] = {}

# Token expiration time (15 minutes)
CSRF_TOKEN_EXPIRY_SECONDS = 900

# Exempt paths (no CSRF check required)
CSRF_EXEMPT_PATHS = [
    "/health",
    "/api/v1/utils/csrf-token",
    "/api/v1/openapi.json",
    "/docs",
    "/redoc",
]

# Methods that require CSRF protection
CSRF_PROTECTED_METHODS = ["POST", "PUT", "DELETE", "PATCH"]


def generate_csrf_token() -> str:
    """
    Generate a cryptographically random CSRF token.

    Returns:
        Base64URL-encoded random token (32 bytes = 256 bits)
    """
    return secrets.token_urlsafe(32)


def store_csrf_token(token: str, user_id: str | None = None) -> None:
    """
    Store CSRF token with expiration.

    Args:
        token: CSRF token
        user_id: Optional user ID for token association
    """
    expires_at = time.time() + CSRF_TOKEN_EXPIRY_SECONDS
    _csrf_tokens[token] = {
        "expires_at": expires_at,
        "user_id": user_id,
    }


def validate_csrf_token(token: str) -> bool:
    """
    Validate CSRF token.

    Args:
        token: CSRF token to validate

    Returns:
        True if token is valid, False otherwise
    """
    if not token:
        return False

    if token not in _csrf_tokens:
        return False

    token_data = _csrf_tokens[token]
    expires_at = token_data.get("expires_at", 0)

    # Check expiration
    if time.time() > expires_at:
        # Clean up expired token
        del _csrf_tokens[token]
        return False

    return True


def cleanup_expired_tokens() -> None:
    """Remove expired CSRF tokens."""
    current_time = time.time()
    expired_tokens = [
        token
        for token, data in _csrf_tokens.items()
        if data.get("expires_at", 0) < current_time
    ]
    for token in expired_tokens:
        del _csrf_tokens[token]


class CSRFMiddleware(BaseHTTPMiddleware):
    """
    CSRF protection middleware.

    Validates CSRF tokens for state-changing requests (POST, PUT, DELETE, PATCH).
    """

    def __init__(self, app, exempt_paths: list[str] | None = None):
        """
        Initialize CSRF middleware.

        Args:
            app: Application instance
            exempt_paths: Additional paths to exempt from CSRF check
        """
        super().__init__(app)
        self.exempt_paths = exempt_paths or []
        self.all_exempt_paths = CSRF_EXEMPT_PATHS + self.exempt_paths

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request through CSRF validation.

        Args:
            request: HTTP request
            call_next: Next middleware handler

        Returns:
            HTTP response

        Raises:
            HTTPException: If CSRF token is missing or invalid
        """
        # Clean up expired tokens periodically
        if len(_csrf_tokens) > 1000:  # Only cleanup if many tokens exist
            cleanup_expired_tokens()

        # Check if path is exempt
        path = request.url.path
        if any(path.startswith(exempt) for exempt in self.all_exempt_paths):
            return await call_next(request)

        # Only check CSRF for protected methods
        if request.method not in CSRF_PROTECTED_METHODS:
            return await call_next(request)

        # Get CSRF token from header
        csrf_token = request.headers.get("X-CSRF-Token")

        if not csrf_token:
            logger.warning(f"CSRF token missing for {request.method} {path}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token missing. Include X-CSRF-Token header.",
            )

        # Validate token
        if not validate_csrf_token(csrf_token):
            logger.warning(f"Invalid CSRF token for {request.method} {path}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid or expired CSRF token.",
            )

        # Process request
        response = await call_next(request)

        return response


def get_csrf_token() -> str:
    """
    Get a new CSRF token.

    Returns:
        CSRF token string
    """
    token = generate_csrf_token()
    store_csrf_token(token)
    return token
