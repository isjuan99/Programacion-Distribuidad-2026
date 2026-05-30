"""add tracking fields to orders, returns table, stock_reservations table

Revision ID: 003_orders_operations
Revises: 002_product_features
Create Date: 2026-05-29
"""
from alembic import op
import sqlalchemy as sa

revision = '003_orders_operations'
down_revision = '002_product_features'
branch_labels = None
depends_on = None


def upgrade():
    # Tracking fields on orders
    op.add_column('orders', sa.Column('tracking_number', sa.String(100), nullable=True))
    op.add_column('orders', sa.Column('tracking_company', sa.String(100), nullable=True))
    op.add_column('orders', sa.Column('tracking_url', sa.String(500), nullable=True))

    # Returns table
    op.create_table(
        'returns',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('order_id', sa.Integer(), sa.ForeignKey('orders.id'), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('reason', sa.String(100), nullable=False),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('images', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('admin_notes', sa.Text(), nullable=True),
        sa.Column('refund_amount', sa.Float(), nullable=True),
        sa.Column('return_label_url', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    # Stock reservations table
    op.create_table(
        'stock_reservations',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('variant_id', sa.Integer(), sa.ForeignKey('product_variants.id'), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(255), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_stock_reservations_session_id', 'stock_reservations', ['session_id'])


def downgrade():
    op.drop_index('ix_stock_reservations_session_id', table_name='stock_reservations')
    op.drop_table('stock_reservations')
    op.drop_table('returns')
    op.drop_column('orders', 'tracking_url')
    op.drop_column('orders', 'tracking_company')
    op.drop_column('orders', 'tracking_number')
