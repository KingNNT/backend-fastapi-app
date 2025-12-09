"""Repository interfaces - data access contracts."""

from app.core.domain.repositories.log import (
    ILogReadRepository,
    ILogRepository,
    ILogWriteRepository,
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
]
