from datetime import datetime, timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm

from app import crud
from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.core import security
from app.core.config import settings
from app.core.security import generate_token, get_password_hash
from app.models import (
    LoginHistory,
    Message,
    NewPassword,
    Token,
    UserPublic,
    UserSession,
)
from app.utils import (
    generate_password_reset_token,
    generate_reset_password_email,
    send_email,
    verify_password_reset_token,
)

router = APIRouter(tags=["login"])


@router.post("/login/access-token")
def login_access_token(
    request: Request,
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    # Get client info for logging
    ip_address = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")

    user = crud.authenticate(
        session=session, email=form_data.username, password=form_data.password
    )

    if not user:
        # Log failed login attempt (no user_id for failed attempts)
        try:
            # Try to find user by email for logging purposes
            attempted_user = crud.get_user_by_email(
                session=session, email=form_data.username
            )
            login_history = LoginHistory(
                user_id=attempted_user.id if attempted_user else None,
                ip_address=ip_address,
                user_agent=user_agent,
                success=False,
                failure_reason="Incorrect email or password",
            )
            session.add(login_history)
            session.commit()
        except Exception:
            pass  # Don't fail login if logging fails

        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        # Log failed login attempt
        try:
            login_history = LoginHistory(
                user_id=user.id,
                ip_address=ip_address,
                user_agent=user_agent,
                success=False,
                failure_reason="Inactive user",
            )
            session.add(login_history)
            session.commit()
        except Exception:
            pass

        raise HTTPException(status_code=400, detail="Inactive user")

    # Log successful login
    try:
        login_history = LoginHistory(
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
            success=True,
        )
        session.add(login_history)

        # Create session record
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        session_token = generate_token()
        expires_at = datetime.utcnow() + access_token_expires

        user_session = UserSession(
            user_id=user.id,
            session_token=session_token,
            device_info=user_agent[:255],  # Truncate if too long
            ip_address=ip_address,
            user_agent=user_agent[:500],  # Truncate if too long
            expires_at=expires_at,
        )
        session.add(user_session)
        session.commit()
    except Exception:
        pass  # Don't fail login if logging fails

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=security.create_access_token(
            user.id, expires_delta=access_token_expires
        )
    )


@router.post("/login/test-token", response_model=UserPublic)
def test_token(current_user: CurrentUser) -> Any:
    """
    Test access token
    """
    return current_user


@router.post("/password-recovery/{email}")
def recover_password(email: str, session: SessionDep) -> Message:
    """
    Password Recovery
    """
    user = crud.get_user_by_email(session=session, email=email)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )
    password_reset_token = generate_password_reset_token(email=email)
    email_data = generate_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )
    send_email(
        email_to=user.email,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return Message(message="Password recovery email sent")


@router.post("/reset-password/")
def reset_password(session: SessionDep, body: NewPassword) -> Message:
    """
    Reset password
    """
    email = verify_password_reset_token(token=body.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = crud.get_user_by_email(session=session, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    hashed_password = get_password_hash(password=body.new_password)
    user.hashed_password = hashed_password
    session.add(user)
    session.commit()
    return Message(message="Password updated successfully")


@router.post(
    "/password-recovery-html-content/{email}",
    dependencies=[Depends(get_current_active_superuser)],
    response_class=HTMLResponse,
)
def recover_password_html_content(email: str, session: SessionDep) -> Any:
    """
    HTML Content for Password Recovery
    """
    user = crud.get_user_by_email(session=session, email=email)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    password_reset_token = generate_password_reset_token(email=email)
    email_data = generate_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )

    return HTMLResponse(
        content=email_data.html_content, headers={"subject:": email_data.subject}
    )
