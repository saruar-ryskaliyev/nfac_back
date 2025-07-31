"""add total_score to user

Revision ID: c5bef0e20b07
Revises: b2437a6523e3
Create Date: 2025-07-31 19:29:17.596582

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c5bef0e20b07'
down_revision = 'b2437a6523e3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('total_score', sa.Integer(), nullable=False, server_default=sa.text('0')))


def downgrade() -> None:
    op.drop_column('users', 'total_score')
