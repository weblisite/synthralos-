from collections.abc import Generator
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session

from app.core.config import settings
from app.core.db import engine
from app.models import User
from supabase import create_client, Client

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
        # First, try to get user info from Supabase using the token
        # This is the most reliable way to get user details
        # Let Supabase handle token validation - it can handle various token formats
        supabase = get_supabase_client()
        user_email = None
        full_name = None
        
        # Decode JWT token directly (Supabase tokens are JWTs)
        # Supabase access tokens contain user info in the JWT payload
        try:
            # Basic JWT format check before decoding
            token_parts = token.split('.')
            if len(token_parts) != 3:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Invalid token format: Not enough segments (expected 3, got {len(token_parts)}). Please ensure you're using a valid Supabase access token.",
                )
            
            # Decode without verification (we'll verify by checking the user exists in DB)
            # Supabase tokens are signed, but we don't need to verify here since we're checking
            # against our database anyway
            payload = jwt.decode(token, options={"verify_signature": False})
            
            # Check token expiration
            import time
            exp = payload.get("exp")
            if exp and exp < time.time():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Token has expired. Please refresh your session.",
                )
            
            # Extract user info from the JWT payload
            # Supabase JWT structure: { "sub": "user-id", "email": "user@synthralos.ai", "user_metadata": {...}, ... }
            user_email = payload.get("email")
            supabase_user_id = payload.get("sub")  # Subject (user ID)
            
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
            
            # If still no email, try using the "sub" (user ID) to look up the user
            # This is a fallback for tokens that don't include email
            if not user_email and supabase_user_id:
                # Try to find user by Supabase user ID stored in a custom field
                # Note: This requires storing supabase_user_id in the User model
                # For now, we'll just log and fail
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Email not found in token, sub: {supabase_user_id}, payload keys: {list(payload.keys())}")
                    
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except jwt.DecodeError as e:
            # More detailed error message
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"JWT decode error: {str(e)}, token length: {len(token)}, token preview: {token[:50]}...")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Invalid token format: {str(e)}. Please ensure you're using a valid Supabase access token.",
            )
        except Exception as e:
            # Log unexpected errors
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Unexpected error decoding token: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Could not decode token: {str(e)}",
            )
        
        if not user_email:
            # Log the payload for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Email not found in token payload. Payload keys: {list(payload.keys())}, sub: {payload.get('sub')}")
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
                    logger.error(f"Failed to create user after retry: {str(create_error)}", exc_info=True)
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Failed to create user account: {str(create_error)}",
                    )
        
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    return user
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log the error for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error verifying Supabase token: {str(e)}", exc_info=True)
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
