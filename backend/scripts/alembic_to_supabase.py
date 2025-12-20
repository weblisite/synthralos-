#!/usr/bin/env python3
"""
Convert Alembic migrations to SQL for Supabase MCP.

This script:
1. Reads Alembic migration files
2. Generates SQL in offline mode
3. Formats SQL for Supabase
4. Optionally applies via Supabase MCP

Usage:
    python scripts/alembic_to_supabase.py [migration_revision] [--apply]

Examples:
    # Generate SQL for latest migration
    python scripts/alembic_to_supabase.py

    # Generate SQL for specific migration
    python scripts/alembic_to_supabase.py c4cd6f5a4f64

    # Generate and apply SQL
    python scripts/alembic_to_supabase.py --apply
"""

import re
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))


from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory


def get_alembic_config() -> Config:
    """Get Alembic configuration."""
    alembic_ini = backend_dir / "alembic.ini"
    config = Config(str(alembic_ini))
    return config


def get_migration_sql(revision: str | None = None) -> str:
    """
    Generate SQL from Alembic migration.

    Args:
        revision: Specific revision ID, or None for head

    Returns:
        SQL string
    """
    import contextlib
    import io

    config = get_alembic_config()
    script = ScriptDirectory.from_config(config)

    # Determine the revision range
    if revision:
        # Get the specific revision
        target_revision = script.get_revision(revision)
        if not target_revision:
            raise ValueError(f"Revision {revision} not found")

        # Get the down_revision (what comes before this)
        down_revision = target_revision.down_revision
        if isinstance(down_revision, tuple):
            down_revision = down_revision[0] if down_revision else None

        # Upgrade from down_revision to target
        upgrade_from = down_revision or "base"
        upgrade_to = revision
    else:
        # Get head revision
        upgrade_from = None  # Will use current database state
        upgrade_to = "head"

    # Set offline mode to generate SQL
    config.set_main_option("sqlalchemy.url", "postgresql://dummy")

    # Capture stdout (where Alembic outputs SQL in offline mode)
    sql_output = io.StringIO()

    # Generate SQL by capturing stdout
    with contextlib.redirect_stdout(sql_output):
        try:
            if upgrade_from:
                # Upgrade from specific revision
                command.upgrade(config, f"{upgrade_from}:{upgrade_to}", sql=True)
            else:
                # Upgrade to head
                command.upgrade(config, upgrade_to, sql=True)
        except SystemExit:
            # Alembic may call sys.exit(), ignore it
            pass

    sql = sql_output.getvalue()
    return sql


def format_sql_for_supabase(sql: str) -> str:
    """
    Format SQL for Supabase MCP.

    Removes Alembic-specific comments and formats for Supabase.
    Converts JSON to JSONB for PostgreSQL.
    """
    lines = sql.split("\n")
    formatted_lines = []

    for line in lines:
        # Skip Alembic version tracking lines
        if "alembic_version" in line.lower() and "INSERT" in line.upper():
            continue

        # Skip empty lines at start
        if not formatted_lines and not line.strip():
            continue

        # Convert JSON to JSONB for PostgreSQL/Supabase
        # Match JSON type declarations but not JSONB (already correct)
        line = re.sub(r"\bJSON\b(?!B)", "JSONB", line)

        # Convert UUID NOT NULL to UUID PRIMARY KEY DEFAULT gen_random_uuid()
        # Only for primary key columns
        if "PRIMARY KEY" in line.upper() and "UUID NOT NULL" in line.upper():
            # This is handled by the column definition, so we'll fix it after
            pass

        # Keep the line
        formatted_lines.append(line)

    # Join and clean up
    formatted_sql = "\n".join(formatted_lines).strip()

    # Remove multiple blank lines
    formatted_sql = re.sub(r"\n\n\n+", "\n\n", formatted_sql)

    # Add DEFAULT gen_random_uuid() to UUID PRIMARY KEY columns
    # Pattern: id UUID NOT NULL, ... PRIMARY KEY (id)
    formatted_sql = re.sub(
        r"(\w+)\s+UUID\s+NOT\s+NULL(\s*,\s*[^,]*?PRIMARY\s+KEY\s*\(\s*\1\s*\))",
        r"\1 UUID NOT NULL DEFAULT gen_random_uuid()\2",
        formatted_sql,
        flags=re.IGNORECASE,
    )

    # Remove BEGIN/COMMIT transaction markers (Supabase handles this)
    formatted_sql = re.sub(r"^\s*BEGIN\s*;?\s*$", "", formatted_sql, flags=re.MULTILINE)
    formatted_sql = re.sub(
        r"^\s*COMMIT\s*;?\s*$", "", formatted_sql, flags=re.MULTILINE
    )

    # Clean up extra whitespace
    formatted_sql = re.sub(r"\n\n\n+", "\n\n", formatted_sql)
    formatted_sql = formatted_sql.strip()

    return formatted_sql


def get_migration_name(revision: str | None = None) -> str:
    """Get migration name from revision."""
    config = get_alembic_config()
    script = ScriptDirectory.from_config(config)

    if revision:
        script_revision = script.get_revision(revision)
        if script_revision:
            # Convert revision to snake_case name
            name = script_revision.doc or script_revision.revision
            name = name.lower().replace(" ", "_").replace("-", "_")
            return name
    else:
        # Get head revision
        head = script.get_current_head()
        if head:
            script_revision = script.get_revision(head)
            if script_revision:
                name = script_revision.doc or script_revision.revision
                name = name.lower().replace(" ", "_").replace("-", "_")
                return name

    return revision or "migration"


def save_sql_to_file(sql: str, migration_name: str, output_dir: Path | None = None):
    """Save SQL to file."""
    if output_dir is None:
        output_dir = backend_dir / "migrations" / "supabase"

    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{migration_name}.sql"

    with open(output_file, "w") as f:
        f.write(f"-- Migration: {migration_name}\n")
        f.write("-- Generated from Alembic migration\n\n")
        f.write(sql)

    print(f"✅ SQL saved to: {output_file}")
    return output_file


def apply_via_mcp(sql: str, migration_name: str):
    """Apply migration via Supabase MCP (requires manual execution)."""
    print("\n" + "=" * 80)
    print("To apply this migration via Supabase MCP, use:")
    print("=" * 80)
    print("\nmcp_supabase_apply_migration(\n")
    print(f'    name="{migration_name}",\n')
    print(f'    query="""{sql}"""\n')
    print(")\n")
    print("=" * 80 + "\n")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Convert Alembic migrations to SQL for Supabase"
    )
    parser.add_argument(
        "revision", nargs="?", help="Specific Alembic revision ID (default: head)"
    )
    parser.add_argument(
        "--apply", action="store_true", help="Show MCP command to apply migration"
    )
    parser.add_argument("--output-dir", type=str, help="Output directory for SQL files")
    parser.add_argument(
        "--no-save", action="store_true", help="Do not save SQL to file"
    )

    args = parser.parse_args()

    revision = args.revision
    migration_name = get_migration_name(revision)

    print(f"🔄 Generating SQL for migration: {migration_name}")
    if revision:
        print(f"   Revision: {revision}")

    try:
        # Generate SQL
        sql = get_migration_sql(revision)

        if not sql.strip():
            print("⚠️  No SQL generated. Migration may already be applied.")
            return

        # Format for Supabase
        formatted_sql = format_sql_for_supabase(sql)

        # Save to file
        if not args.no_save:
            output_dir = Path(args.output_dir) if args.output_dir else None
            save_sql_to_file(formatted_sql, migration_name, output_dir)

        # Show SQL preview
        print("\n📄 SQL Preview (first 500 chars):")
        print("-" * 80)
        print(formatted_sql[:500])
        if len(formatted_sql) > 500:
            print(f"\n... ({len(formatted_sql) - 500} more characters)")
        print("-" * 80)

        # Show MCP command if requested
        if args.apply:
            apply_via_mcp(formatted_sql, migration_name)

        print(f"\n✅ Successfully generated SQL for {migration_name}")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
