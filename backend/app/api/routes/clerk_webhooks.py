"""
Clerk Webhook Handler

Syncs Clerk user events to local database.
"""
import hashlib
import hmac
import json
import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Request, status
from sqlmodel import Session, select

from app.api.deps import get_db
from app.core.config import settings
from app.models import User, UserPreferences

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
logger = logging.getLogger(__name__)


@router.post("/clerk")
async def clerk_webhook(request: Request) -> dict[str, Any]:
    """
    Handle Clerk webhook events.

    Events handled:
    - user.created: Create user in database
    - user.updated: Update user in database (including avatar sync)
    - user.deleted: Deactivate user in database
    """
    # Verify webhook signature
    svix_id = request.headers.get("svix-id")
    svix_timestamp = request.headers.get("svix-timestamp")
    svix_signature = request.headers.get("svix-signature")

    if not all([svix_id, svix_timestamp, svix_signature]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing webhook headers"
        )

    # Verify signature
    payload = await request.body()
    signed_content = f"{svix_id}.{svix_timestamp}.{payload.decode()}"

    if not settings.CLERK_WEBHOOK_SECRET:
        logger.warning(
            "CLERK_WEBHOOK_SECRET not configured, skipping signature verification"
        )
    else:
        expected_signature = hmac.new(
            settings.CLERK_WEBHOOK_SECRET.encode(),
            signed_content.encode(),
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(svix_signature, f"v1={expected_signature}"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature",
            )

    # Parse event
    event = json.loads(payload)
    event_type = event.get("type")
    data = event.get("data", {})

    logger.info(f"Received Clerk webhook event: {event_type}")

    # Get database session
    db_gen = get_db()
    db: Session = next(db_gen)

    try:
        if event_type == "user.created":
            # Create user in database
            email_addresses = data.get("email_addresses", [])
            primary_email = None
            for email_obj in email_addresses:
                if email_obj.get("id") == data.get("primary_email_address_id"):
                    primary_email = email_obj.get("email_address")
                    break

            if not primary_email and email_addresses:
                primary_email = email_addresses[0].get("email_address")

            if primary_email:
                # Check if user already exists
                existing_user = db.exec(
                    select(User).where(User.email == primary_email)
                ).first()

                if not existing_user:
                    new_user = User(
                        email=primary_email,
                        hashed_password="",
                        full_name=(
                            f"{data.get('first_name', '')} {data.get('last_name', '')}".strip()
                            or None
                        ),
                        is_active=True,
                    )
                    db.add(new_user)
                    db.commit()
                    db.refresh(new_user)
                    logger.info(f"Created user from Clerk webhook: {primary_email}")

        elif event_type == "user.updated":
            # Update user in database
            email_addresses = data.get("email_addresses", [])
            primary_email = None
            for email_obj in email_addresses:
                if email_obj.get("id") == data.get("primary_email_address_id"):
                    primary_email = email_obj.get("email_address")
                    break

            if primary_email:
                user = db.exec(select(User).where(User.email == primary_email)).first()

                if user:
                    # Update full name
                    full_name = (
                        f"{data.get('first_name', '')} {data.get('last_name', '')}".strip()
                        or user.full_name
                    )
                    if full_name != user.full_name:
                        user.full_name = full_name

                    # Sync avatar URL from Clerk to preferences
                    image_url = data.get("image_url")
                    if image_url:
                        preferences = db.exec(
                            select(UserPreferences).where(
                                UserPreferences.user_id == user.id
                            )
                        ).first()

                        if preferences:
                            if preferences.avatar_url != image_url:
                                preferences.avatar_url = image_url
                                db.add(preferences)
                        else:
                            # Create preferences if they don't exist
                            preferences = UserPreferences(
                                user_id=user.id,
                                avatar_url=image_url,
                            )
                            db.add(preferences)

                    db.add(user)
                    db.commit()
                    logger.info(f"Updated user from Clerk webhook: {primary_email}")

        elif event_type == "user.deleted":
            # Deactivate user in database
            # Note: Clerk user ID != our database user ID
            # We'll match by email addresses
            email_addresses = data.get("email_addresses", [])
            for email_obj in email_addresses:
                email = email_obj.get("email_address")
                if email:
                    user = db.exec(select(User).where(User.email == email)).first()
                    if user:
                        user.is_active = False
                        db.add(user)
                        db.commit()
                        logger.info(f"Deactivated user from Clerk webhook: {email}")
                        break

        return {"status": "success"}

    except Exception as e:
        logger.error(f"Error processing Clerk webhook: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing webhook: {str(e)}",
        )
    finally:
        db.close()
