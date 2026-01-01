"""Add backup_codes table

Revision ID: 218259ca4894
Revises: 1599c9e272f3
Create Date: 2026-01-01 17:26:11.603422

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '218259ca4894'
down_revision = '1599c9e272f3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create backup_codes table for 2FA recovery
    op.create_table('backup_codes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('code_hash', sa.String(length=255), nullable=False),
        sa.Column('is_used', sa.Boolean(), nullable=False),
        sa.Column('used_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_backup_codes_id'), 'backup_codes', ['id'], unique=False)
    op.create_index(op.f('ix_backup_codes_user_id'), 'backup_codes', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_backup_codes_user_id'), table_name='backup_codes')
    op.drop_index(op.f('ix_backup_codes_id'), table_name='backup_codes')
    op.drop_table('backup_codes')
