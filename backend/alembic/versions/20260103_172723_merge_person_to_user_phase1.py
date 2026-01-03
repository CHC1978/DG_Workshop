"""merge_person_to_user_phase1

Revision ID: 02fc1f9e38e8
Revises: aa25ceedd4c2
Create Date: 2026-01-03 17:27:23.114054

Person Location 合併到 User 第一階段：
- User 新增: employee_id, department, phone, photo_url
- Equipment 新增: assigned_user_id
- Location 新增: contact_user_id
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '02fc1f9e38e8'
down_revision = 'aa25ceedd4c2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # User 表新增欄位（從 Person Location 合併）
    op.add_column('users', sa.Column('employee_id', sa.String(length=30), nullable=True))
    op.add_column('users', sa.Column('department', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('phone', sa.String(length=50), nullable=True))
    op.add_column('users', sa.Column('photo_url', sa.String(length=500), nullable=True))
    op.create_index(op.f('ix_users_employee_id'), 'users', ['employee_id'], unique=True)

    # Equipment 表新增 assigned_user_id（設備負責人）
    op.add_column('equipments', sa.Column('assigned_user_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_equipments_assigned_user_id'), 'equipments', ['assigned_user_id'], unique=False)

    # Location 表新增 contact_user_id（聯繫人指向 User）
    op.add_column('locations', sa.Column('contact_user_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_locations_contact_user_id'), 'locations', ['contact_user_id'], unique=False)


def downgrade() -> None:
    # Location
    op.drop_index(op.f('ix_locations_contact_user_id'), table_name='locations')
    op.drop_column('locations', 'contact_user_id')

    # Equipment
    op.drop_index(op.f('ix_equipments_assigned_user_id'), table_name='equipments')
    op.drop_column('equipments', 'assigned_user_id')

    # User
    op.drop_index(op.f('ix_users_employee_id'), table_name='users')
    op.drop_column('users', 'photo_url')
    op.drop_column('users', 'phone')
    op.drop_column('users', 'department')
    op.drop_column('users', 'employee_id')
