import logging
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import func, select

logger = logging.getLogger(__name__)

from app import crud
from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.models import (
    Message,
    UpdatePassword,
    User,
    UserAPIKey,
    UserAPIKeyCreate,
    UserAPIKeyPublic,
    UserAPIKeyUpdate,
    UserCreate,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
)
from app.services.api_keys import (
    SERVICE_DEFINITIONS,
    default_api_key_service,
)
from app.utils import generate_new_account_email, send_email

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
