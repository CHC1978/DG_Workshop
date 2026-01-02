"""add_refresh_tokens_table

Revision ID: 2ca4b4a028dd
Revises: 218259ca4894
Create Date: 2026-01-02 08:18:38.827100

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2ca4b4a028dd'
down_revision = '218259ca4894'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 建立 refresh_tokens 表
    op.create_table('refresh_tokens',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('token_hash', sa.String(length=64), nullable=False),
    sa.Column('token_family', sa.String(length=36), nullable=False),
    sa.Column('device_fingerprint', sa.String(length=255), nullable=True),
    sa.Column('user_agent', sa.String(length=500), nullable=True),
    sa.Column('ip_address', sa.String(length=50), nullable=True),
    sa.Column('expires_at', sa.DateTime(), nullable=False),
    sa.Column('is_revoked', sa.Boolean(), nullable=False),
    sa.Column('revoked_at', sa.DateTime(), nullable=True),
    sa.Column('revoked_reason', sa.String(length=100), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('last_used_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_refresh_tokens_family', 'refresh_tokens', ['token_family'], unique=False)
    op.create_index(op.f('ix_refresh_tokens_id'), 'refresh_tokens', ['id'], unique=False)
    op.create_index(op.f('ix_refresh_tokens_token_hash'), 'refresh_tokens', ['token_hash'], unique=True)
    op.create_index(op.f('ix_refresh_tokens_user_id'), 'refresh_tokens', ['user_id'], unique=False)
    op.create_index('ix_refresh_tokens_user_token', 'refresh_tokens', ['user_id', 'token_hash'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_refresh_tokens_user_token', table_name='refresh_tokens')
    op.drop_index(op.f('ix_refresh_tokens_user_id'), table_name='refresh_tokens')
    op.drop_index(op.f('ix_refresh_tokens_token_hash'), table_name='refresh_tokens')
    op.drop_index(op.f('ix_refresh_tokens_id'), table_name='refresh_tokens')
    op.drop_index('ix_refresh_tokens_family', table_name='refresh_tokens')
    op.drop_table('refresh_tokens')
