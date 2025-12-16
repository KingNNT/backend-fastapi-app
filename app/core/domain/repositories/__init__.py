"""Repository interfaces - data access contracts."""

from app.core.domain.repositories.log import (
    ILogReadRepository,
    ILogRepository,
    ILogWriteRepository,
)
from app.core.domain.repositories.permission import (
    IPermissionReadRepository,
    IPermissionRepository,
    IPermissionWriteRepository,
)
from app.core.domain.repositories.role import (
    IRoleReadRepository,
    IRoleRepository,
    IRoleWriteRepository,
)
from app.core.domain.repositories.user import (
    IUserReadRepository,
    IUserRepository,
    IUserWriteRepository,
)

__all__ = [
    "IUserRepository",
    "IUserReadRepository",
    "IUserWriteRepository",
    "ILogRepository",
    "ILogReadRepository",
    "ILogWriteRepository",
    "IRoleRepository",
    "IRoleReadRepository",
    "IRoleWriteRepository",
    "IPermissionRepository",
    "IPermissionReadRepository",
    "IPermissionWriteRepository",
]
