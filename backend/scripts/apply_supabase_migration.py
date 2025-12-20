#!/usr/bin/env python3
"""
Apply SQL migration directly via Supabase MCP.

This script reads a SQL file and applies it via Supabase MCP.

Usage:
    python scripts/apply_supabase_migration.py <migration_file.sql> [--name migration_name]

Example:
    python scripts/apply_supabase_migration.py migrations/supabase/add_all_prd_models.sql
"""

import argparse
import sys
from pathlib import Path

# Note: This script is a helper that shows the MCP command
# Actual execution must be done via the MCP tool in Cursor


def read_sql_file(file_path: Path) -> str:
    """Read SQL file."""
    if not file_path.exists():
        raise FileNotFoundError(f"SQL file not found: {file_path}")

    with open(file_path) as f:
        return f.read()


def get_migration_name(file_path: Path) -> str:
    """Extract migration name from file path."""
    # Remove .sql extension and path
    name = file_path.stem
    # Convert to snake_case if needed
    name = name.replace("-", "_").replace(" ", "_")
    return name


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Apply SQL migration via Supabase MCP")
    parser.add_argument("sql_file", type=str, help="Path to SQL migration file")
    parser.add_argument(
        "--name", type=str, help="Migration name (default: filename without extension)"
    )

    args = parser.parse_args()

    sql_file = Path(args.sql_file)
    migration_name = args.name or get_migration_name(sql_file)

    try:
        # Read SQL
        sql = read_sql_file(sql_file)

        print("=" * 80)
        print("Supabase MCP Migration Command")
        print("=" * 80)
        print(f"\nMigration Name: {migration_name}")
        print(f"SQL File: {sql_file}")
        print(f"SQL Length: {len(sql)} characters")
        print("\n" + "=" * 80)
        print("Copy and use this in Cursor with MCP:")
        print("=" * 80)
        print("\nmcp_supabase_apply_migration(")
        print(f'    name="{migration_name}",')
        print('    query="""')
        print(sql)
        print('"""')
        print(")\n")
        print("=" * 80)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
