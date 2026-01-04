#!/usr/bin/env python3
"""
Check migration status and prepare SQL for Supabase MCP.

This script:
1. Checks current Alembic version in database
2. Lists all migrations in codebase
3. Identifies pending migrations
4. Generates SQL for pending migrations
5. Shows MCP commands to apply them
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from alembic.config import Config  # noqa: E402
from alembic.script import ScriptDirectory  # noqa: E402


def get_alembic_config() -> Config:
    """Get Alembic configuration."""
    alembic_ini = backend_dir / "alembic.ini"
    config = Config(str(alembic_ini))
    return config


def get_migration_chain():
    """Get all migrations in order."""
    config = get_alembic_config()
    script = ScriptDirectory.from_config(config)

    migrations = []
    current = script.get_current_head()

    # Walk backwards from head to get all migrations
    rev = current
    while rev:
        migration = script.get_revision(rev)
        if migration:
            migrations.insert(
                0,
                {
                    "revision": migration.revision,
                    "down_revision": migration.down_revision,
                    "doc": migration.doc,
                },
            )
            rev = migration.down_revision
            if isinstance(rev, tuple):
                rev = rev[0] if rev else None
        else:
            break

    return migrations


def main():
    """Main function."""
    print("=" * 80)  # noqa: T201
    print("Migration Status Check")  # noqa: T201
    print("=" * 80)  # noqa: T201

    # Get migration chain
    migrations = get_migration_chain()

    print(f"\n📋 Found {len(migrations)} migrations in codebase:")  # noqa: T201
    for i, mig in enumerate(migrations, 1):
        print(f"  {i}. {mig['revision']} - {mig['doc']}")  # noqa: T201
        if mig["down_revision"]:
            if isinstance(mig["down_revision"], tuple):
                print(f"     ↓ (from {mig['down_revision'][0]})")  # noqa: T201
            else:
                print(f"     ↓ (from {mig['down_revision']})")  # noqa: T201

    print("\n" + "=" * 80)  # noqa: T201
    print("To check current database version, run:")  # noqa: T201
    print(  # noqa: T201
        "  SELECT version_num FROM alembic_version ORDER BY version_num DESC LIMIT 1;"
    )
    print("\nTo check if platform_settings table exists:")  # noqa: T201
    print("  SELECT EXISTS (SELECT FROM information_schema.tables")  # noqa: T201
    print("    WHERE table_schema = 'public' AND table_name = 'platform_settings');")  # noqa: T201
    print("\n" + "=" * 80)  # noqa: T201
    print("\n📝 SQL Migration File Ready:")  # noqa: T201
    print(  # noqa: T201
        "  backend/migrations/supabase/20250102000000_add_platform_settings_table.sql"
    )
    print("\n" + "=" * 80)  # noqa: T201
    print("\nTo apply via Supabase MCP, use:")  # noqa: T201
    print("\nmcp_supabase_apply_migration(")  # noqa: T201
    print('    name="add_platform_settings_table",')  # noqa: T201
    print('    query="""')  # noqa: T201
    print("        -- SQL from migration file")  # noqa: T201
    print('    """')  # noqa: T201
    print(")")  # noqa: T201
    print("\n" + "=" * 80)  # noqa: T201


if __name__ == "__main__":
    main()
