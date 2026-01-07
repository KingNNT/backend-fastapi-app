"""Repository interfaces - data access contracts."""

from app.core.domain.repositories.log import (
    ILogReadRepository,
    ILogRepository,
    ILogWriteRepository,
)
from app.core.domain.repositories.permission import (
    IPermissionReadRepository,
    IPermissionWriteRepository,
)
from app.core.domain.repositories.role import (
    IRoleReadRepository,
    IRoleWriteRepository,
)
from app.core.domain.repositories.user import (
    IUserReadRepository,
    IUserWriteRepository,
)

__all__ = [
    # User - separated read/write
    "IUserReadRepository",
    "IUserWriteRepository",
    # Role - separated read/write
    "IRoleReadRepository",
    "IRoleWriteRepository",
    # Permission - separated read/write
    "IPermissionReadRepository",
    "IPermissionWriteRepository",
    # Log - keeps combined (write-only for commands, read for queries)
    "ILogRepository",
    "ILogReadRepository",
    "ILogWriteRepository",
]
