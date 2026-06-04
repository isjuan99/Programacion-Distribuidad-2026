# backend/alembic/versions/005_add_return_fields.py
"""add tracking_number, return_address, refund_type to returns

Revision ID: 005_add_return_fields
Revises: 004_offers_compare_price
Create Date: 2026-06-03
"""
from alembic import op
import sqlalchemy as sa

revision = '005_add_return_fields'
down_revision = '004_offers_compare_price'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('returns', sa.Column('tracking_number', sa.String(100), nullable=True))
    op.add_column('returns', sa.Column('return_address', sa.String(500), nullable=True))
    op.add_column('returns', sa.Column('refund_type', sa.String(20), nullable=True))


def downgrade():
    op.drop_column('returns', 'refund_type')
    op.drop_column('returns', 'return_address')
    op.drop_column('returns', 'tracking_number')
