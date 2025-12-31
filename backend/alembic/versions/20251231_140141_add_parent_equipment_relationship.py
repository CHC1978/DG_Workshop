"""add_parent_equipment_relationship

Revision ID: 6063a4ee1ce2
Revises: f6d78c052629
Create Date: 2025-12-31 14:01:41.080577

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6063a4ee1ce2'
down_revision = 'f6d78c052629'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add parent_equipment_id column to equipments table
    op.add_column('equipments', sa.Column('parent_equipment_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_equipments_parent_equipment_id'), 'equipments', ['parent_equipment_id'], unique=False)

    # Create foreign key constraint (SQLite limitation: may need to be handled at application level)
    # For SQLite, we'll handle FK at application level as it doesn't support ALTER TABLE ADD CONSTRAINT

    # 2. Migrate data from sub_equipments to equipments
    # This will be done via a data migration script to maintain data integrity
    # See: backend/scripts/migrate_sub_equipments_to_equipments.py

    # Note: We keep the sub_equipments table for now as a backup
    # It can be dropped after confirming successful migration


def downgrade() -> None:
    # Remove parent_equipment_id column
    op.drop_index(op.f('ix_equipments_parent_equipment_id'), table_name='equipments')
    op.drop_column('equipments', 'parent_equipment_id')

    # Note: This downgrade does NOT restore migrated sub_equipments data
    # Make sure to backup before upgrading
