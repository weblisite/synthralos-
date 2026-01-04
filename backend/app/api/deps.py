from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.exc import DatabaseError, OperationalError
from sqlmodel import Session, select

from app.core.db import engine
from app.models import User
from app.services.clerk_service import verify_clerk_token
from app.services.system_alerts import create_system_alert

# Use HTTPBearer for Clerk tokens
security_scheme = HTTPBearer()


def get_db() -> Generator[Session, None, None]:
    """
    Get database session with circuit breaker protection.

    Raises HTTPException with 503 if circuit breaker is open.
    """
    from datetime import datetime

    from app.core.db import _circuit_breaker_open_until

    # Check if circuit breaker is open
    if _circuit_breaker_open_until and datetime.now() < _circuit_breaker_open_until:
        remaining = int((_circuit_breaker_open_until - datetime.now()).total_seconds())
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                f"Database circuit breaker is open. Please wait {remaining} seconds before retrying. "
                f"This is a Supabase protection mechanism that activates after too many failed authentication attempts. "
                f"Resets at {_circuit_breaker_open_until.strftime('%H:%M:%S')}"
            ),
        )

    try:
        with Session(engine) as session:
            yield session
    except OperationalError as e:
        error_str = str(e).lower()
        if "circuit breaker" in error_str:
            from app.core.db import (
                _circuit_breaker_wait_time,
                _handle_circuit_breaker_error,
            )

            _handle_circuit_breaker_error(e)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=(
                    f"Database circuit breaker detected. Please wait {_circuit_breaker_wait_time} seconds before retrying. "
                    f"This is a Supabase protection mechanism."
                ),
            )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection error: {str(e)}",
        )


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[HTTPAuthorizationCredentials, Depends(security_scheme)]


def get_current_user(session: SessionDep, credentials: TokenDep) -> User:
    """
    Verify Clerk JWT token and get the current user from the database.
    """
    token = credentials.credentials

    # Validate token is not empty
    if not token or not isinstance(token, str) or not token.strip():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing or empty authentication token",
        )

    try:
        import logging

        logger = logging.getLogger(__name__)

        # Verify token with Clerk
        user_info = verify_clerk_token(token)
        user_email = user_info["email"]
        clerk_user_id = user_info["user_id"]
        full_name = user_info.get("full_name")

        logger.info(
            f"Verified Clerk token for user: {user_email} (ID: {clerk_user_id})"
        )

        # Find user in our database by clerk_user_id first, then email
        try:
            user = None
            if clerk_user_id:
                # Try to find by clerk_user_id first (more reliable)
                user = session.exec(
                    select(User).where(User.clerk_user_id == clerk_user_id)
                ).first()

            # Fallback to email if not found by clerk_user_id
            if not user:
                statement = select(User).where(User.email == user_email)
                user = session.exec(statement).first()
        except (OperationalError, DatabaseError) as db_error:
            logger.error(
                f"Database connection error while fetching user: {str(db_error)}",
                exc_info=True,
            )
            try:
                create_system_alert(
                    session,
                    title="Database Connection Error",
                    message=f"Failed to connect to database during user authentication: {str(db_error)}",
                    severity="critical",
                    category="database",
                    metadata_={"error": str(db_error)},
                )
            except Exception:
                pass
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Database connection error: {str(db_error)}. Please try again later.",
            )
        except Exception as db_error:
            logger.error(
                f"Database error while fetching user: {str(db_error)}", exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(db_error)}",
            )

        # Create user if doesn't exist (Clerk handles auth)
        if not user:
            try:
                # Extract additional info from user_info
                phone_number = None
                if "phone_numbers" in user_info.get("metadata", {}):
                    phone_numbers = user_info["metadata"].get("phone_numbers", [])
                    if phone_numbers and isinstance(phone_numbers, list):
                        phone_number = (
                            phone_numbers[0].get("phone_number")
                            if isinstance(phone_numbers[0], dict)
                            else None
                        )

                new_user = User(
                    email=user_email,
                    hashed_password="",  # Empty for Clerk auth users
                    full_name=full_name,
                    clerk_user_id=clerk_user_id,
                    phone_number=phone_number,
                    email_verified=user_info.get("email_verified", False),
                    clerk_metadata=user_info.get("metadata", {}),
                    is_active=True,
                )
                session.add(new_user)
                session.commit()
                session.refresh(new_user)
                user = new_user
                logger.info(
                    f"Created new user in database: {user_email} "
                    f"(Clerk ID: {clerk_user_id})"
                )

                # Publish real-time update
                try:
                    from app.services.realtime_sync import publish_user_created

                    publish_user_created(
                        str(user.id),
                        {
                            "email": user.email,
                            "full_name": user.full_name,
                            "clerk_user_id": user.clerk_user_id,
                            "is_active": user.is_active,
                        },
                    )
                except Exception as rt_error:
                    # Don't fail user creation if realtime sync fails
                    logger.warning(
                        f"Failed to publish real-time update: {str(rt_error)}"
                    )
            except Exception as create_error:
                logger.warning(f"Error creating user, retrying: {str(create_error)}")
                session.rollback()
                user = session.exec(statement).first()
                if not user:
                    logger.error(
                        f"Failed to create user after retry: {str(create_error)}",
                        exc_info=True,
                    )
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Failed to create user account: {str(create_error)}",
                    )

        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")

        return user

    except HTTPException:
        raise
    except Exception as e:
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Error verifying Clerk token: {str(e)}", exc_info=True)

        # Log authentication error to Wazuh
        try:
            from app.observability.wazuh import default_wazuh_client

            default_wazuh_client.log_security_event(
                event_type="authentication_error",
                severity="high",
                message=f"Token verification error: {str(e)}",
                metadata={"error_type": type(e).__name__},
            )
        except Exception:
            pass

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Could not validate credentials: {str(e)}",
        )


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user
