#!/usr/bin/env python3
"""
Verify Supabase connection string format and provide guidance.

This script helps verify that the connection string is correctly formatted
and provides instructions for getting the correct string from Supabase.
"""

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.config import settings


def parse_connection_string(url: str) -> dict:
    """Parse connection string and extract components."""
    try:
        parsed = urlparse(url)

        # Extract password (may be URL-encoded)
        password_match = re.search(r"://([^:]+):([^@]+)@", url)
        username = password_match.group(1) if password_match else None
        password_encoded = password_match.group(2) if password_match else None
        password_decoded = unquote(password_encoded) if password_encoded else None

        return {
            "scheme": parsed.scheme,
            "username": username,
            "password_encoded": password_encoded,
            "password_decoded": password_decoded,
            "host": parsed.hostname,
            "port": parsed.port,
            "database": parsed.path.lstrip("/"),
            "full_url": url,
        }
    except Exception as e:
        return {"error": str(e)}


def verify_connection_string_format(conn_info: dict) -> list[str]:
    """Verify connection string format and return issues."""
    issues = []

    if "error" in conn_info:
        issues.append(f"❌ Parse error: {conn_info['error']}")
        return issues

    # Check scheme
    if not conn_info["scheme"].startswith("postgresql"):
        issues.append(
            f"⚠️  Scheme should be 'postgresql' or 'postgresql+psycopg', got: {conn_info['scheme']}"
        )

    # Check username format (for pooler)
    if conn_info["host"] and ".pooler.supabase.com" in conn_info["host"]:
        if not conn_info["username"] or not conn_info["username"].startswith(
            "postgres."
        ):
            issues.append(
                f"⚠️  Pooler connection should use username format 'postgres.[PROJECT_REF]', "
                f"got: {conn_info['username']}"
            )

    # Check port
    if conn_info["port"]:
        if ".pooler.supabase.com" in conn_info["host"] and conn_info["port"] != 6543:
            issues.append(
                f"⚠️  Pooler connection should use port 6543, got: {conn_info['port']}"
            )
        elif (
            "db." in conn_info["host"]
            and ".supabase.co" in conn_info["host"]
            and conn_info["port"] != 5432
        ):
            issues.append(
                f"⚠️  Direct connection should use port 5432, got: {conn_info['port']}"
            )

    # Check password
    if conn_info["password_decoded"]:
        if "[" in conn_info["password_decoded"] or "]" in conn_info["password_decoded"]:
            issues.append(
                f"⚠️  Password should not contain brackets. Current: {conn_info['password_decoded']}"
            )
        if len(conn_info["password_decoded"].strip()) == 0:
            issues.append("❌ Password is empty")

    # Check host format
    if conn_info["host"]:
        if (
            ".pooler.supabase.com" not in conn_info["host"]
            and "db." not in conn_info["host"]
        ):
            issues.append(
                f"⚠️  Host should be either '*.pooler.supabase.com' (pooler) or "
                f"'db.*.supabase.co' (direct), got: {conn_info['host']}"
            )

    return issues


def main():
    """Main verification function."""
    print("=" * 70)
    print("Supabase Connection String Verification")
    print("=" * 70)
    print()

    # Get connection string from settings
    try:
        db_url = str(settings.SQLALCHEMY_DATABASE_URI)
        print("📋 Current Connection String:")
        print(f"   {db_url}")
        print()
    except Exception as e:
        print(f"❌ Error getting connection string: {e}")
        return

    # Parse connection string
    conn_info = parse_connection_string(db_url)

    if "error" in conn_info:
        print(f"❌ Failed to parse connection string: {conn_info['error']}")
        return

    # Display parsed components
    print("📊 Parsed Components:")
    print(f"   Scheme:     {conn_info['scheme']}")
    print(f"   Username:   {conn_info['username']}")
    print(
        f"   Password:   {'*' * len(conn_info['password_decoded']) if conn_info['password_decoded'] else 'Not found'}"
    )
    print(f"   Host:       {conn_info['host']}")
    print(f"   Port:       {conn_info['port']}")
    print(f"   Database:   {conn_info['database']}")
    print()

    # Verify format
    print("🔍 Verification:")
    issues = verify_connection_string_format(conn_info)

    if not issues:
        print("   ✅ Connection string format looks correct!")
        print()
        print("   However, if authentication is still failing:")
        print("   1. Verify the password in Supabase Dashboard")
        print("   2. Get a fresh connection string from Supabase Dashboard")
        print("   3. Ensure no extra spaces or hidden characters")
    else:
        for issue in issues:
            print(f"   {issue}")
        print()

    # Instructions
    print("=" * 70)
    print("📝 How to Get Correct Connection String from Supabase:")
    print("=" * 70)
    print()
    print("1. Go to: https://supabase.com/dashboard")
    print("2. Select your project")
    print("3. Navigate to: Settings → Database")
    print("4. Scroll to: Connection string section")
    print("5. Select tab: Connection pooling")
    print("6. Copy the connection string")
    print("7. Replace [YOUR-PASSWORD] with your actual password")
    print("8. Update SUPABASE_DB_URL in .env file")
    print()
    print("Expected format (pooler):")
    print(
        "   postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-[N]-[REGION].pooler.supabase.com:6543/postgres"
    )
    print()
    print("Expected format (direct):")
    print(
        "   postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres"
    )
    print()
    print("=" * 70)
    print("🔑 Password Verification:")
    print("=" * 70)
    print()
    print("To verify your password:")
    print("1. Go to: Settings → Database")
    print("2. Check: Database Password section")
    print("3. If needed: Click 'Reset Database Password'")
    print("4. Copy the new password")
    print("5. Update SUPABASE_DB_URL in .env file")
    print()

    # Show decoded password for verification
    if conn_info["password_decoded"]:
        print(f"Current password (decoded): '{conn_info['password_decoded']}'")
        print(f"Password length: {len(conn_info['password_decoded'])} characters")
        print(
            f"Contains brackets: {'Yes' if '[' in conn_info['password_decoded'] or ']' in conn_info['password_decoded'] else 'No'}"
        )
        print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}", exc_info=True)
        sys.exit(1)
