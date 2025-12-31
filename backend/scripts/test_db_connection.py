#!/usr/bin/env python3
"""
Test database connection without triggering circuit breaker.

This script tests the database connection with minimal retries
to avoid triggering Supabase's circuit breaker protection.

Usage:
    python scripts/test_db_connection.py
"""

import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import logging

from app.core.config import settings
from app.core.db import get_circuit_breaker_status

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Test database connection."""
    print("=" * 60)
    print("Database Connection Test")
    print("=" * 60)
    print()

    # Check circuit breaker status first
    cb_status = get_circuit_breaker_status()
    print(f"Circuit Breaker Status: {'OPEN' if cb_status['is_open'] else 'CLOSED'}")
    if cb_status["is_open"]:
        print("  ⚠️  Circuit breaker is open!")
        print(f"  ⏳ Wait {cb_status['remaining_seconds']} seconds before retrying")
        print(f"  🕐 Resets at: {cb_status['resets_at']}")
        print()
        print("💡 TIP: The circuit breaker is a Supabase protection mechanism.")
        print("   It activates after too many failed authentication attempts.")
        print("   Check your database password in the .env file.")
        return False

    print()
    print("Testing database connection...")
    print(
        f"Database URL: {str(settings.SQLALCHEMY_DATABASE_URI).split('@')[1] if '@' in str(settings.SQLALCHEMY_DATABASE_URI) else 'Hidden'}"
    )
    print()

    # Test connection with detailed error reporting
    try:
        from sqlmodel import Session, select

        from app.core.db import engine

        print("Attempting database connection...")
        with Session(engine) as session:
            result = session.exec(select(1))
            result.first()
        print("✅ Database connection successful!")
        return True
    except Exception as e:
        error_str = str(e)
        print("❌ Database connection failed!")
        print()
        print(f"Error: {error_str}")
        print()

        if "circuit breaker" in error_str.lower():
            print("🔴 CIRCUIT BREAKER IS OPEN")
            print("  - Wait 5-15 minutes for it to reset")
            print("  - Do NOT retry immediately (this keeps it open)")
            print("  - Verify your database password is correct")
        elif "authentication" in error_str.lower() or "password" in error_str.lower():
            print("🔴 AUTHENTICATION FAILED")
            print("  - Check your SUPABASE_DB_PASSWORD in .env")
            print("  - Verify the password in Supabase dashboard")
            print(
                "  - Ensure password is URL-encoded if it contains special characters"
            )
        elif "connection" in error_str.lower() or "timeout" in error_str.lower():
            print("🔴 CONNECTION FAILED")
            print("  - Check network connectivity")
            print("  - Verify database server is accessible")
            print("  - Check firewall settings")
        else:
            print("Possible causes:")
            print("  1. Incorrect database password in .env file")
            print("  2. Database server is down")
            print("  3. Network connectivity issues")
            print("  4. Circuit breaker is open")

        print()
        print("💡 TIP: Verify your SUPABASE_DB_URL or SUPABASE_DB_PASSWORD in .env")
        print(
            "💡 TIP: Get the correct connection string from Supabase Dashboard → Settings → Database"
        )
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
