"""Repository interfaces - data access contracts.

IAM repository interfaces moved to app.iam.domain.<aggregate>.repository.
Only Log repository interface remains here.
"""

from app.core.domain.repositories.log import (
    ILogReadRepository,
    ILogRepository,
    ILogWriteRepository,
)

__all__ = [
    "ILogRepository",
    "ILogReadRepository",
    "ILogWriteRepository",
]
