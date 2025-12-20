#!/usr/bin/env python3
"""
Script to promote a user to superuser/admin status.

Usage:
    cd backend && source .venv/bin/activate
    python scripts/promote_user_to_admin.py <email>

Example:
    python scripts/promote_user_to_admin.py myweblisite@gmail.com
"""

import sys
from pathlib import Path

# Add backend directory to path so we can import app modules
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Load environment variables from .env file
from dotenv import load_dotenv

env_path = backend_dir / ".env"
if env_path.exists():
    load_dotenv(env_path)

from sqlmodel import Session, select

from app.core.db import engine
from app.models import User


def promote_user_to_admin(email: str) -> None:
    """Promote a user to superuser/admin status."""
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == email)).first()

        if not user:
            print(f"❌ User with email '{email}' not found")
            sys.exit(1)

        if user.is_superuser:
            print(f"✅ User '{email}' is already a superuser")
            return

        user.is_superuser = True
        session.add(user)
        session.commit()
        session.refresh(user)

        print(f"✅ Successfully promoted user '{email}' to superuser/admin")
        print(f"   User ID: {user.id}")
        print(f"   Full Name: {user.full_name or 'N/A'}")
        print(f"   Is Superuser: {user.is_superuser}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/promote_user_to_admin.py <email>")
        sys.exit(1)

    email = sys.argv[1]
    promote_user_to_admin(email)
