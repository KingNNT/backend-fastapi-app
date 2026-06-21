"""Log read repository implementation for MongoDB."""

from datetime import datetime
from typing import Optional

from beanie import PydanticObjectId

from app.core.application.read_models.log_read_model import LogReadModel
from app.core.domain.aggregates.log import LogAggregate
from app.core.domain.value_objects.action import Action
from app.infrastructure.persistence.mongodb.mappers.log import LogMapper
from app.infrastructure.persistence.mongodb.models.log import LogModel
from app.shared.domain.ids.log_id import LogId


class MongoLogReadRepository:
    """MongoDB implementation of log read repository."""

    def __init__(self) -> None:
        self._mapper = LogMapper()

    async def get_by_id(self, log_id: LogId) -> Optional[LogAggregate]:
        """Get a log by ID."""
        try:
            object_id = PydanticObjectId(str(log_id))
        except Exception:
            return None

        model = await LogModel.get(object_id)
        if model is None:
            return None
        return self._mapper.to_aggregate(model)

    async def list_by_user(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[LogAggregate]:
        """List logs for a specific user."""
        models = (
            await LogModel.find(LogModel.user_id == user_id)
            .sort(-LogModel.timestamp)
            .skip(skip)
            .limit(limit)
            .to_list()
        )
        return [self._mapper.to_aggregate(model) for model in models]

    async def list_by_action(
        self,
        action: Action,
        skip: int = 0,
        limit: int = 100,
    ) -> list[LogAggregate]:
        """List logs by action type."""
        models = (
            await LogModel.find(LogModel.action == str(action))
            .sort(-LogModel.timestamp)
            .skip(skip)
            .limit(limit)
            .to_list()
        )
        return [self._mapper.to_aggregate(model) for model in models]

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[LogAggregate]:
        """List all logs with pagination."""
        models = (
            await LogModel.find_all()
            .sort(-LogModel.timestamp)
            .skip(skip)
            .limit(limit)
            .to_list()
        )
        return [self._mapper.to_aggregate(model) for model in models]

    async def list_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        skip: int = 0,
        limit: int = 100,
    ) -> list[LogAggregate]:
        """List logs within a date range."""
        models = (
            await LogModel.find(
                LogModel.timestamp >= start_date,
                LogModel.timestamp <= end_date,
            )
            .sort(-LogModel.timestamp)
            .skip(skip)
            .limit(limit)
            .to_list()
        )
        return [self._mapper.to_aggregate(model) for model in models]

    async def count(self) -> int:
        """Count total logs."""
        return await LogModel.count()

    async def count_by_user(self, user_id: str) -> int:
        """Count logs for a specific user."""
        return await LogModel.find(LogModel.user_id == user_id).count()


class MongoLogReadModelRepository:
    """MongoDB implementation of log read model repository."""

    def __init__(self) -> None:
        self._mapper = LogMapper()

    async def get_by_id(self, log_id: str) -> Optional[LogReadModel]:
        """Get log read model by ID."""
        try:
            object_id = PydanticObjectId(log_id)
        except Exception:
            return None

        model = await LogModel.get(object_id)
        if model is None:
            return None
        return self._mapper.to_read_model(model)

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[LogReadModel]:
        """List log read models with pagination."""
        models = (
            await LogModel.find_all()
            .sort(-LogModel.timestamp)
            .skip(skip)
            .limit(limit)
            .to_list()
        )
        return [self._mapper.to_read_model(model) for model in models]

    async def list_by_user(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[LogReadModel]:
        """List logs for a specific user."""
        models = (
            await LogModel.find(LogModel.user_id == user_id)
            .sort(-LogModel.timestamp)
            .skip(skip)
            .limit(limit)
            .to_list()
        )
        return [self._mapper.to_read_model(model) for model in models]

    async def list_by_action(
        self,
        action: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[LogReadModel]:
        """List logs by action type."""
        models = (
            await LogModel.find(LogModel.action == action)
            .sort(-LogModel.timestamp)
            .skip(skip)
            .limit(limit)
            .to_list()
        )
        return [self._mapper.to_read_model(model) for model in models]

    async def list_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        skip: int = 0,
        limit: int = 100,
    ) -> list[LogReadModel]:
        """List logs within a date range."""
        models = (
            await LogModel.find(
                LogModel.timestamp >= start_date,
                LogModel.timestamp <= end_date,
            )
            .sort(-LogModel.timestamp)
            .skip(skip)
            .limit(limit)
            .to_list()
        )
        return [self._mapper.to_read_model(model) for model in models]
