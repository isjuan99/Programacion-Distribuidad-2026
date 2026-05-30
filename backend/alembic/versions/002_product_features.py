"""add bundle_items table, review images, is_bundle to products

Revision ID: 002_product_features
Revises: 001_auth_user
Create Date: 2026-05-29
"""
from alembic import op
import sqlalchemy as sa

revision = '002_product_features'
down_revision = '001_auth_user'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('products', sa.Column('is_bundle', sa.Boolean(), nullable=True, server_default='false'))
    op.create_table(
        'bundle_items',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('bundle_id', sa.Integer(), sa.ForeignKey('products.id', ondelete='CASCADE'), nullable=False),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id', ondelete='CASCADE'), nullable=False),
        sa.Column('variant_id', sa.Integer(), sa.ForeignKey('product_variants.id', ondelete='SET NULL'), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='1'),
    )
    op.add_column('reviews', sa.Column('images', sa.JSON(), nullable=True))


def downgrade():
    op.drop_column('reviews', 'images')
    op.drop_table('bundle_items')
    op.drop_column('products', 'is_bundle')
