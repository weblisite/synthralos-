# Row Level Security (RLS) Migration Guide

## Overview

This guide explains the RLS migration that enables Row Level Security on all database tables to address Supabase security linter warnings.

## What is RLS?

Row Level Security (RLS) is a PostgreSQL feature that allows you to control access to individual rows in a table based on the user executing a query. Supabase recommends enabling RLS on all tables in the `public` schema as a security best practice.

## Why Enable RLS?

Even though this application uses **direct database connections** (not PostgREST), enabling RLS provides:

1. **Defense-in-Depth Security**: Protects against accidental exposure via PostgREST
2. **Compliance**: Meets Supabase security recommendations
3. **Future-Proofing**: Ready if PostgREST is enabled later
4. **Security Auditing**: Satisfies security linter requirements

## Important Notes

### Service Role Bypasses RLS

The `service_role` in Supabase **bypasses RLS by default**. This means:

- ✅ **Backend operations are unaffected** - Direct database connections continue to work
- ✅ **No code changes required** - Application logic remains the same
- ✅ **RLS is enabled** - Provides security for PostgREST access (if enabled)

### PostgREST Access

If you use PostgREST (via `SUPABASE_ANON_KEY`), you may want to add more restrictive policies. The migration includes commented-out policies that can be enabled to block PostgREST access entirely.

## Migration Details

### Migration File

`backend/app/alembic/versions/c1d1196b0e7d_enable_rls_on_all_tables.py`

### What It Does

1. **Enables RLS** on all tables in the `public` schema
2. **Creates permissive policies** for `service_role` (allows full access)
3. **Includes commented policies** to restrict `anon`/`authenticated` roles (optional)

### Tables Affected

All tables reported by Supabase linter, including:
- User-related: `user`, `user_preferences`, `user_session`, `login_history`, `user_api_key`, `user_connector_connection`
- Workflow-related: `workflow`, `workflowexecution`, `workflownode`, `workflowschedule`, etc.
- Connector-related: `connector`, `connectorversion`
- Team-related: `team`, `teammember`, `teaminvitation`
- And 40+ other tables

## Running the Migration

### Local Development

```bash
cd backend
source .venv/bin/activate
alembic upgrade head
```

### Production (Render)

The migration will run automatically during deployment if Alembic is configured to run migrations on startup.

### Verify RLS is Enabled

```sql
-- Check if RLS is enabled on a table
SELECT tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
AND tablename = 'user';

-- Check policies on a table
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual
FROM pg_policies
WHERE tablename = 'user';
```

## Customizing Policies

### Block PostgREST Access

If you want to completely block PostgREST access, uncomment the policies in the migration:

```python
# Uncomment these in the migration:
op.execute(f"""
    DROP POLICY IF EXISTS "{table}_deny_anon_policy" ON "{table}";
    CREATE POLICY "{table}_deny_anon_policy" ON "{table}"
    FOR ALL
    TO anon
    USING (false)
    WITH CHECK (false);
""")
```

### Add User-Specific Policies

If you need user-specific access control, add policies like:

```sql
-- Example: Users can only see their own data
CREATE POLICY "user_own_data" ON "user_preferences"
FOR SELECT
TO authenticated
USING (auth.uid() = user_id);
```

## Troubleshooting

### Migration Fails: Table Doesn't Exist

**Error**: `relation "table_name" does not exist`

**Solution**: Ensure all previous migrations have run successfully:
```bash
alembic upgrade head
```

### Backend Can't Access Data

**Error**: Backend queries return empty results

**Solution**: This shouldn't happen because `service_role` bypasses RLS. If it does:
1. Verify you're using the service role connection string
2. Check that policies allow `service_role` access
3. Review migration logs for errors

### PostgREST Queries Fail

**Error**: PostgREST queries return 403 Forbidden

**Solution**: This is expected if you uncommented the deny policies. Either:
1. Comment out the deny policies, or
2. Create proper policies for `anon`/`authenticated` roles

## Rollback

If you need to rollback the migration:

```bash
alembic downgrade -1
```

This will:
1. Drop all RLS policies
2. Disable RLS on all tables

**Warning**: Rolling back removes security protections. Only do this if necessary.

## Security Best Practices

1. ✅ **Keep RLS Enabled**: Don't disable RLS unless absolutely necessary
2. ✅ **Review Policies Regularly**: Ensure policies match your access requirements
3. ✅ **Test PostgREST Access**: If using PostgREST, test with proper authentication
4. ✅ **Monitor Access Logs**: Review Supabase logs for unauthorized access attempts
5. ✅ **Use Service Role Carefully**: Only use service role for backend operations

## Related Documentation

- [Supabase RLS Documentation](https://supabase.com/docs/guides/database/postgres/row-level-security)
- [Supabase Database Linter](https://supabase.com/docs/guides/database/database-linter)
- [Alembic Migrations Guide](../backend/app/alembic/README.md)

## Support

If you encounter issues with the RLS migration:

1. Check migration logs: `alembic history`
2. Verify table existence: `SELECT tablename FROM pg_tables WHERE schemaname = 'public';`
3. Check RLS status: `SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = 'public';`
4. Review Supabase dashboard for errors
