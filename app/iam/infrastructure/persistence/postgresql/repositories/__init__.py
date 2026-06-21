"""IAM PostgreSQL repository implementations."""

from app.iam.infrastructure.persistence.postgresql.repositories.assignment import (
    AssignmentRepository,
)
from app.iam.infrastructure.persistence.postgresql.repositories.permission_read import (
    PostgresPermissionReadModelRepository,
    PostgresPermissionReadRepository,
)
from app.iam.infrastructure.persistence.postgresql.repositories.permission_write import (  # noqa: E501
    PostgresPermissionWriteRepository,
)
from app.iam.infrastructure.persistence.postgresql.repositories.role_read import (
    PostgresRoleReadModelRepository,
    PostgresRoleReadRepository,
)
from app.iam.infrastructure.persistence.postgresql.repositories.role_write import (
    PostgresRoleWriteRepository,
)
from app.iam.infrastructure.persistence.postgresql.repositories.user_read import (
    PostgresUserReadModelRepository,
    PostgresUserReadRepository,
)
from app.iam.infrastructure.persistence.postgresql.repositories.user_write import (
    PostgresUserWriteRepository,
)

__all__ = [
    "AssignmentRepository",
    "PostgresUserReadRepository",
    "PostgresUserReadModelRepository",
    "PostgresUserWriteRepository",
    "PostgresRoleReadRepository",
    "PostgresRoleReadModelRepository",
    "PostgresRoleWriteRepository",
    "PostgresPermissionReadRepository",
    "PostgresPermissionReadModelRepository",
    "PostgresPermissionWriteRepository",
]
