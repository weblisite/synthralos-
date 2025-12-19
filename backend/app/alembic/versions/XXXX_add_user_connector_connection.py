"""Add user_connector_connection table

Revision ID: add_user_connector_connection
Revises: c4cd6f5a4f64
Create Date: 2025-01-19

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import UUID

# revision identifiers, used by Alembic.
revision = 'add_user_connector_connection'
down_revision = 'c4cd6f5a4f64'  # Update this with your latest migration revision
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create user_connector_connection table
    op.create_table(
        'user_connector_connection',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('connector_id', UUID(as_uuid=True), nullable=False),
        sa.Column('nango_connection_id', sa.String(), nullable=False, unique=True),
        sa.Column('status', sa.String(), nullable=False, server_default='pending'),
        sa.Column('connected_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('disconnected_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_synced_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('config', postgresql.JSONB, nullable=True),
        sa.Column('last_error', sa.String(), nullable=True),
        sa.Column('error_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['connector_id'], ['connector.id'], ondelete='CASCADE'),
    )
    
    # Create indexes
    op.create_index('ix_user_connector_connection_user_id', 'user_connector_connection', ['user_id'])
    op.create_index('ix_user_connector_connection_connector_id', 'user_connector_connection', ['connector_id'])
    op.create_index('ix_user_connector_connection_nango_connection_id', 'user_connector_connection', ['nango_connection_id'])
    op.create_index('ix_user_connector_connection_status', 'user_connector_connection', ['status'])
    
    # Create composite index for common queries
    op.create_index('ix_user_connector_connection_user_connector', 'user_connector_connection', ['user_id', 'connector_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_user_connector_connection_user_connector', table_name='user_connector_connection')
    op.drop_index('ix_user_connector_connection_status', table_name='user_connector_connection')
    op.drop_index('ix_user_connector_connection_nango_connection_id', table_name='user_connector_connection')
    op.drop_index('ix_user_connector_connection_connector_id', table_name='user_connector_connection')
    op.drop_index('ix_user_connector_connection_user_id', table_name='user_connector_connection')
    
    # Drop table
    op.drop_table('user_connector_connection')


