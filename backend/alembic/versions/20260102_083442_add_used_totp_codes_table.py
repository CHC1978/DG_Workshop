"""add_used_totp_codes_table

Revision ID: 512daa0f6ca2
Revises: 2ca4b4a028dd
Create Date: 2026-01-02 08:34:42.125031

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '512daa0f6ca2'
down_revision = '2ca4b4a028dd'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 建立 used_totp_codes 表 - TOTP 重播保護
    op.create_table('used_totp_codes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('code_hash', sa.String(length=64), nullable=False),
    sa.Column('used_at', sa.DateTime(), nullable=False),
    sa.Column('expires_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_used_totp_codes_code_hash'), 'used_totp_codes', ['code_hash'], unique=False)
    op.create_index('ix_used_totp_codes_expires', 'used_totp_codes', ['expires_at'], unique=False)
    op.create_index(op.f('ix_used_totp_codes_id'), 'used_totp_codes', ['id'], unique=False)
    op.create_index('ix_used_totp_codes_user_hash', 'used_totp_codes', ['user_id', 'code_hash'], unique=False)
    op.create_index(op.f('ix_used_totp_codes_user_id'), 'used_totp_codes', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_used_totp_codes_user_id'), table_name='used_totp_codes')
    op.drop_index('ix_used_totp_codes_user_hash', table_name='used_totp_codes')
    op.drop_index(op.f('ix_used_totp_codes_id'), table_name='used_totp_codes')
    op.drop_index('ix_used_totp_codes_expires', table_name='used_totp_codes')
    op.drop_index(op.f('ix_used_totp_codes_code_hash'), table_name='used_totp_codes')
    op.drop_table('used_totp_codes')
