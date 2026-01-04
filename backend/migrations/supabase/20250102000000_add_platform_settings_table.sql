-- Migration: add_platform_settings_table
-- Revision ID: 20250102000000
-- Revises: c1d1196b0e7d
-- Create Date: 2025-01-02 00:00:00.000000

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
-- Allow all authenticated users to read platform settings
CREATE POLICY "platform_settings_select" ON platform_settings
    FOR SELECT
    USING (true);

-- Only superusers can insert/update/delete platform settings
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

-- Update Alembic version tracking
-- Note: This will be done separately after verifying the migration succeeded
