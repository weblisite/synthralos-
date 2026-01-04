"""add_clerk_user_id_and_metadata

Revision ID: 20250104000000
Revises: 20250102000000
Create Date: 2025-01-04 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250104000000'
down_revision = '20250102000000'
branch_labels = None
depends_on = None


def upgrade():
    # Check if columns exist before adding them (idempotent migration)
    # This handles the case where migration was already applied via Supabase MCP

    # Check and add clerk_user_id column
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('user')]

    if 'clerk_user_id' not in columns:
        op.add_column('user', sa.Column('clerk_user_id', sa.String(length=255), nullable=True))

    # Check and create index on clerk_user_id
    indexes = [idx['name'] for idx in inspector.get_indexes('user')]
    if 'ix_user_clerk_user_id' not in indexes:
        op.create_index(op.f('ix_user_clerk_user_id'), 'user', ['clerk_user_id'], unique=True)

    # Check and add phone_number column
    if 'phone_number' not in columns:
        op.add_column('user', sa.Column('phone_number', sa.String(length=50), nullable=True))

    # Check and add email_verified column
    if 'email_verified' not in columns:
        op.add_column('user', sa.Column('email_verified', sa.Boolean(), nullable=False, server_default='false'))

    # Check and add clerk_metadata column
    if 'clerk_metadata' not in columns:
        op.add_column('user', sa.Column('clerk_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'))

    # Check and create index on email_verified
    if 'ix_user_email_verified' not in indexes:
        op.create_index(op.f('ix_user_email_verified'), 'user', ['email_verified'], unique=False)


def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_user_email_verified'), table_name='user')
    op.drop_index(op.f('ix_user_clerk_user_id'), table_name='user')

    # Drop columns
    op.drop_column('user', 'clerk_metadata')
    op.drop_column('user', 'email_verified')
    op.drop_column('user', 'phone_number')
    op.drop_column('user', 'clerk_user_id')
