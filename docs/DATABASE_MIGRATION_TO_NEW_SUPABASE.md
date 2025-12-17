# Database Migration to New Supabase Project

## Current Status

✅ **Supabase MCP Connection Verified**
- Project URL: `https://lorefpaifkembnzmlodm.supabase.co`
- Database connection: Working
- Current state: Empty database (no tables, no migrations)

## Migration Plan

### Step 1: Update Environment Variables

Update `.env` file to point to the new Supabase project:

```bash
# Old Supabase Project
# SUPABASE_URL=https://mvtchmenmquqvrpfwoml.supabase.co

# New Supabase Project
SUPABASE_URL=https://lorefpaifkembnzmlodm.supabase.co
SUPABASE_ANON_KEY=<your-new-anon-key>
SUPABASE_DB_URL=postgresql://postgres.lorefpaifkembnzmlodm:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
```

### Step 2: Run Alembic Migrations

Run all migrations in order on the new database:

```bash
cd backend
source .venv/bin/activate  # or your virtual environment
alembic upgrade head
```

### Step 3: Verify Migration

Check that all tables were created:

```bash
# Using Supabase MCP
list_tables with schemas: ["public"]

# Or using SQL
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
```

### Step 4: Verify Alembic Version

Check that Alembic version is set correctly:

```bash
# Using Supabase MCP
execute_sql: SELECT version_num FROM alembic_version;

# Should return: c4cd6f5a4f64
```

## Migration Order

The migrations will run in this order:
1. `e2412789c190` - Initialize models (user, item tables)
2. `9c0a54914c78` - Add max length for string fields
3. `d98dd8ec85a3` - Replace integer IDs with UUIDs
4. `1a31ce608336` - Add cascade delete relationships
5. `c4cd6f5a4f64` - Add all PRD models (latest)

## Important Notes

⚠️ **Note about Item table**: The first migration creates an `item` table, but we've removed Items functionality from the codebase. The migration will still create the table, but it won't be used. You can drop it later if needed.

## After Migration

1. Update Render environment variables to use new Supabase project
2. Update frontend `.env` to use new Supabase project
3. Test all functionality to ensure everything works
4. (Optional) Drop unused `item` table if desired

