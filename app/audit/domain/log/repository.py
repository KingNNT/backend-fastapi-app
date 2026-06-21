"""Log repository interface - defines data access contract."""

from datetime import datetime
from typing import Optional, Protocol

from app.audit.domain.log.aggregate import LogAggregate
from app.audit.domain.log.value_objects import Action
from app.shared.domain.ids.log_id import LogId


class ILogWriteRepository(Protocol):
    """
    Repository interface for log write operations (Command side).
    Implementations will be in the infrastructure layer (MongoDB).
    """

    async def save(self, aggregate: LogAggregate) -> None:
        """Save a log aggregate (create only - logs are immutable)."""
        ...


class ILogReadRepository(Protocol):
    """
    Repository interface for log read operations (Query side).
    Implementations will be in the infrastructure layer (MongoDB).
    """

    async def get_by_id(self, log_id: LogId) -> Optional[LogAggregate]:
        """Get a log by ID."""
        ...

    async def list_by_user(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[LogAggregate]:
        """List logs for a specific user."""
        ...

    async def list_by_action(
        self,
        action: Action,
        skip: int = 0,
        limit: int = 100,
    ) -> list[LogAggregate]:
        """List logs by action type."""
        ...

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[LogAggregate]:
        """List all logs with pagination."""
        ...

    async def list_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        skip: int = 0,
        limit: int = 100,
    ) -> list[LogAggregate]:
        """List logs within a date range."""
        ...

    async def count(self) -> int:
        """Count total logs."""
        ...

    async def count_by_user(self, user_id: str) -> int:
        """Count logs for a specific user."""
        ...


class ILogRepository(ILogWriteRepository, ILogReadRepository, Protocol):
    """
    Combined repository interface for log operations.
    Use this when you need both read and write access.
    """

    pass
