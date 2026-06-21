"""Unit of Work base interface — transaction coordination contract.

This is the SHARED base contract that all BC-specific UoW interfaces extend.
It defines only the transaction lifecycle and event collection behavior,
without any BC-specific repository attributes.
"""

import logging
from typing import Protocol, Self, runtime_checkable

from app.shared.domain.base_event import BaseDomainEvent

logger = logging.getLogger(__name__)


@runtime_checkable
class IUnitOfWork(Protocol):
    """Base Unit of Work interface for coordinating transactions.

    The Unit of Work pattern:
    1. Coordinates multiple repository operations within a single transaction
    2. Collects domain events from aggregates during the transaction
    3. Commits all changes atomically
    4. Publishes domain events AFTER successful commit
    5. Rolls back all changes if any operation fails

    BC-specific UoW interfaces (e.g., IIamUnitOfWork) extend this with
    repository attributes specific to that BC.

    Usage:
        async with uow:
            await uow.users.save(aggregate)
            uow.collect_events(aggregate)
        # Auto-commits on success, auto-rollback on exception
        # Events published after successful commit
    """

    async def __aenter__(self) -> Self:
        """Enter the transaction context.

        Creates a new database session and initializes event collection.
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
        """
        ...

    def add_event(self, event: BaseDomainEvent) -> None:
        """Add a single domain event to be published after commit.

        Use this when you need to add events that aren't from an aggregate.
        """
        ...
