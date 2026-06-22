"""Log write repository implementation for MongoDB."""

from app.audit.domain.log.aggregate import LogAggregate
from app.audit.infrastructure.persistence.mongodb.mappers.log import LogMapper
from app.shared.domain.ids.log_id import LogId


class MongoLogWriteRepository:
    """MongoDB implementation of log write repository."""

    def __init__(self) -> None:
        self._mapper = LogMapper()

    async def save(self, aggregate: LogAggregate) -> None:
        """Save a log aggregate (create only - logs are immutable)."""
        model = self._mapper.to_model(aggregate)
        await model.insert()

        # Set the ID on the aggregate after persistence
        if model.id:
            aggregate.set_id(LogId.from_string(str(model.id)))
