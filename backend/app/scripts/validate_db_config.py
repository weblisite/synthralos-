#!/usr/bin/env python3
"""
Validate database configuration before running migrations.

This script checks that SUPABASE_DB_URL is properly configured
and doesn't use IP addresses (which will fail on Render).
"""

import logging
import re
import sys
from urllib.parse import urlparse

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def validate_db_url(db_url: str) -> bool:
    """
    Validate that the database URL doesn't use an IP address.

    Returns True if valid, raises ValueError if invalid.
    """
    if not db_url:
        raise ValueError(
            "SUPABASE_DB_URL is not set. Please set it in Render environment variables."
        )

    # Parse the URL
    parsed = urlparse(db_url)
    hostname = parsed.hostname or ""

    if not hostname:
        raise ValueError(
            f"Invalid SUPABASE_DB_URL: Could not parse hostname from '{db_url[:50]}...'"
        )

    # Check if hostname is an IP address
    if re.match(r"^\d+\.\d+\.\d+\.\d+$", hostname):
        error_msg = (
            f"❌ CRITICAL ERROR: SUPABASE_DB_URL uses IP address ({hostname}) instead of hostname.\n"
            f"This will cause connection failures on Render because Supabase blocks direct IP connections.\n\n"
            f"🔧 SOLUTION: Update SUPABASE_DB_URL in Render to use one of these formats:\n\n"
            f"1. Session Pooler (RECOMMENDED for Render):\n"
            f"   postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-1-[REGION].pooler.supabase.com:5432/postgres\n\n"
            f"2. Direct Connection (if Session Pooler doesn't work):\n"
            f"   postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres\n\n"
            f"📖 How to get the correct connection string:\n"
            f"   1. Go to Supabase Dashboard → Your Project\n"
            f"   2. Settings → Database\n"
            f"   3. Connection string → Connection pooling\n"
            f"   4. Select 'Session mode'\n"
            f"   5. Copy the connection string\n"
            f"   6. Update SUPABASE_DB_URL in Render environment variables\n\n"
            f"Current (invalid) connection string hostname: {hostname}\n"
        )
        logger.error(error_msg)
        raise ValueError(error_msg)

    # Log the hostname being used (helps debug)
    logger.info("✅ Database URL validated successfully")
    logger.info(f"   Hostname: {hostname}")
    logger.info(f"   Port: {parsed.port or 5432}")
    logger.info(f"   Database: {parsed.path or '/postgres'}")

    return True


def main():
    """Main validation function."""
    try:
        from app.core.config import settings

        logger.info("Validating database configuration...")

        # Get the database URL (this will trigger our validation in config.py)
        db_url = str(settings.SQLALCHEMY_DATABASE_URI)

        # Additional validation
        validate_db_url(db_url)

        logger.info("✅ Database configuration is valid. Proceeding with migrations...")
        return 0

    except ValueError as e:
        logger.error(str(e))
        logger.error("\n❌ Database configuration validation failed!")
        logger.error(
            "Please fix SUPABASE_DB_URL in Render environment variables and redeploy."
        )
        return 1
    except Exception as e:
        logger.error(f"Unexpected error during validation: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
