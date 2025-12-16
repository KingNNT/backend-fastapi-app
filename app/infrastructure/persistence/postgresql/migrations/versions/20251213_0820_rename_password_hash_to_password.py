"""rename_password_hash_to_password

Revision ID: a1b2c3d4e5f6
Revises: e0f058e2d55e
Create Date: 2025-12-13 08:20:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "e0f058e2d55e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("users", "password_hash", new_column_name="password")


def downgrade() -> None:
    op.alter_column("users", "password", new_column_name="password_hash")
