from collections.abc import Generator
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session
from supabase import Client, create_client

from app.core.config import settings
from app.core.db import engine
from app.models import User

# Use HTTPBearer instead of OAuth2PasswordBearer for Supabase tokens
security_scheme = HTTPBearer()

# Initialize Supabase client for token verification
supabase_client: Client | None = None


def get_supabase_client() -> Client:
    global supabase_client
    if supabase_client is None:
        supabase_client = create_client(
            settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY
        )
    return supabase_client


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[HTTPAuthorizationCredentials, Depends(security_scheme)]


def get_current_user(session: SessionDep, credentials: TokenDep) -> User:
    """
    Verify Supabase JWT token and get the current user from the database.
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
        
        # Use Supabase to verify the token and get user info
        # This is the most reliable way to validate tokens and get user details
        supabase = get_supabase_client()
        user_email = None
        full_name = None
        supabase_user_id = None

        try:
            # Verify token with Supabase and get user info
            # This validates the token signature and expiration
            user_response = supabase.auth.get_user(token)
            
            if not user_response or not user_response.user:
                logger.warning(f"Supabase get_user returned no user for token (length: {len(token)})")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid or expired token. Please refresh your session.",
                )
            
            # Extract user info from Supabase user object
            supabase_user = user_response.user
            user_email = supabase_user.email
            supabase_user_id = supabase_user.id
            
            # Get full_name from user_metadata if available
            if supabase_user.user_metadata:
                full_name = supabase_user.user_metadata.get("full_name")
            
            logger.debug(f"Verified token for user: {user_email} (ID: {supabase_user_id})")
            
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            # Log the error for debugging
            logger.error(
                f"Error verifying token with Supabase: {str(e)}", 
                exc_info=True
            )
            
            # Fallback: Try to decode JWT directly if Supabase verification fails
            # This might happen if the token format is unexpected
            try:
                # Basic JWT format check
                token_parts = token.split(".")
                if len(token_parts) != 3:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Invalid token format: Not enough segments (expected 3, got {len(token_parts)}). Please ensure you're using a valid Supabase access token.",
                    )

                # Decode without verification as fallback
                payload = jwt.decode(token, options={"verify_signature": False})

                # Check token expiration
                import time
                exp = payload.get("exp")
                if exp and exp < time.time():
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Token has expired. Please refresh your session.",
                    )

                # Extract user info from JWT payload
                user_email = payload.get("email")
                supabase_user_id = payload.get("sub")

                # Try to get email from user_metadata if not directly in payload
                if not user_email:
                    user_metadata = payload.get("user_metadata", {})
                    if isinstance(user_metadata, dict):
                        user_email = user_metadata.get("email")
                        full_name = user_metadata.get("full_name")

                # Try app_metadata as last resort
                if not user_email:
                    app_metadata = payload.get("app_metadata", {})
                    if isinstance(app_metadata, dict):
                        user_email = app_metadata.get("email")
                
                logger.warning(f"Used JWT fallback for user: {user_email}")
                
            except HTTPException:
                raise
            except Exception as fallback_error:
                logger.error(
                    f"JWT fallback also failed: {str(fallback_error)}, token length: {len(token)}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Could not validate token: {str(e)}. Please ensure you're using a valid Supabase access token.",
                )

        if not user_email:
            logger.error(
                f"Email not found after token verification. User ID: {supabase_user_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User email not found in token. Please ensure you're using a valid user access token.",
            )

        # Find user in our database by email
        from sqlmodel import select

        statement = select(User).where(User.email == user_email)
        user = session.exec(statement).first()

        if not user:
            # User exists in Supabase but not in our DB - create it
            # For Supabase auth users, we don't store passwords in our DB
            # User is already imported at the top of the file

            # Create user directly without password (Supabase handles auth)
            # full_name is already extracted above

            try:
                new_user = User(
                    email=user_email,
                    hashed_password="",  # Empty for Supabase auth users
                    full_name=full_name,
                    is_active=True,
                )
                session.add(new_user)
                session.commit()
                session.refresh(new_user)
                user = new_user
            except Exception as create_error:
                # Handle race condition: user might have been created by another request
                # Rollback and try to fetch again
                import logging

                logger = logging.getLogger(__name__)
                logger.warning(f"Error creating user, retrying: {str(create_error)}")
                session.rollback()
                user = session.exec(statement).first()
                if not user:
                    # Log the error and re-raise with better message
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

    except HTTPException as http_exc:
        # Log authentication failure to Wazuh

        from app.observability.wazuh import default_wazuh_client

        # Try to get IP address from request context if available
        ip_address = None
        try:
            # This is a workaround - FastAPI doesn't expose request in deps easily
            # In production, you might want to pass request explicitly
            pass
        except Exception:
            pass

        default_wazuh_client.log_security_event(
            event_type="authentication_failure",
            severity="medium",
            message=f"Authentication failed: {http_exc.detail}",
            ip_address=ip_address,
            metadata={"status_code": http_exc.status_code},
        )
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log the error for debugging
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Error verifying Supabase token: {str(e)}", exc_info=True)

        # Log authentication error to Wazuh
        from app.observability.wazuh import default_wazuh_client

        default_wazuh_client.log_security_event(
            event_type="authentication_error",
            severity="high",
            message=f"Token verification error: {str(e)}",
            metadata={"error_type": type(e).__name__},
        )

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
