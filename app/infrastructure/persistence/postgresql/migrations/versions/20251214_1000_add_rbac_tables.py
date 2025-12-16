"""add_rbac_tables

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2025-12-14 10:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b2c3d4e5f6g7"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create roles table (with soft delete - inherits BaseModel)
    op.create_table(
        "roles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("updated_by", sa.Uuid(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_by", sa.Uuid(), nullable=True),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_roles_name"), "roles", ["name"], unique=True)

    # Create permissions table (with soft delete - inherits BaseModel)
    op.create_table(
        "permissions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("updated_by", sa.Uuid(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_by", sa.Uuid(), nullable=True),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_permissions_name"), "permissions", ["name"], unique=True)

    # Create user_has_role junction table (no soft delete)
    op.create_table(
        "user_has_role",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("role_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name="fk_user_has_role_user"
        ),
        sa.ForeignKeyConstraint(
            ["role_id"], ["roles.id"], name="fk_user_has_role_role"
        ),
        sa.UniqueConstraint("user_id", "role_id", name="uq_user_has_role"),
    )
    op.create_index(op.f("ix_user_has_role_user_id"), "user_has_role", ["user_id"])
    op.create_index(op.f("ix_user_has_role_role_id"), "user_has_role", ["role_id"])

    # Create user_has_permission junction table (no soft delete)
    op.create_table(
        "user_has_permission",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("permission_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name="fk_user_has_permission_user"
        ),
        sa.ForeignKeyConstraint(
            ["permission_id"],
            ["permissions.id"],
            name="fk_user_has_permission_permission",
        ),
        sa.UniqueConstraint("user_id", "permission_id", name="uq_user_has_permission"),
    )
    op.create_index(
        op.f("ix_user_has_permission_user_id"), "user_has_permission", ["user_id"]
    )
    op.create_index(
        op.f("ix_user_has_permission_permission_id"),
        "user_has_permission",
        ["permission_id"],
    )

    # Create role_has_permissions junction table (no soft delete)
    op.create_table(
        "role_has_permissions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("role_id", sa.Uuid(), nullable=False),
        sa.Column("permission_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["role_id"], ["roles.id"], name="fk_role_has_permissions_role"
        ),
        sa.ForeignKeyConstraint(
            ["permission_id"],
            ["permissions.id"],
            name="fk_role_has_permissions_permission",
        ),
        sa.UniqueConstraint("role_id", "permission_id", name="uq_role_has_permissions"),
    )
    op.create_index(
        op.f("ix_role_has_permissions_role_id"), "role_has_permissions", ["role_id"]
    )
    op.create_index(
        op.f("ix_role_has_permissions_permission_id"),
        "role_has_permissions",
        ["permission_id"],
    )


def downgrade() -> None:
    # Drop junction tables first (they have foreign keys)
    op.drop_index(
        op.f("ix_role_has_permissions_permission_id"), table_name="role_has_permissions"
    )
    op.drop_index(
        op.f("ix_role_has_permissions_role_id"), table_name="role_has_permissions"
    )
    op.drop_table("role_has_permissions")

    op.drop_index(
        op.f("ix_user_has_permission_permission_id"), table_name="user_has_permission"
    )
    op.drop_index(
        op.f("ix_user_has_permission_user_id"), table_name="user_has_permission"
    )
    op.drop_table("user_has_permission")

    op.drop_index(op.f("ix_user_has_role_role_id"), table_name="user_has_role")
    op.drop_index(op.f("ix_user_has_role_user_id"), table_name="user_has_role")
    op.drop_table("user_has_role")

    # Then drop main tables
    op.drop_index(op.f("ix_permissions_name"), table_name="permissions")
    op.drop_table("permissions")

    op.drop_index(op.f("ix_roles_name"), table_name="roles")
    op.drop_table("roles")
