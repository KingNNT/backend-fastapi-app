"""Log mapper for MongoDB - converts between domain and persistence models."""

from app.core.application.read_models.log_read_model import LogReadModel
from app.core.domain.aggregates.log import LogAggregate
from app.core.domain.entities.log import Log
from app.core.domain.value_objects.action import Action
from app.core.domain.value_objects.log_id import LogId
from app.infrastructure.persistence.mongodb.models.log import LogModel


class LogMapper:
    """Mapper between Log domain entity and LogModel persistence model."""

    @staticmethod
    def to_model(aggregate: LogAggregate) -> LogModel:
        """Convert domain aggregate to persistence model."""
        log = aggregate.log
        return LogModel(
            action=log.action_str,
            user_id=log.user_id,
            timestamp=log.timestamp,
            metadata=log.metadata,
        )

    @staticmethod
    def to_entity(model: LogModel) -> Log:
        """Convert persistence model to domain entity."""
        log_id = LogId.from_string(str(model.id)) if model.id else None
        return Log(
            id=log_id,
            action=Action.custom(model.action),
            user_id=model.user_id,
            timestamp=model.timestamp,
            metadata=model.metadata,
        )

    @staticmethod
    def to_aggregate(model: LogModel) -> LogAggregate:
        """Convert persistence model to domain aggregate."""
        entity = LogMapper.to_entity(model)
        return LogAggregate.reconstitute(entity)

    @staticmethod
    def to_read_model(model: LogModel) -> LogReadModel:
        """Convert persistence model to read model."""
        return LogReadModel(
            id=str(model.id) if model.id else "",
            action=model.action,
            user_id=model.user_id,
            timestamp=model.timestamp,
            metadata=model.metadata,
        )
