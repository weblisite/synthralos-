from fastapi import APIRouter, Depends
from pydantic.networks import EmailStr

from app.api.deps import get_current_active_superuser
from app.api.middleware.csrf import get_csrf_token
from app.models import Message
from app.utils import generate_test_email, send_email

router = APIRouter(prefix="/utils", tags=["utils"])


@router.post(
    "/test-email/",
    dependencies=[Depends(get_current_active_superuser)],
    status_code=201,
)
def test_email(email_to: EmailStr) -> Message:
    """
    Test emails.
    """
    email_data = generate_test_email(email_to=email_to)
    send_email(
        email_to=email_to,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return Message(message="Test email sent")


@router.get("/health-check")
async def health_check() -> bool:
    return True


@router.get("/csrf-token")
def get_csrf_token_endpoint() -> dict[str, str]:
    """
    Get CSRF token for authenticated requests.

    Note: This endpoint is exempt from CSRF protection (in CSRF_EXEMPT_PATHS).

    Returns:
        Dictionary with CSRF token
    """
    token = get_csrf_token()
    return {"csrf_token": token}
