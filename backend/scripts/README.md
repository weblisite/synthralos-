# Migration Scripts

Scripts to help convert and apply Alembic migrations to Supabase.

## Scripts

### `alembic_to_supabase.py`

Converts Alembic migrations to SQL format for Supabase MCP.

**Usage:**
```bash
# Generate SQL for latest migration (head)
python scripts/alembic_to_supabase.py

# Generate SQL for specific migration
python scripts/alembic_to_supabase.py c4cd6f5a4f64

# Generate SQL and show MCP command
python scripts/alembic_to_supabase.py --apply

# Save to custom directory
python scripts/alembic_to_supabase.py --output-dir migrations/supabase

# Don't save to file (just show preview)
python scripts/alembic_to_supabase.py --no-save
```

**Output:**
- Saves SQL to `backend/migrations/supabase/{migration_name}.sql`
- Shows SQL preview
- Optionally shows MCP command to apply

### `apply_supabase_migration.py`

Helper script to generate MCP command from SQL file.

**Usage:**
```bash
python scripts/apply_supabase_migration.py migrations/supabase/add_all_prd_models.sql
python scripts/apply_supabase_migration.py migrations/supabase/add_all_prd_models.sql --name custom_name
```

## Workflow

### 1. Create Alembic Migration
```bash
cd backend
source .venv/bin/activate
alembic revision --autogenerate -m "add_new_feature"
```

### 2. Convert to SQL
```bash
python scripts/alembic_to_supabase.py --apply
```

### 3. Review SQL
Check the generated SQL file in `migrations/supabase/`

### 4. Apply via Supabase MCP
Use the MCP command shown, or:
```bash
python scripts/apply_supabase_migration.py migrations/supabase/add_new_feature.sql
```

Then copy the MCP command and execute it in Cursor.

## Notes

- Alembic migrations are Python-based and database-agnostic
- SQL migrations are database-specific (PostgreSQL for Supabase)
- Both should produce the same schema
- Alembic tracks migrations in `alembic_version` table
- Supabase tracks migrations in its own system
- Always review generated SQL before applying
