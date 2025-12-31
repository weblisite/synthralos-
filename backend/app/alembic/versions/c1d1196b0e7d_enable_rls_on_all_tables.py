"""enable_rls_on_all_tables

Revision ID: c1d1196b0e7d
Revises: add_user_connector_connection
Create Date: 2025-12-30 10:53:43.937760

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = 'c1d1196b0e7d'
down_revision = 'add_user_connector_connection'
branch_labels = None
depends_on = None


# List of all tables that need RLS enabled
# These match the tables reported by Supabase linter
# Note: alembic_version is excluded as it's managed by Alembic
TABLES = [
    'connector',
    'contentchecksum',
    'domainprofile',
    'alembic_version',  # Alembic version table (optional, but Supabase flagged it)
    'user',
    'eventlog',
    'modelcostlog',
    'proxylog',
    'agenttask',
    'agenttasklog',
    'browsersession',
    'browseraction',
    'agentcontextcache',
    'agentframeworkconfig',
    'changedetection',
    'codeexecution',
    'codesandbox',
    'codetoolregistry',
    'connectorversion',
    'ocrjob',
    'ocrdocument',
    'ocrresult',
    'osintstream',
    'osintalert',
    'osintsignal',
    'ragindex',
    'scrapejob',
    'scraperesult',
    'workflow',
    'ragdocument',
    'ragfinetunejob',
    'ragquery',
    'webhooksubscription',
    'workflowexecution',
    'workflownode',
    'workflowschedule',
    'executionlog',
    'ragfinetunedataset',
    'ragswitchlog',
    'workflowsignal',
    'user_connector_connection',
    'user_api_key',
    'team',
    'workflowwebhooksubscription',
    'teammember',
    'teaminvitation',
    'emailtemplate',
    'user_session',
    'user_preferences',
    'login_history',
    'system_alert',  # Added for completeness
]


def upgrade():
    """
    Enable Row Level Security (RLS) on all tables.

    Since this application uses direct database connections (not PostgREST),
    we enable RLS but create permissive policies for the service role (backend).

    IMPORTANT NOTES:
    1. The service_role in Supabase bypasses RLS by default, so enabling RLS
       won't affect backend operations that use direct connections.
    2. This migration enables RLS as a defense-in-depth security measure.
    3. If you use PostgREST (via SUPABASE_ANON_KEY), you may want to add
       more restrictive policies for anon/authenticated roles.

    This provides defense-in-depth security while allowing the backend API
    to function normally.
    """
    # Enable RLS on all tables
    connection = op.get_bind()

    for table in TABLES:
        try:
            # Check if table exists before enabling RLS
            # This prevents errors if a table hasn't been created yet
            result = connection.execute(
                text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_schema = 'public'
                        AND table_name = :table_name
                    );
                """),
                {"table_name": table}
            )

            if not result.scalar():
                print(f"Info: Table {table} does not exist, skipping RLS enablement")
                continue

            # Enable RLS (idempotent - safe to run multiple times)
            op.execute(text(f'ALTER TABLE "{table}" ENABLE ROW LEVEL SECURITY;'))

            # Create policy that allows service_role (backend) full access
            # Note: service_role bypasses RLS by default, but this ensures
            # RLS is enabled and provides a fallback if service_role is not used
            op.execute(text(f'DROP POLICY IF EXISTS "{table}_service_role_policy" ON "{table}";'))
            op.execute(text(f"""
                CREATE POLICY "{table}_service_role_policy" ON "{table}"
                FOR ALL
                TO service_role
                USING (true)
                WITH CHECK (true);
            """))

            # Optionally: Restrict anon/authenticated roles if PostgREST is not used
            # Uncomment these if you want to completely block PostgREST access:
            # op.execute(text(f'DROP POLICY IF EXISTS "{table}_deny_anon_policy" ON "{table}";'))
            # op.execute(text(f"""
            #     CREATE POLICY "{table}_deny_anon_policy" ON "{table}"
            #     FOR ALL
            #     TO anon
            #     USING (false)
            #     WITH CHECK (false);
            # """))
            # op.execute(text(f'DROP POLICY IF EXISTS "{table}_deny_authenticated_policy" ON "{table}";'))
            # op.execute(text(f"""
            #     CREATE POLICY "{table}_deny_authenticated_policy" ON "{table}"
            #     FOR ALL
            #     TO authenticated
            #     USING (false)
            #     WITH CHECK (false);
            # """))

        except Exception as e:
            # Log error but continue with other tables
            # Some tables might not exist or already have RLS enabled
            print(f"Warning: Could not enable RLS on {table}: {e}")
            # Continue with next table - don't rollback as it would abort the transaction
            pass


def downgrade():
    """
    Disable RLS on all tables (not recommended for production).
    """
    for table in TABLES:
        try:
            # Drop policies first
            op.execute(text(f'DROP POLICY IF EXISTS "{table}_service_role_policy" ON "{table}";'))
            # op.execute(text(f'DROP POLICY IF EXISTS "{table}_deny_anon_policy" ON "{table}";'))
            # op.execute(text(f'DROP POLICY IF EXISTS "{table}_deny_authenticated_policy" ON "{table}";'))

            # Disable RLS
            op.execute(text(f'ALTER TABLE "{table}" DISABLE ROW LEVEL SECURITY;'))
        except Exception:
            # Ignore errors if table doesn't exist or RLS not enabled
            pass
