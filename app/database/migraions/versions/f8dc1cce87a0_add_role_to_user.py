"""add role to user

Revision ID: f8dc1cce87a0
Revises: 975a9a91fdd9
Create Date: 2025-07-31 19:42:42.561850

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "f8dc1cce87a0"
down_revision = "975a9a91fdd9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE TYPE userrole AS ENUM ('admin', 'student')")
    op.add_column("users", sa.Column("role", sa.Enum("admin", "student", name="userrole"), nullable=False, server_default=sa.text("'student'")))


def downgrade() -> None:
    op.drop_column("users", "role")
    op.execute("DROP TYPE userrole")
