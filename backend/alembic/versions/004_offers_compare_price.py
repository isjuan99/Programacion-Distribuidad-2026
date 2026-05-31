"""add compare_at_price to product_variants for offers/discounts

Revision ID: 004_offers_compare_price
Revises: 003_orders_operations
Create Date: 2026-05-30
"""
from alembic import op
import sqlalchemy as sa

revision = '004_offers_compare_price'
down_revision = '003_orders_operations'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'product_variants',
        sa.Column('compare_at_price', sa.Float(), nullable=True)
    )


def downgrade():
    op.drop_column('product_variants', 'compare_at_price')
