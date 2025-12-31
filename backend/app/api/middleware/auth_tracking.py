"""
Authentication tracking middleware.

Tracks login history and sessions when users authenticate via Clerk.
This middleware is called on first authentication to log login events.
"""

import logging
from collections.abc import Callable
from datetime import datetime, timedelta

from fastapi import Request, Response
from sqlmodel import Session

from app.core.config import settings
from app.core.db import engine
from app.core.security import generate_token
from app.models import LoginHistory, User, UserSession

logger = logging.getLogger(__name__)

# Track which users have been logged in this request cycle
_logged_users: set[str] = set()


def get_client_info(request: Request) -> tuple[str, str]:
    """Extract client IP and user agent from request."""
    # Get IP address
    ip_address = "unknown"
    if request.client:
        ip_address = request.client.host
    # Check for forwarded IP (from proxy/load balancer)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        ip_address = forwarded_for.split(",")[0].strip()

    # Get user agent
    user_agent = request.headers.get("user-agent", "unknown")

    return ip_address, user_agent


async def track_auth_middleware(request: Request, call_next: Callable) -> Response:
    """
    Middleware to track authentication events.

    Logs login history and creates session records when users authenticate.
    """
    response = await call_next(request)

    # Only track successful authenticated requests
    if response.status_code != 200:
        return response

    # Check if this is an authenticated request
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return response

    token = auth_header.replace("Bearer ", "")

    # Extract user email from token (same logic as get_current_user)
    try:
        import jwt

        payload = jwt.decode(token, options={"verify_signature": False})
        user_email = payload.get("email")
        if not user_email:
            user_metadata = payload.get("user_metadata", {})
            if isinstance(user_metadata, dict):
                user_email = user_metadata.get("email")

        if not user_email:
            return response

        # Check if we've already logged this user in this request cycle
        if user_email in _logged_users:
            return response

        # Get user from database
        with Session(engine) as session:
            from sqlmodel import select

            statement = select(User).where(User.email == user_email)
            user = session.exec(statement).first()

            if not user:
                return response

            # Check if this is a new login (no recent login history)
            # Only log if last login was more than 5 minutes ago
            recent_login = session.exec(
                select(LoginHistory)
                .where(
                    LoginHistory.user_id == user.id,
                    LoginHistory.success.is_(True),
                    LoginHistory.created_at > datetime.utcnow() - timedelta(minutes=5),
                )
                .order_by(LoginHistory.created_at.desc())
                .limit(1)
            ).first()

            if not recent_login:
                # Log successful login
                ip_address, user_agent = get_client_info(request)

                try:
                    login_history = LoginHistory(
                        user_id=user.id,
                        ip_address=ip_address,
                        user_agent=user_agent[:500],  # Truncate if too long
                        success=True,
                    )
                    session.add(login_history)

                    # Create session record
                    access_token_expires = timedelta(
                        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
                    )
                    session_token = generate_token()
                    expires_at = datetime.utcnow() + access_token_expires

                    user_session = UserSession(
                        user_id=user.id,
                        session_token=session_token,
                        device_info=user_agent[:255],
                        ip_address=ip_address,
                        user_agent=user_agent[:500],
                        expires_at=expires_at,
                    )
                    session.add(user_session)
                    session.commit()

                    # Mark as logged
                    _logged_users.add(user_email)

                    logger.info(f"Logged login for user {user_email} from {ip_address}")
                except Exception as e:
                    logger.error(f"Failed to log login history: {e}", exc_info=True)
                    session.rollback()

    except Exception as e:
        # Don't fail the request if tracking fails
        logger.error(f"Error in auth tracking middleware: {e}", exc_info=True)

    return response
