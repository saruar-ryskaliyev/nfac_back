"""create answers table

Revision ID: ghi789jkl012
Revises: def456ghi789
Create Date: 2025-08-01 12:01:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "ghi789jkl012"
down_revision = "def456ghi789"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SEQUENCE answers_id_seq")
    op.create_table(
        "answers",
        sa.Column("id", sa.Integer(), nullable=False, server_default=sa.text("nextval('answers_id_seq'::regclass)")),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("question_id", sa.Integer(), nullable=False),
        sa.Column("selected_option_ids", sa.ARRAY(sa.Integer()), nullable=True),
        sa.Column("text_answer", sa.Text(), nullable=True),
        sa.Column("is_correct", sa.Boolean(), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["question_id"],
            ["questions.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("answers")
    op.execute("DROP SEQUENCE IF EXISTS answers_id_seq")
