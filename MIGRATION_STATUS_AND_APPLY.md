# Migration Status Check and Apply

## Step 1: Check Current Migration Status

Run these SQL queries via Supabase MCP to check current status:

```sql
-- Check current Alembic version
SELECT version_num FROM alembic_version ORDER BY version_num DESC LIMIT 1;

-- Check if platform_settings table exists
SELECT EXISTS (
    SELECT FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_name = 'platform_settings'
) AS table_exists;
```

## Step 2: Migration Chain Reference

Expected migration chain:
1. `e2412789c190` - Initialize models
2. `9c0a54914c78` - Add max length
3. `d98dd8ec85a3` - Replace id integers with UUID
4. `1a31ce608336` - Add cascade delete
5. `c4cd6f5a4f64` - Add all PRD models
6. `add_user_connector_connection` - Add user connector connection
7. `c1d1196b0e7d` - Enable RLS on all tables
8. `20250102000000` - Add platform_settings table ⬅️ **PENDING**

## Step 3: Apply Migration

SQL migration file ready: `backend/migrations/supabase/20250102000000_add_platform_settings_table.sql`

Apply via Supabase MCP using the command shown below.

## Step 4: Update Alembic Version

After migration succeeds, update Alembic version:
```sql
UPDATE alembic_version SET version_num = '20250102000000';
```
