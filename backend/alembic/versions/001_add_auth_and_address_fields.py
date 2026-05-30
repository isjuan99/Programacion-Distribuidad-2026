"""add verification and oauth fields to users, extend addresses

Revision ID: 001_auth_user
Revises:
Create Date: 2026-05-29
"""
from alembic import op
import sqlalchemy as sa

revision = '001_auth_user'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('verification_token', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('google_id', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('apple_id', sa.String(255), nullable=True))
    op.add_column('addresses', sa.Column('phone', sa.String(20), nullable=True))
    op.add_column('addresses', sa.Column('state', sa.String(100), nullable=True))
    op.add_column('addresses', sa.Column('first_name', sa.String(100), nullable=True))
    op.add_column('addresses', sa.Column('last_name', sa.String(100), nullable=True))


def downgrade():
    op.drop_column('users', 'verification_token')
    op.drop_column('users', 'google_id')
    op.drop_column('users', 'apple_id')
    op.drop_column('addresses', 'phone')
    op.drop_column('addresses', 'state')
    op.drop_column('addresses', 'first_name')
    op.drop_column('addresses', 'last_name')
