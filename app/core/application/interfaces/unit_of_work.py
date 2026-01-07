"""Unit of Work interface for transaction management."""

import logging
from typing import Protocol, Self, runtime_checkable

from app.core.domain.events.base import BaseDomainEvent
from app.core.domain.repositories.permission import (
    IPermissionReadRepository,
    IPermissionWriteRepository,
)
from app.core.domain.repositories.role import IRoleReadRepository, IRoleWriteRepository
from app.core.domain.repositories.user import IUserReadRepository, IUserWriteRepository

logger = logging.getLogger(__name__)


@runtime_checkable
class IUnitOfWork(Protocol):
    """Unit of Work interface for coordinating transactions across repositories.

    The Unit of Work pattern:
    1. Coordinates multiple repository operations within a single transaction
    2. Collects domain events from aggregates during the transaction
    3. Commits all changes atomically
    4. Publishes domain events AFTER successful commit
    5. Rolls back all changes if any operation fails

    Usage:
        async with uow:
            await uow.users.save(aggregate)
            uow.collect_events(aggregate)
        # Auto-commits on success, auto-rollback on exception
        # Events published after successful commit
    """

    # Write repositories (for command handlers)
    users: IUserWriteRepository
    roles: IRoleWriteRepository
    permissions: IPermissionWriteRepository

    # Read repositories (for validation during commands)
    users_read: IUserReadRepository
    roles_read: IRoleReadRepository
    permissions_read: IPermissionReadRepository

    async def __aenter__(self) -> Self:
        """Enter the transaction context.

        Creates a new database session and initializes event collection.

        Returns:
            Self for use in async with statements.
        """
        ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> None:
        """Exit the transaction context.

        - If an exception occurred: rolls back the transaction and discards events.
        - If no exception: commits the transaction and publishes events.
        - Always closes the session.

        Args:
            exc_type: Exception type if an error occurred.
            exc_val: Exception value if an error occurred.
            exc_tb: Traceback if an error occurred.
        """
        ...

    async def commit(self) -> None:
        """Commit the current transaction and publish events.

        After calling commit:
        - All changes are persisted to the database
        - All collected domain events are published via the event bus
        """
        ...

    async def rollback(self) -> None:
        """Rollback the current transaction.

        Discards all changes made within the unit of work
        and clears all collected domain events.
        """
        ...

    def collect_events(self, aggregate: object) -> None:
        """Collect domain events from an aggregate.

        Extracts all pending events from the aggregate and adds them
        to the internal event list. Clears the aggregate's event list.
        Events will be published after successful commit.

        Args:
            aggregate: An aggregate with an 'events' attribute and
                      'clear_events()' method.
        """
        ...

    def add_event(self, event: BaseDomainEvent) -> None:
        """Add a single domain event to be published after commit.

        Use this when you need to add events that aren't from an aggregate.

        Args:
            event: The domain event to add.
        """
        ...
