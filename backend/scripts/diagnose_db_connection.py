#!/usr/bin/env python3
"""
Diagnose database connection issues.

This script helps identify what's causing database connection failures
by testing different connection scenarios.
"""

import re
import sys
from pathlib import Path
from urllib.parse import unquote

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.config import settings


def analyze_connection_string():
    """Analyze the connection string for potential issues."""
    print("=" * 70)
    print("Database Connection String Analysis")
    print("=" * 70)
    print()

    db_url = str(settings.SQLALCHEMY_DATABASE_URI)

    # Extract components
    match = re.search(r"://([^:]+):([^@]+)@([^:/]+):(\d+)/(.+)", db_url)
    if not match:
        print("❌ Could not parse connection string")
        return

    username = match.group(1)
    password_encoded = match.group(2)
    host = match.group(3)
    port = match.group(4)
    database = match.group(5)

    password_decoded = unquote(password_encoded)

    print("📋 Connection String Components:")
    print(f"   Username: {username}")
    print(
        f"   Password: {'*' * min(len(password_decoded), 20)} (length: {len(password_decoded)})"
    )
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Database: {database}")
    print()

    # Check for common issues
    print("🔍 Potential Issues:")
    issues = []

    # Check password format
    if "[" in password_decoded or "]" in password_decoded:
        issues.append("❌ Password contains brackets - should be removed")
        print(f"   Password contains brackets: '{password_decoded}'")

    if password_decoded != password_decoded.strip():
        issues.append("⚠️  Password has leading/trailing whitespace")
        print(f"   Password has whitespace: '{password_decoded}'")

    # Check username format for pooler
    if ".pooler.supabase.com" in host:
        if not username.startswith("postgres."):
            issues.append(
                "⚠️  Pooler connection should use 'postgres.[PROJECT_REF]' format"
            )
            print(f"   Username format: {username} (expected: postgres.[PROJECT_REF])")

        if port != "6543":
            issues.append("❌ Pooler connection should use port 6543")
            print(f"   Port: {port} (expected: 6543)")

    # Check host format
    if ".pooler.supabase.com" not in host and "db." not in host:
        issues.append("⚠️  Host format doesn't match Supabase patterns")
        print(f"   Host: {host}")

    if not issues:
        print("   ✅ Connection string format looks correct")
    else:
        print()
        print("💡 Recommendations:")
        for issue in issues:
            if "brackets" in issue.lower():
                print("   1. Remove brackets from password in .env file")
            if "port" in issue.lower():
                print("   2. Use port 6543 for pooler connections")
            if "username" in issue.lower():
                print("   3. Verify username format matches Supabase dashboard")

    print()
    print("=" * 70)
    print("🔑 Password Verification Steps:")
    print("=" * 70)
    print()
    print("1. Go to Supabase Dashboard:")
    print("   https://supabase.com/dashboard")
    print()
    print("2. Select your project")
    print()
    print("3. Navigate to: Settings → Database")
    print()
    print("4. Check 'Database Password' section")
    print()
    print("5. Verify password matches exactly (no brackets, no extra spaces)")
    print()
    print("6. If password is different:")
    print("   - Click 'Reset Database Password'")
    print("   - Copy the new password")
    print("   - Update SUPABASE_DB_URL in .env file")
    print()
    print("=" * 70)
    print("📝 Getting Fresh Connection String:")
    print("=" * 70)
    print()
    print("1. In Supabase Dashboard → Settings → Database")
    print()
    print("2. Scroll to 'Connection string' section")
    print()
    print("3. Select 'Connection pooling' tab")
    print()
    print("4. Copy the connection string")
    print()
    print("5. Replace [YOUR-PASSWORD] with actual password")
    print()
    print("6. Update SUPABASE_DB_URL in .env file")
    print()
    print("Expected format:")
    print(
        "   postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-[N]-[REGION].pooler.supabase.com:6543/postgres"
    )
    print()


if __name__ == "__main__":
    try:
        analyze_connection_string()
    except Exception as e:
        print(f"❌ Error: {e}", exc_info=True)
        sys.exit(1)
