"""PostgreSQL repositories."""

from app.infrastructure.persistence.postgresql.repositories.assignment_repository import (  # noqa: E501
    AssignmentRepository,
)
from app.infrastructure.persistence.postgresql.repositories.combined import (
    CombinedPermissionRepository,
    CombinedRoleRepository,
    CombinedUserRepository,
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
    "AssignmentRepository",
    "CombinedPermissionRepository",
    "CombinedRoleRepository",
    "CombinedUserRepository",
    "PostgresPermissionReadModelRepository",
    "PostgresPermissionReadRepository",
    "PostgresPermissionWriteRepository",
    "PostgresRoleReadModelRepository",
    "PostgresRoleReadRepository",
    "PostgresRoleWriteRepository",
    "PostgresUserReadModelRepository",
    "PostgresUserReadRepository",
    "PostgresUserWriteRepository",
]
