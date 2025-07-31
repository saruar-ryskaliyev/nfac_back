"""create quizzes table

Revision ID: 975a9a91fdd9
Revises: c5bef0e20b07
Create Date: 2025-07-31 19:37:30.692861

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '975a9a91fdd9'
down_revision = 'c5bef0e20b07'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SEQUENCE quizzes_id_seq")
    op.create_table('quizzes',
    sa.Column('id', sa.Integer(), nullable=False, server_default=sa.text("nextval('quizzes_id_seq'::regclass)")),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('creator_id', sa.Integer(), nullable=False),
    sa.Column('is_public', sa.Boolean(), nullable=False, server_default=sa.text('true')),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True, server_default=sa.text('now()')),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['creator_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('quizzes')
    op.execute("DROP SEQUENCE IF EXISTS quizzes_id_seq")
