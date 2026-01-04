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
    # Add clerk_user_id column to user table
    op.add_column('user', sa.Column('clerk_user_id', sa.String(length=255), nullable=True))

    # Add index on clerk_user_id for faster lookups
    op.create_index(op.f('ix_user_clerk_user_id'), 'user', ['clerk_user_id'], unique=True)

    # Add phone_number column
    op.add_column('user', sa.Column('phone_number', sa.String(length=50), nullable=True))

    # Add email_verified column
    op.add_column('user', sa.Column('email_verified', sa.Boolean(), nullable=False, server_default='false'))

    # Add clerk_metadata column (JSONB for storing additional Clerk metadata)
    op.add_column('user', sa.Column('clerk_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'))

    # Create index on email_verified for filtering
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
