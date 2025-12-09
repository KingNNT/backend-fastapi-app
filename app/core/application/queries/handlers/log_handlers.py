"""Log query handlers - execute log read operations."""

from datetime import datetime
from typing import Optional, Protocol

from app.core.application.queries.log.get_log import GetLogByIdQuery
from app.core.application.queries.log.list_logs import (
    ListLogsByActionQuery,
    ListLogsByDateRangeQuery,
    ListLogsByUserQuery,
    ListLogsQuery,
)
from app.core.application.read_models.log_read_model import LogReadModel


class ILogReadModelRepository(Protocol):
    """Interface for log read model repository."""

    async def get_by_id(self, log_id: str) -> Optional[LogReadModel]:
        """Get log read model by ID."""
        ...

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[LogReadModel]:
        """List log read models with pagination."""
        ...

    async def list_by_user(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[LogReadModel]:
        """List logs for a specific user."""
        ...

    async def list_by_action(
        self,
        action: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[LogReadModel]:
        """List logs by action type."""
        ...

    async def list_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        skip: int = 0,
        limit: int = 100,
    ) -> list[LogReadModel]:
        """List logs within a date range."""
        ...


class GetLogByIdHandler:
    """Handler for GetLogByIdQuery."""

    def __init__(self, repository: ILogReadModelRepository) -> None:
        self._repository = repository

    async def handle(self, query: GetLogByIdQuery) -> Optional[LogReadModel]:
        """Execute the get log by ID query."""
        return await self._repository.get_by_id(query.log_id)


class ListLogsHandler:
    """Handler for ListLogsQuery."""

    def __init__(self, repository: ILogReadModelRepository) -> None:
        self._repository = repository

    async def handle(self, query: ListLogsQuery) -> list[LogReadModel]:
        """Execute the list logs query."""
        return await self._repository.list_all(
            skip=query.skip,
            limit=query.limit,
        )


class ListLogsByUserHandler:
    """Handler for ListLogsByUserQuery."""

    def __init__(self, repository: ILogReadModelRepository) -> None:
        self._repository = repository

    async def handle(self, query: ListLogsByUserQuery) -> list[LogReadModel]:
        """Execute the list logs by user query."""
        return await self._repository.list_by_user(
            user_id=query.user_id,
            skip=query.skip,
            limit=query.limit,
        )


class ListLogsByActionHandler:
    """Handler for ListLogsByActionQuery."""

    def __init__(self, repository: ILogReadModelRepository) -> None:
        self._repository = repository

    async def handle(self, query: ListLogsByActionQuery) -> list[LogReadModel]:
        """Execute the list logs by action query."""
        return await self._repository.list_by_action(
            action=query.action,
            skip=query.skip,
            limit=query.limit,
        )


class ListLogsByDateRangeHandler:
    """Handler for ListLogsByDateRangeQuery."""

    def __init__(self, repository: ILogReadModelRepository) -> None:
        self._repository = repository

    async def handle(self, query: ListLogsByDateRangeQuery) -> list[LogReadModel]:
        """Execute the list logs by date range query."""
        return await self._repository.list_by_date_range(
            start_date=query.start_date,
            end_date=query.end_date,
            skip=query.skip,
            limit=query.limit,
        )
