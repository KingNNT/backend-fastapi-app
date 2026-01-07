"""PostgreSQL repositories."""

from app.infrastructure.persistence.postgresql.repositories.assignment_repository import (  # noqa: E501
    AssignmentRepository,
)
from app.infrastructure.persistence.postgresql.repositories.permission_read import (
    PostgresPermissionReadModelRepository,
    PostgresPermissionReadRepository,
)
from app.infrastructure.persistence.postgresql.repositories.permission_write import (
    PostgresPermissionWriteRepository,
)
from app.infrastructure.persistence.postgresql.repositories.role_read import (
    PostgresRoleReadModelRepository,
    PostgresRoleReadRepository,
)
from app.infrastructure.persistence.postgresql.repositories.role_write import (
    PostgresRoleWriteRepository,
)
from app.infrastructure.persistence.postgresql.repositories.user_read import (
    PostgresUserReadModelRepository,
    PostgresUserReadRepository,
)
from app.infrastructure.persistence.postgresql.repositories.user_write import (
    PostgresUserWriteRepository,
)

__all__ = [
    # Assignment
    "AssignmentRepository",
    # User - separated read/write
    "PostgresUserReadModelRepository",
    "PostgresUserReadRepository",
    "PostgresUserWriteRepository",
    # Role - separated read/write
    "PostgresRoleReadModelRepository",
    "PostgresRoleReadRepository",
    "PostgresRoleWriteRepository",
    # Permission - separated read/write
    "PostgresPermissionReadModelRepository",
    "PostgresPermissionReadRepository",
    "PostgresPermissionWriteRepository",
]
