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
from app.services.realtime_sync import (
    publish_user_created,
    publish_user_deleted,
    publish_user_updated,
)

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
            # Extract Clerk user ID
            clerk_user_id = data.get("id")

            # Create user in database
            email_addresses = data.get("email_addresses", [])
            primary_email = None
            email_verified = False

            for email_obj in email_addresses:
                if email_obj.get("id") == data.get("primary_email_address_id"):
                    primary_email = email_obj.get("email_address")
                    verification = email_obj.get("verification", {})
                    if isinstance(verification, dict):
                        email_verified = verification.get("status") == "verified"
                    break

            if not primary_email and email_addresses:
                primary_email = email_addresses[0].get("email_address")
                verification = email_addresses[0].get("verification", {})
                if isinstance(verification, dict):
                    email_verified = verification.get("status") == "verified"

            if primary_email:
                # Check if user already exists (by email or clerk_user_id)
                existing_user = None
                if clerk_user_id:
                    existing_user = db.exec(
                        select(User).where(User.clerk_user_id == clerk_user_id)
                    ).first()

                if not existing_user:
                    existing_user = db.exec(
                        select(User).where(User.email == primary_email)
                    ).first()

                if not existing_user:
                    # Extract phone number
                    phone_numbers = data.get("phone_numbers", [])
                    primary_phone = None
                    if phone_numbers:
                        primary_phone_id = data.get("primary_phone_number_id")
                        for phone_obj in phone_numbers:
                            if phone_obj.get("id") == primary_phone_id:
                                primary_phone = phone_obj.get("phone_number")
                                break
                        if not primary_phone and phone_numbers:
                            primary_phone = phone_numbers[0].get("phone_number")

                    # Extract metadata
                    clerk_metadata = {
                        "public_metadata": data.get("public_metadata", {}),
                        "private_metadata": data.get("private_metadata", {}),
                        "unsafe_metadata": data.get("unsafe_metadata", {}),
                        "external_id": data.get("external_id"),
                        "username": data.get("username"),
                        "created_at": data.get("created_at"),
                        "updated_at": data.get("updated_at"),
                    }

                    new_user = User(
                        email=primary_email,
                        hashed_password="",
                        full_name=(
                            f"{data.get('first_name', '')} {data.get('last_name', '')}".strip()
                            or None
                        ),
                        clerk_user_id=clerk_user_id,
                        phone_number=primary_phone,
                        email_verified=email_verified,
                        clerk_metadata=clerk_metadata,
                        is_active=True,
                    )
                    db.add(new_user)
                    db.commit()
                    db.refresh(new_user)
                    logger.info(
                        f"Created user from Clerk webhook: {primary_email} "
                        f"(Clerk ID: {clerk_user_id})"
                    )

                    # Publish real-time update
                    publish_user_created(
                        str(new_user.id),
                        {
                            "email": new_user.email,
                            "full_name": new_user.full_name,
                            "clerk_user_id": new_user.clerk_user_id,
                            "is_active": new_user.is_active,
                        },
                    )

        elif event_type == "user.updated":
            # Extract Clerk user ID
            clerk_user_id = data.get("id")

            # Update user in database (match by clerk_user_id first, then email)
            user = None
            if clerk_user_id:
                user = db.exec(
                    select(User).where(User.clerk_user_id == clerk_user_id)
                ).first()

            if not user:
                email_addresses = data.get("email_addresses", [])
                primary_email = None
                for email_obj in email_addresses:
                    if email_obj.get("id") == data.get("primary_email_address_id"):
                        primary_email = email_obj.get("email_address")
                        break

                if primary_email:
                    user = db.exec(
                        select(User).where(User.email == primary_email)
                    ).first()

            if user:
                updated_fields = []

                # Update clerk_user_id if not set
                if clerk_user_id and not user.clerk_user_id:
                    user.clerk_user_id = clerk_user_id
                    updated_fields.append("clerk_user_id")

                # Update full name
                full_name = (
                    f"{data.get('first_name', '')} {data.get('last_name', '')}".strip()
                    or user.full_name
                )
                if full_name != user.full_name:
                    user.full_name = full_name
                    updated_fields.append("full_name")

                # Update email verification status
                email_addresses = data.get("email_addresses", [])
                email_verified = False
                for email_obj in email_addresses:
                    if email_obj.get("id") == data.get("primary_email_address_id"):
                        verification = email_obj.get("verification", {})
                        if isinstance(verification, dict):
                            email_verified = verification.get("status") == "verified"
                        break

                if user.email_verified != email_verified:
                    user.email_verified = email_verified
                    updated_fields.append("email_verified")

                # Update phone number
                phone_numbers = data.get("phone_numbers", [])
                if phone_numbers:
                    primary_phone_id = data.get("primary_phone_number_id")
                    primary_phone = None
                    for phone_obj in phone_numbers:
                        if phone_obj.get("id") == primary_phone_id:
                            primary_phone = phone_obj.get("phone_number")
                            break
                    if not primary_phone and phone_numbers:
                        primary_phone = phone_numbers[0].get("phone_number")

                    if user.phone_number != primary_phone:
                        user.phone_number = primary_phone
                        updated_fields.append("phone_number")

                # Update Clerk metadata
                clerk_metadata = {
                    "public_metadata": data.get("public_metadata", {}),
                    "private_metadata": data.get("private_metadata", {}),
                    "unsafe_metadata": data.get("unsafe_metadata", {}),
                    "external_id": data.get("external_id"),
                    "username": data.get("username"),
                    "created_at": data.get("created_at"),
                    "updated_at": data.get("updated_at"),
                }
                user.clerk_metadata = clerk_metadata
                updated_fields.append("clerk_metadata")

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
                            updated_fields.append("avatar_url")
                    else:
                        # Create preferences if they don't exist
                        preferences = UserPreferences(
                            user_id=user.id,
                            avatar_url=image_url,
                        )
                        db.add(preferences)
                        updated_fields.append("avatar_url")

                db.add(user)
                db.commit()
                logger.info(
                    f"Updated user from Clerk webhook: {user.email} "
                    f"(Clerk ID: {clerk_user_id}, Fields: {', '.join(updated_fields)})"
                )

                # Publish real-time update
                publish_user_updated(
                    str(user.id),
                    {
                        "email": user.email,
                        "full_name": user.full_name,
                        "clerk_user_id": user.clerk_user_id,
                        "phone_number": user.phone_number,
                        "email_verified": user.email_verified,
                        "is_active": user.is_active,
                        "updated_fields": updated_fields,
                    },
                )

        elif event_type == "user.deleted":
            # Deactivate user in database
            # Match by clerk_user_id first, then email
            clerk_user_id = data.get("id")
            user = None

            if clerk_user_id:
                user = db.exec(
                    select(User).where(User.clerk_user_id == clerk_user_id)
                ).first()

            if not user:
                # Fallback to email matching
                email_addresses = data.get("email_addresses", [])
                for email_obj in email_addresses:
                    email = email_obj.get("email_address")
                    if email:
                        user = db.exec(select(User).where(User.email == email)).first()
                        if user:
                            break

            if user:
                user.is_active = False
                db.add(user)
                db.commit()
                logger.info(
                    f"Deactivated user from Clerk webhook: {user.email} "
                    f"(Clerk ID: {clerk_user_id})"
                )

                # Publish real-time update
                publish_user_deleted(str(user.id))

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
