# Migration Check and Apply Guide

## Current Migration Status

### Migration Chain (from codebase):
1. `e2412789c190` - Initialize models (down_revision: None)
2. `9c0a54914c78` - Add max length (down_revision: e2412789c190)
3. `d98dd8ec85a3` - Replace id integers with UUID (down_revision: 9c0a54914c78)
4. `1a31ce608336` - Add cascade delete (down_revision: d98dd8ec85a3)
5. `c4cd6f5a4f64` - Add all PRD models (down_revision: 1a31ce608336)
6. `add_user_connector_connection` - Add user connector connection (down_revision: c4cd6f5a4f64)
7. `c1d1196b0e7d` - Enable RLS on all tables (down_revision: add_user_connector_connection)
8. `20250102000000` - Add platform_settings table (down_revision: c1d1196b0e7d) ⬅️ **PENDING**

## Steps to Check and Apply

### 1. Check Current Alembic Version in Supabase

Run this SQL query via Supabase MCP:
```sql
SELECT version_num FROM alembic_version ORDER BY version_num DESC LIMIT 1;
```

### 2. Check if platform_settings Table Exists

```sql
SELECT EXISTS (
    SELECT FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_name = 'platform_settings'
);
```

### 3. Check All Pending Migrations

Compare current version with migration chain above to identify pending migrations.

### 4. Apply Migration via Supabase MCP

The SQL migration file is ready at: `backend/migrations/supabase/20250102000000_add_platform_settings_table.sql`

Apply using Supabase MCP:
```python
mcp_supabase_apply_migration(
    name="add_platform_settings_table",
    query="""
-- Create platform_settings table
CREATE TABLE IF NOT EXISTS platform_settings (
    id UUID NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
    key VARCHAR(255) NOT NULL UNIQUE,
    value JSONB NOT NULL DEFAULT '{}',
    description VARCHAR(500),
    updated_by UUID,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now(),
    CONSTRAINT fk_platform_settings_updated_by FOREIGN KEY (updated_by) REFERENCES "user"(id) ON DELETE SET NULL
);

-- Create index on key for faster lookups
CREATE INDEX IF NOT EXISTS ix_platform_settings_key ON platform_settings(key);

-- Enable RLS
ALTER TABLE platform_settings ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist (for idempotency)
DROP POLICY IF EXISTS "platform_settings_select" ON platform_settings;
DROP POLICY IF EXISTS "platform_settings_insert" ON platform_settings;
DROP POLICY IF EXISTS "platform_settings_update" ON platform_settings;
DROP POLICY IF EXISTS "platform_settings_delete" ON platform_settings;

-- Create RLS policies
CREATE POLICY "platform_settings_select" ON platform_settings
    FOR SELECT
    USING (true);

CREATE POLICY "platform_settings_insert" ON platform_settings
    FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM "user"
            WHERE "user".id = auth.uid()
            AND "user".is_superuser = true
        )
    );

CREATE POLICY "platform_settings_update" ON platform_settings
    FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM "user"
            WHERE "user".id = auth.uid()
            AND "user".is_superuser = true
        )
    );

CREATE POLICY "platform_settings_delete" ON platform_settings
    FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM "user"
            WHERE "user".id = auth.uid()
            AND "user".is_superuser = true
        )
    );
"""
)
```

### 5. Update Alembic Version Tracking

After migration succeeds, update Alembic version:
```sql
UPDATE alembic_version SET version_num = '20250102000000';
```

Or insert if it doesn't exist:
```sql
INSERT INTO alembic_version (version_num) VALUES ('20250102000000')
ON CONFLICT DO NOTHING;
```
