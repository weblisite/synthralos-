-- Check current Alembic version
SELECT version_num FROM alembic_version ORDER BY version_num DESC LIMIT 1;

-- Check if platform_settings table exists
SELECT EXISTS (
    SELECT FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_name = 'platform_settings'
) AS table_exists;

-- List all migrations in order (for reference)
-- Expected chain:
-- e2412789c190 -> 9c0a54914c78 -> d98dd8ec85a3 -> 1a31ce608336 -> c4cd6f5a4f64 -> add_user_connector_connection -> c1d1196b0e7d -> 20250102000000
