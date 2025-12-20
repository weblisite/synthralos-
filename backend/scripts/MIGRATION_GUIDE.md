# Alembic to Supabase Migration Guide

## Quick Start

### 1. Create Alembic Migration
```bash
cd backend
source .venv/bin/activate
alembic revision --autogenerate -m "your_migration_name"
```

### 2. Convert to SQL for Supabase
```bash
# Generate SQL for latest migration
python scripts/alembic_to_supabase.py

# Generate SQL for specific migration
python scripts/alembic_to_supabase.py <revision_id>

# Generate SQL and show MCP command
python scripts/alembic_to_supabase.py --apply
```

### 3. Review Generated SQL
Check `backend/migrations/supabase/{migration_name}.sql`

### 4. Apply via Supabase MCP
Use the MCP command shown, or manually:
```python
mcp_supabase_apply_migration(
    name="your_migration_name",
    query="""<SQL_CONTENT>"""
)
```

## Script Details

### `alembic_to_supabase.py`

**Features:**
- ✅ Converts Alembic Python migrations to raw SQL
- ✅ Converts JSON → JSONB for PostgreSQL
- ✅ Removes Alembic-specific tracking
- ✅ Formats SQL for Supabase
- ✅ Saves to `migrations/supabase/` directory
- ✅ Shows MCP command for easy copy-paste

**Options:**
- `revision` - Specific Alembic revision ID (default: head)
- `--apply` - Show MCP command to apply migration
- `--output-dir` - Custom output directory
- `--no-save` - Don't save to file (preview only)

### `apply_supabase_migration.py`

**Features:**
- Reads SQL file and generates MCP command
- Useful for re-applying migrations

**Usage:**
```bash
python scripts/apply_supabase_migration.py migrations/supabase/add_all_prd_models.sql
```

## Why Convert?

1. **Alembic** = Python code → Database-agnostic → Generates SQL at runtime
2. **Supabase MCP** = Requires raw SQL → PostgreSQL-specific → Direct execution

Both produce the same result, but Supabase MCP needs SQL directly.

## Example Workflow

```bash
# 1. Create migration
alembic revision --autogenerate -m "add_user_preferences"

# 2. Edit migration file if needed
# backend/app/alembic/versions/xxxxx_add_user_preferences.py

# 3. Convert to SQL
python scripts/alembic_to_supabase.py --apply

# 4. Review SQL file
cat migrations/supabase/add_user_preferences.sql

# 5. Apply via Supabase MCP (in Cursor)
# Copy the MCP command from step 3 and execute
```

## Notes

- ✅ Always review generated SQL before applying
- ✅ Alembic tracks migrations in `alembic_version` table
- ✅ Supabase tracks migrations in its own system
- ✅ Both systems should stay in sync
- ✅ JSON is automatically converted to JSONB
- ✅ UUID columns get `DEFAULT gen_random_uuid()` when appropriate

## Troubleshooting

**Issue:** Script generates SQL for all migrations, not just one
- **Solution:** Specify the revision ID explicitly

**Issue:** JSON not converted to JSONB
- **Solution:** Regenerate the SQL file (script was updated)

**Issue:** Migration already applied
- **Solution:** Check Supabase migrations list before applying
