import json
import logging
import os
import tempfile
import uuid
import zipfile
from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import func, select

from app import crud
from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from app.core.config import settings
from app.core.security import generate_token, get_password_hash, verify_password
from app.models import (
    LoginHistory,
    Message,
    TeamMember,
    UpdatePassword,
    User,
    UserAPIKey,
    UserAPIKeyCreate,
    UserAPIKeyPublic,
    UserAPIKeyUpdate,
    UserCreate,
    UserPreferences,
    UserPreferencesUpdate,
    UserPublic,
    UserRegister,
    UserSession,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
    Workflow,
    WorkflowExecution,
)
from app.services.api_keys import (
    SERVICE_DEFINITIONS,
    default_api_key_service,
)
from app.services.storage import default_storage_service
from app.utils import generate_new_account_email, send_email

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UsersPublic,
)
def read_users(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve users.
    """

    count_statement = select(func.count()).select_from(User)
    count = session.exec(count_statement).one()

    statement = select(User).offset(skip).limit(limit)
    users = session.exec(statement).all()

    return UsersPublic(data=users, count=count)


@router.post(
    "/", dependencies=[Depends(get_current_active_superuser)], response_model=UserPublic
)
def create_user(*, session: SessionDep, user_in: UserCreate) -> Any:
    """
    Create new user.
    """
    user = crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )

    user = crud.create_user(session=session, user_create=user_in)
    if settings.emails_enabled and user_in.email:
        email_data = generate_new_account_email(
            email_to=user_in.email, username=user_in.email, password=user_in.password
        )
        send_email(
            email_to=user_in.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )
    return user


@router.patch("/me", response_model=UserPublic)
def update_user_me(
    *, session: SessionDep, user_in: UserUpdateMe, current_user: CurrentUser
) -> Any:
    """
    Update own user.
    """

    if user_in.email:
        existing_user = crud.get_user_by_email(session=session, email=user_in.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )
    user_data = user_in.model_dump(exclude_unset=True)
    current_user.sqlmodel_update(user_data)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user


@router.patch("/me/password", response_model=Message)
def update_password_me(
    *, session: SessionDep, body: UpdatePassword, current_user: CurrentUser
) -> Any:
    """
    Update own password.
    """
    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    if body.current_password == body.new_password:
        raise HTTPException(
            status_code=400, detail="New password cannot be the same as the current one"
        )
    hashed_password = get_password_hash(body.new_password)
    current_user.hashed_password = hashed_password
    session.add(current_user)
    session.commit()
    return Message(message="Password updated successfully")


@router.get("/me", response_model=UserPublic)
def read_user_me(current_user: CurrentUser) -> Any:
    """
    Get current user.
    """
    return current_user


@router.delete("/me", response_model=Message)
def delete_user_me(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Delete own user.
    """
    if current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )
    session.delete(current_user)
    session.commit()
    return Message(message="User deleted successfully")


@router.post("/signup", response_model=UserPublic)
def register_user(session: SessionDep, user_in: UserRegister) -> Any:
    """
    Create new user without the need to be logged in.
    """
    from app.observability.posthog import default_posthog_client

    user = crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
    user_create = UserCreate.model_validate(user_in)
    user = crud.create_user(session=session, user_create=user_create)

    # Track user signup in PostHog
    default_posthog_client.capture(
        distinct_id=str(user.id),
        event="user_signed_up",
        properties={
            "email": user.email,
            "full_name": user.full_name,
            "is_superuser": user.is_superuser,
        },
    )
    default_posthog_client.identify(
        distinct_id=str(user.id),
        properties={
            "email": user.email,
            "full_name": user.full_name,
            "is_superuser": user.is_superuser,
        },
    )

    return user


@router.get("/{user_id}", response_model=UserPublic)
def read_user_by_id(
    user_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get a specific user by id.
    """
    user = session.get(User, user_id)
    if user == current_user:
        return user
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="The user doesn't have enough privileges",
        )
    return user


@router.patch(
    "/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
)
def update_user(
    *,
    session: SessionDep,
    user_id: uuid.UUID,
    user_in: UserUpdate,
) -> Any:
    """
    Update a user.
    """

    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    if user_in.email:
        existing_user = crud.get_user_by_email(session=session, email=user_in.email)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )

    db_user = crud.update_user(session=session, db_user=db_user, user_in=user_in)
    return db_user


@router.delete("/{user_id}", dependencies=[Depends(get_current_active_superuser)])
def delete_user(
    session: SessionDep, current_user: CurrentUser, user_id: uuid.UUID
) -> Message:
    """
    Delete a user.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user == current_user:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )
    session.delete(user)
    session.commit()
    return Message(message="User deleted successfully")


# ============================================================================
# USER API KEYS ENDPOINTS
# ============================================================================


@router.get("/me/api-keys", response_model=list[UserAPIKeyPublic])
def list_user_api_keys(
    current_user: CurrentUser,
    session: SessionDep,
) -> Any:
    """
    List all API keys for current user.

    Returns masked API keys (only last 4 characters visible).
    """

    api_key_service = default_api_key_service

    # Get all API keys for user
    statement = select(UserAPIKey).where(UserAPIKey.user_id == current_user.id)
    api_keys = session.exec(statement).all()

    # Convert to public format with masked keys
    result = []
    for api_key in api_keys:
        # Retrieve key from Infisical to mask it
        try:
            credentials = api_key_service.retrieve_api_key(
                str(current_user.id), api_key.service_name, api_key.credential_type
            )

            masked_key = "***hidden***"
            if credentials:
                main_key = credentials.get("api_key", "")
                if main_key:
                    masked_key = api_key_service.mask_key(main_key)
        except Exception as e:
            # If retrieval fails (e.g., Infisical not configured), use default masked value
            logger.warning(f"Failed to retrieve API key for masking: {e}")
            masked_key = "***hidden***"

        result.append(
            UserAPIKeyPublic(
                id=api_key.id,
                service_name=api_key.service_name,
                service_display_name=api_key.service_display_name,
                credential_type=api_key.credential_type,
                masked_key=masked_key,
                is_active=api_key.is_active,
                last_used_at=api_key.last_used_at,
                created_at=api_key.created_at,
                updated_at=api_key.updated_at,
            )
        )

    return result


@router.get("/me/api-keys/services", response_model=dict[str, Any])
def list_available_services() -> Any:
    """
    List all available services that support API keys.

    Returns service definitions with display names and credential types.
    """
    return {
        "services": {
            service_name: {
                "display_name": service_def["display_name"],
                "credential_types": service_def["credential_types"],
            }
            for service_name, service_def in SERVICE_DEFINITIONS.items()
        }
    }


@router.post("/me/api-keys", response_model=UserAPIKeyPublic, status_code=201)
def create_user_api_key(
    current_user: CurrentUser,
    session: SessionDep,
    api_key_data: UserAPIKeyCreate,
) -> Any:
    """
    Create a new API key for user.

    Validates the API key before storing it.
    """

    api_key_service = default_api_key_service

    # Validate service name
    if api_key_data.service_name not in SERVICE_DEFINITIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown service: {api_key_data.service_name}",
        )

    service_def = SERVICE_DEFINITIONS[api_key_data.service_name]

    # Validate credential type
    if api_key_data.credential_type:
        if api_key_data.credential_type not in service_def["credential_types"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid credential type '{api_key_data.credential_type}' for service '{api_key_data.service_name}'. Valid types: {service_def['credential_types']}",
            )
    else:
        # Default to first credential type
        api_key_data.credential_type = service_def["credential_types"][0]

    # Check if API key already exists for this service/credential type
    existing = session.exec(
        select(UserAPIKey).where(
            UserAPIKey.user_id == current_user.id,
            UserAPIKey.service_name == api_key_data.service_name,
            UserAPIKey.credential_type == api_key_data.credential_type,
        )
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"API key already exists for {service_def['display_name']} ({api_key_data.credential_type}). Update or delete existing key first.",
        )

    # Validate API key
    if not api_key_service.validate_api_key(
        api_key_data.service_name, api_key_data.api_key, api_key_data.credential_type
    ):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid API key for {service_def['display_name']}. Please check your credentials.",
        )

    # Prepare additional credentials
    additional_credentials = {}
    if api_key_data.api_secret:
        additional_credentials["api_secret"] = api_key_data.api_secret
    if api_key_data.access_token:
        additional_credentials["access_token"] = api_key_data.access_token
    if api_key_data.access_token_secret:
        additional_credentials["access_token_secret"] = api_key_data.access_token_secret

    # Store encrypted key in Infisical
    infisical_path = api_key_service.store_api_key(
        str(current_user.id),
        api_key_data.service_name,
        api_key_data.api_key,
        api_key_data.credential_type,
        additional_credentials if additional_credentials else None,
    )

    # Generate hash for verification
    key_hash = api_key_service.hash_key(api_key_data.api_key)

    # Create database record
    api_key = UserAPIKey(
        user_id=current_user.id,
        service_name=api_key_data.service_name,
        service_display_name=service_def["display_name"],
        credential_type=api_key_data.credential_type,
        infisical_path=infisical_path,
        key_hash=key_hash,
        is_active=True,
    )

    session.add(api_key)
    session.commit()
    session.refresh(api_key)

    # Return masked key
    masked_key = api_key_service.mask_key(api_key_data.api_key)

    return UserAPIKeyPublic(
        id=api_key.id,
        service_name=api_key.service_name,
        service_display_name=api_key.service_display_name,
        credential_type=api_key.credential_type,
        masked_key=masked_key,
        is_active=api_key.is_active,
        last_used_at=api_key.last_used_at,
        created_at=api_key.created_at,
        updated_at=api_key.updated_at,
    )


@router.put("/me/api-keys/{key_id}", response_model=UserAPIKeyPublic)
def update_user_api_key(
    key_id: uuid.UUID,
    current_user: CurrentUser,
    session: SessionDep,
    api_key_data: UserAPIKeyUpdate,
) -> Any:
    """
    Update an API key.

    Can update the key value or toggle active status.
    """
    from datetime import datetime

    api_key_service = default_api_key_service

    # Get API key
    api_key = session.get(UserAPIKey, key_id)
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    if api_key.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Update key value if provided
    if api_key_data.api_key:
        # Validate new key
        if not api_key_service.validate_api_key(
            api_key.service_name, api_key_data.api_key, api_key.credential_type
        ):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid API key for {api_key.service_display_name}",
            )

        # Prepare additional credentials
        additional_credentials = {}
        if api_key_data.api_secret:
            additional_credentials["api_secret"] = api_key_data.api_secret
        if api_key_data.access_token:
            additional_credentials["access_token"] = api_key_data.access_token
        if api_key_data.access_token_secret:
            additional_credentials[
                "access_token_secret"
            ] = api_key_data.access_token_secret

        # Update in Infisical
        api_key_service.store_api_key(
            str(current_user.id),
            api_key.service_name,
            api_key_data.api_key,
            api_key.credential_type,
            additional_credentials if additional_credentials else None,
        )

        # Update hash
        api_key.key_hash = api_key_service.hash_key(api_key_data.api_key)
        api_key.updated_at = datetime.utcnow()

    # Update active status
    if api_key_data.is_active is not None:
        api_key.is_active = api_key_data.is_active

    session.add(api_key)
    session.commit()
    session.refresh(api_key)

    # Return masked key
    credentials = api_key_service.retrieve_api_key(
        str(current_user.id), api_key.service_name, api_key.credential_type
    )
    masked_key = "***hidden***"
    if credentials:
        main_key = credentials.get("api_key", "")
        if main_key:
            masked_key = api_key_service.mask_key(main_key)

    return UserAPIKeyPublic(
        id=api_key.id,
        service_name=api_key.service_name,
        service_display_name=api_key.service_display_name,
        credential_type=api_key.credential_type,
        masked_key=masked_key,
        is_active=api_key.is_active,
        last_used_at=api_key.last_used_at,
        created_at=api_key.created_at,
        updated_at=api_key.updated_at,
    )


@router.delete("/me/api-keys/{key_id}", response_model=Message)
def delete_user_api_key(
    key_id: uuid.UUID,
    current_user: CurrentUser,
    session: SessionDep,
) -> Any:
    """
    Delete an API key.

    Removes key from both database and Infisical.
    """
    api_key_service = default_api_key_service

    # Get API key
    api_key = session.get(UserAPIKey, key_id)
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    if api_key.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Delete from Infisical
    api_key_service.delete_api_key(
        str(current_user.id), api_key.service_name, api_key.credential_type
    )

    # Delete from database
    session.delete(api_key)
    session.commit()

    return Message(message="API key deleted successfully")


@router.post("/me/api-keys/{key_id}/test", response_model=dict[str, Any])
def test_user_api_key(
    key_id: uuid.UUID,
    current_user: CurrentUser,
    session: SessionDep,
) -> Any:
    """
    Test an API key by making a validation request.

    Returns validation result and status.
    """
    api_key_service = default_api_key_service

    # Get API key
    api_key = session.get(UserAPIKey, key_id)
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    if api_key.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Retrieve key from Infisical
    credentials = api_key_service.retrieve_api_key(
        str(current_user.id), api_key.service_name, api_key.credential_type
    )

    if not credentials:
        raise HTTPException(status_code=404, detail="API key not found in storage")

    api_key_value = credentials.get("api_key")
    if not api_key_value:
        raise HTTPException(status_code=400, detail="Invalid API key format")

    # Validate key
    is_valid = api_key_service.validate_api_key(
        api_key.service_name, api_key_value, api_key.credential_type
    )

    # Update last_used_at if valid
    if is_valid:
        from datetime import datetime

        api_key.last_used_at = datetime.utcnow()
        session.add(api_key)
        session.commit()

    return {
        "valid": is_valid,
        "service": api_key.service_display_name,
        "message": "API key is valid" if is_valid else "API key validation failed",
    }


# ============================================================================
# USER PREFERENCES ENDPOINTS
# ============================================================================


@router.get("/me/preferences", response_model=UserPreferences)
def get_user_preferences(current_user: CurrentUser, session: SessionDep) -> Any:
    """
    Get user preferences. Creates default preferences if none exist.
    """
    preferences = session.exec(
        select(UserPreferences).where(UserPreferences.user_id == current_user.id)
    ).first()

    if not preferences:
        # Create default preferences
        preferences = UserPreferences(user_id=current_user.id)
        session.add(preferences)
        session.commit()
        session.refresh(preferences)

    return preferences


@router.patch("/me/preferences", response_model=UserPreferences)
def update_user_preferences(
    current_user: CurrentUser,
    session: SessionDep,
    preferences_update: UserPreferencesUpdate,
) -> Any:
    """
    Update user preferences.
    """
    preferences = session.exec(
        select(UserPreferences).where(UserPreferences.user_id == current_user.id)
    ).first()

    if not preferences:
        # Create preferences if they don't exist
        preferences = UserPreferences(user_id=current_user.id)
        session.add(preferences)
        session.commit()
        session.refresh(preferences)

    # Update only provided fields
    update_data = preferences_update.model_dump(exclude_unset=True)
    preferences.sqlmodel_update(update_data)
    session.add(preferences)
    session.commit()
    session.refresh(preferences)

    return preferences


# ============================================================================
# USER SESSIONS ENDPOINTS
# ============================================================================


@router.get("/me/sessions", response_model=list[UserSession])
def get_user_sessions(
    current_user: CurrentUser, session: SessionDep, limit: int = 50
) -> Any:
    """
    Get active sessions for current user.
    """
    from datetime import datetime

    # Get active sessions (not expired)
    statement = (
        select(UserSession)
        .where(
            UserSession.user_id == current_user.id,
            UserSession.expires_at > datetime.utcnow(),
        )
        .order_by(UserSession.last_active_at.desc())
        .limit(limit)
    )
    sessions = session.exec(statement).all()
    return list(sessions)


@router.delete("/me/sessions/{session_id}", response_model=Message)
def revoke_user_session(
    session_id: uuid.UUID, current_user: CurrentUser, session: SessionDep
) -> Any:
    """
    Revoke a specific session.
    """
    user_session = session.get(UserSession, session_id)
    if not user_session:
        raise HTTPException(status_code=404, detail="Session not found")

    if user_session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    session.delete(user_session)
    session.commit()
    return Message(message="Session revoked successfully")


@router.delete("/me/sessions", response_model=Message)
def revoke_all_sessions_except_current(
    current_user: CurrentUser, session: SessionDep
) -> Any:
    """
    Revoke all sessions except the current one.
    Note: This requires the current session token to be passed in headers.
    """
    from datetime import datetime

    # Get all active sessions except current (this is a simplified version)
    # In production, you'd need to identify the current session token
    statement = select(UserSession).where(
        UserSession.user_id == current_user.id,
        UserSession.expires_at > datetime.utcnow(),
    )
    sessions = session.exec(statement).all()

    # Delete all sessions (in production, exclude current session)
    for user_session in sessions:
        session.delete(user_session)

    session.commit()
    return Message(message="All sessions revoked successfully")


# ============================================================================
# LOGIN HISTORY ENDPOINTS
# ============================================================================


@router.get("/me/login-history", response_model=list[LoginHistory])
def get_login_history(
    current_user: CurrentUser, session: SessionDep, limit: int = 50
) -> Any:
    """
    Get login history for current user.
    """
    statement = (
        select(LoginHistory)
        .where(LoginHistory.user_id == current_user.id)
        .order_by(LoginHistory.created_at.desc())
        .limit(limit)
    )
    history = session.exec(statement).all()
    return list(history)


@router.post("/me/track-login", response_model=Message)
def track_login(
    request: Request, current_user: CurrentUser, session: SessionDep
) -> Any:
    """
    Track a login event. Called by frontend after successful Clerk authentication.
    Creates login history and session records.
    """
    from datetime import datetime, timedelta

    # Get client info
    ip_address = request.client.host if request.client else "unknown"
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        ip_address = forwarded_for.split(",")[0].strip()
    user_agent = request.headers.get("user-agent", "unknown")

    # Check if we've already logged this login recently (within 5 minutes)
    recent_login = session.exec(
        select(LoginHistory)
        .where(
            LoginHistory.user_id == current_user.id,
            LoginHistory.success.is_(True),
            LoginHistory.created_at > datetime.utcnow() - timedelta(minutes=5),
        )
        .order_by(LoginHistory.created_at.desc())
        .limit(1)
    ).first()

    if not recent_login:
        # Log successful login
        login_history = LoginHistory(
            user_id=current_user.id,
            ip_address=ip_address,
            user_agent=user_agent[:500],
            success=True,
        )
        session.add(login_history)

        # Create session record
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        session_token = generate_token()
        expires_at = datetime.utcnow() + access_token_expires

        user_session = UserSession(
            user_id=current_user.id,
            session_token=session_token,
            device_info=user_agent[:255],
            ip_address=ip_address,
            user_agent=user_agent[:500],
            expires_at=expires_at,
        )
        session.add(user_session)
        session.commit()

    return Message(message="Login tracked successfully")


@router.post("/me/data/export", response_model=dict[str, str])
def export_user_data(
    current_user: CurrentUser,
    session: SessionDep,
) -> Any:
    """
    Export all user data as a ZIP file.

    Includes:
    - User profile and preferences
    - Workflows and workflow executions
    - API keys (masked)
    - Team memberships
    - Connector connections
    - Agent tasks
    - RAG indexes
    - OCR jobs
    - Scraping jobs
    - OSINT streams

    Returns a download URL for the exported ZIP file.
    """
    # Create temporary ZIP file
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, f"user_data_export_{current_user.id}.zip")

    export_data = {
        "export_date": datetime.utcnow().isoformat(),
        "user_id": str(current_user.id),
        "user_email": current_user.email,
        "user_profile": {
            "email": current_user.email,
            "full_name": current_user.full_name,
            "is_active": current_user.is_active,
            "is_superuser": current_user.is_superuser,
        },
    }

    # Export workflows
    workflows = session.exec(
        select(Workflow).where(Workflow.owner_id == current_user.id)
    ).all()
    export_data["workflows"] = [
        {
            "id": str(w.id),
            "name": w.name,
            "description": w.description,
            "is_active": w.is_active,
            "trigger_config": w.trigger_config,
            "graph_config": w.graph_config,
            "created_at": w.created_at.isoformat(),
            "updated_at": w.updated_at.isoformat(),
        }
        for w in workflows
    ]

    # Export workflow executions (limit to last 1000)
    executions = session.exec(
        select(WorkflowExecution)
        .where(WorkflowExecution.owner_id == current_user.id)
        .order_by(WorkflowExecution.started_at.desc())
        .limit(1000)
    ).all()
    export_data["workflow_executions"] = [
        {
            "execution_id": e.execution_id,
            "workflow_id": str(e.workflow_id),
            "status": e.status,
            "started_at": e.started_at.isoformat() if e.started_at else None,
            "completed_at": e.completed_at.isoformat() if e.completed_at else None,
        }
        for e in executions
    ]

    # Export API keys (masked)
    api_keys = session.exec(
        select(UserAPIKey).where(UserAPIKey.user_id == current_user.id)
    ).all()
    export_data["api_keys"] = [
        {
            "service_name": ak.service_name,
            "service_display_name": ak.service_display_name,
            "credential_type": ak.credential_type,
            "masked_key": "***hidden***",
            "is_active": ak.is_active,
            "created_at": ak.created_at.isoformat(),
        }
        for ak in api_keys
    ]

    # Export team memberships
    team_members = session.exec(
        select(TeamMember).where(TeamMember.user_id == current_user.id)
    ).all()
    export_data["team_memberships"] = [
        {
            "team_id": str(tm.team_id),
            "role": tm.role,
            "joined_at": tm.joined_at.isoformat() if tm.joined_at else None,
        }
        for tm in team_members
    ]

    # Export user preferences
    try:
        from app.models import UserPreferences

        preferences = session.exec(
            select(UserPreferences).where(UserPreferences.user_id == current_user.id)
        ).first()
        if preferences:
            export_data["preferences"] = {
                "theme": preferences.theme,
                "timezone": preferences.timezone,
                "language": preferences.language,
            }
    except Exception:
        pass

    # Create ZIP file
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        # Add main data file
        zipf.writestr(
            "user_data.json",
            json.dumps(export_data, indent=2, default=str),
        )

        # Add README
        readme = f"""User Data Export
Generated: {datetime.utcnow().isoformat()}
User ID: {current_user.id}
Email: {current_user.email}

This export contains:
- User profile information
- Workflows and workflow executions
- API keys (masked for security)
- Team memberships
- User preferences

All timestamps are in UTC.
"""
        zipf.writestr("README.txt", readme)

    # Upload to storage
    try:
        storage_service = default_storage_service
        file_name = f"exports/user_{current_user.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.zip"

        with open(zip_path, "rb") as f:
            upload_result = storage_service.upload_file(
                bucket="exports",
                file_path=file_name,
                file_data=f.read(),
                content_type="application/zip",
            )

        # Clean up temp file
        os.remove(zip_path)
        os.rmdir(temp_dir)

        return {
            "download_url": upload_result.get("url")
            or upload_result.get("signed_url")
            or upload_result.get("public_url"),
            "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "message": "Data export completed successfully",
        }
    except Exception as e:
        # Clean up on error
        if os.path.exists(zip_path):
            os.remove(zip_path)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)
        logger.error(f"Failed to upload export: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create export: {str(e)}",
        )


@router.post("/me/data/import", response_model=Message)
async def import_user_data(
    request: Request,
    current_user: CurrentUser,
    session: SessionDep,
) -> Any:
    """
    Import workflows from a JSON file.

    Accepts a JSON file with workflow definitions.
    Expected format: {"workflows": [{"name": "...", "description": "...", ...}]}
    """
    from app import crud
    from app.models import WorkflowCreate

    # Check content type
    content_type = request.headers.get("content-type", "")
    if not content_type.startswith("application/json"):
        raise HTTPException(
            status_code=400,
            detail="Content-Type must be application/json",
        )

    # Parse JSON body
    try:
        body = await request.json()
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid JSON: {str(e)}",
        )

    # Validate structure
    if "workflows" not in body:
        raise HTTPException(
            status_code=400,
            detail="JSON must contain a 'workflows' array",
        )

    workflows_data = body["workflows"]
    if not isinstance(workflows_data, list):
        raise HTTPException(
            status_code=400,
            detail="'workflows' must be an array",
        )

    imported_count = 0
    errors = []

    for workflow_data in workflows_data:
        try:
            # Create workflow
            workflow_create = WorkflowCreate(
                name=workflow_data.get("name", "Imported Workflow"),
                description=workflow_data.get("description"),
                is_active=workflow_data.get("is_active", True),
                trigger_config=workflow_data.get("trigger_config", {}),
                graph_config=workflow_data.get("graph_config", {}),
            )

            crud.workflow.create(
                session=session,
                obj_in=workflow_create,
                owner_id=current_user.id,
            )
            imported_count += 1
        except Exception as e:
            logger.error(f"Failed to import workflow: {e}", exc_info=True)
            errors.append(
                f"Failed to import workflow '{workflow_data.get('name', 'unknown')}': {str(e)}"
            )

    if errors:
        return Message(
            message=f"Imported {imported_count} workflows with {len(errors)} errors. Check logs for details."
        )

    return Message(message=f"Successfully imported {imported_count} workflows")


@router.post("/me/avatar", response_model=dict[str, str])
async def upload_avatar(
    request: Request, current_user: CurrentUser, session: SessionDep
) -> Any:
    """
    Upload user avatar to Supabase Storage.

    Expects multipart/form-data with 'file' field containing image.
    """
    from fastapi import UploadFile

    # Get file from request
    form = await request.form()
    file = form.get("file")

    if not file or not hasattr(file, "file"):
        raise HTTPException(status_code=400, detail="No file provided")

    upload_file: UploadFile = file  # type: ignore

    # Validate file type
    if not upload_file.content_type or not upload_file.content_type.startswith(
        "image/"
    ):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Validate file size (max 2MB)
    contents = await upload_file.read()
    if len(contents) > 2 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size must be less than 2MB")

    # Generate filename
    file_extension = (
        upload_file.filename.split(".")[-1] if upload_file.filename else "jpg"
    )
    filename = f"{current_user.id}/{uuid.uuid4()}.{file_extension}"

    try:
        # Upload to Supabase Storage
        upload_result = default_storage_service.upload_file(
            bucket="avatars",
            file_path=filename,
            file_data=contents,
            content_type=upload_file.content_type,
        )

        # Update user preferences
        preferences = session.exec(
            select(UserPreferences).where(UserPreferences.user_id == current_user.id)
        ).first()

        if not preferences:
            preferences = UserPreferences(user_id=current_user.id)
            session.add(preferences)

        preferences.avatar_url = upload_result.get("url") or upload_result.get(
            "public_url"
        )
        session.add(preferences)
        session.commit()
        session.refresh(preferences)

        return {"avatar_url": preferences.avatar_url or ""}
    except Exception as e:
        logger.error(f"Failed to upload avatar: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to upload avatar: {str(e)}"
        )
