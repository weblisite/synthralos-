"""add_platform_settings_table

Revision ID: 20250102000000
Revises: c1d1196b0e7d
Create Date: 2025-01-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250102000000'
down_revision = 'c1d1196b0e7d'
branch_labels = None
depends_on = None


def upgrade():
    # Create platform_settings table
    op.create_table('platform_settings',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('key', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
    sa.Column('value', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
    sa.Column('updated_by', sa.Uuid(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('key'),
    sa.ForeignKeyConstraint(['updated_by'], ['user.id'], ondelete='SET NULL'),
    )

    # Create index on key for faster lookups
    op.create_index(op.f('ix_platform_settings_key'), 'platform_settings', ['key'], unique=False)

    # Enable RLS
    op.execute('ALTER TABLE platform_settings ENABLE ROW LEVEL SECURITY')

    # Create RLS policies
    # Allow all authenticated users to read platform settings
    op.execute("""
        CREATE POLICY "platform_settings_select" ON platform_settings
        FOR SELECT
        USING (true)
    """)

    # Only superusers can insert/update/delete platform settings
    op.execute("""
        CREATE POLICY "platform_settings_insert" ON platform_settings
        FOR INSERT
        WITH CHECK (
            EXISTS (
                SELECT 1 FROM "user"
                WHERE "user".id = auth.uid()
                AND "user".is_superuser = true
            )
        )
    """)

    op.execute("""
        CREATE POLICY "platform_settings_update" ON platform_settings
        FOR UPDATE
        USING (
            EXISTS (
                SELECT 1 FROM "user"
                WHERE "user".id = auth.uid()
                AND "user".is_superuser = true
            )
        )
    """)

    op.execute("""
        CREATE POLICY "platform_settings_delete" ON platform_settings
        FOR DELETE
        USING (
            EXISTS (
                SELECT 1 FROM "user"
                WHERE "user".id = auth.uid()
                AND "user".is_superuser = true
            )
        )
    """)


def downgrade():
    # Drop RLS policies
    op.execute('DROP POLICY IF EXISTS "platform_settings_delete" ON platform_settings')
    op.execute('DROP POLICY IF EXISTS "platform_settings_update" ON platform_settings')
    op.execute('DROP POLICY IF EXISTS "platform_settings_insert" ON platform_settings')
    op.execute('DROP POLICY IF EXISTS "platform_settings_select" ON platform_settings')

    # Drop index
    op.drop_index(op.f('ix_platform_settings_key'), table_name='platform_settings')

    # Drop table
    op.drop_table('platform_settings')
