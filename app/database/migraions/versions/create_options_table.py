"""create options table

Revision ID: def456ghi789
Revises: abc123def456
Create Date: 2025-08-01 12:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "def456ghi789"
down_revision = "abc123def456"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SEQUENCE options_id_seq")
    op.create_table(
        "options",
        sa.Column("id", sa.Integer(), nullable=False, server_default=sa.text("nextval('options_id_seq'::regclass)")),
        sa.Column("question_id", sa.Integer(), nullable=False),
        sa.Column("option_text", sa.Text(), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["question_id"],
            ["questions.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("options")
    op.execute("DROP SEQUENCE IF EXISTS options_id_seq")
