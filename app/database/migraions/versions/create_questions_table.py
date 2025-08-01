"""create questions table

Revision ID: abc123def456
Revises: f8dc1cce87a0
Create Date: 2025-07-31 19:45:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "abc123def456"
down_revision = "f8dc1cce87a0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SEQUENCE questions_id_seq")
    op.create_table(
        "questions",
        sa.Column("id", sa.Integer(), nullable=False, server_default=sa.text("nextval('questions_id_seq'::regclass)")),
        sa.Column("quiz_id", sa.Integer(), nullable=False),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("question_type", sa.String(), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["quiz_id"],
            ["quizzes.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("questions")
    op.execute("DROP SEQUENCE IF EXISTS questions_id_seq")
