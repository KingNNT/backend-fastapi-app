"""Log command handlers - execute log write operations."""

from app.core.application.commands.log.create_log import CreateLogCommand
from app.core.domain.aggregates.log import LogAggregate
from app.core.domain.repositories.log import ILogWriteRepository
from app.core.domain.value_objects.action import Action
from app.shared.application.interfaces.event_bus import IEventBus


class CreateLogHandler:
    """Handler for CreateLogCommand."""

    def __init__(
        self,
        repository: ILogWriteRepository,
        event_bus: IEventBus,
    ) -> None:
        self._repository = repository
        self._event_bus = event_bus

    async def handle(self, command: CreateLogCommand) -> str:
        """Execute the create log command and return log ID."""
        # Create action value object
        action = Action.custom(command.action)

        # Create aggregate
        aggregate = LogAggregate.create(
            action=action,
            user_id=command.user_id,
            metadata=dict(command.metadata),
        )

        # Persist (repository will assign ID)
        await self._repository.save(aggregate)

        # Publish domain events
        for event in aggregate.events:
            await self._event_bus.publish(event)
        aggregate.clear_events()

        return aggregate.id_str or ""
