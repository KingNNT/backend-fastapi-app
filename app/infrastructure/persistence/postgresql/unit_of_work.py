"""PostgreSQL Unit of Work implementation."""

import logging
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.iam.domain.assignment.repository import IAssignmentRepository
from app.iam.domain.permission.repository import (
    IPermissionReadRepository,
    IPermissionWriteRepository,
)
from app.iam.domain.role.repository import IRoleReadRepository, IRoleWriteRepository
from app.iam.domain.user.repository import IUserReadRepository, IUserWriteRepository
from app.infrastructure.persistence.postgresql.repositories.assignment_repository import (  # noqa: E501
    AssignmentRepository,
)
from app.infrastructure.persistence.postgresql.repositories.permission_read import (
    PostgresPermissionReadRepository,
)
from app.infrastructure.persistence.postgresql.repositories.permission_write import (
    PostgresPermissionWriteRepository,
)
from app.infrastructure.persistence.postgresql.repositories.role_read import (
    PostgresRoleReadRepository,
)
from app.infrastructure.persistence.postgresql.repositories.role_write import (
    PostgresRoleWriteRepository,
)
from app.infrastructure.persistence.postgresql.repositories.user_read import (
    PostgresUserReadRepository,
)
from app.infrastructure.persistence.postgresql.repositories.user_write import (
    PostgresUserWriteRepository,
)
from app.shared.application.interfaces.event_bus import IEventBus
from app.shared.domain.base_event import BaseDomainEvent

logger = logging.getLogger(__name__)


class PostgresUnitOfWork:
    """PostgreSQL implementation of Unit of Work pattern.

    Coordinates transactions across multiple repositories with:
    - Repository initialization on context entry
    - Automatic commit on successful context exit
    - Automatic rollback on exception
    - Domain event collection and publishing after commit

    Usage:
        async with uow:
            await uow.users.save(aggregate)
            uow.collect_events(aggregate)
        # Auto-commits and publishes events on success
    """

    # Repository attributes (initialized in __aenter__)
    users: IUserWriteRepository
    users_read: IUserReadRepository
    roles: IRoleWriteRepository
    roles_read: IRoleReadRepository
    permissions: IPermissionWriteRepository
    permissions_read: IPermissionReadRepository
    assignments: IAssignmentRepository

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        event_bus: IEventBus,
    ) -> None:
        """Initialize the Unit of Work.

        Args:
            session_factory: Factory for creating async database sessions.
            event_bus: Event bus for publishing domain events.
        """
        self._session_factory = session_factory
        self._event_bus = event_bus
        self._session: AsyncSession | None = None
        self._events: list[BaseDomainEvent] = []

    def _ensure_session(self) -> AsyncSession:
        """Ensure session exists and return it.

        Raises:
            RuntimeError: If called outside of context manager.
        """
        if self._session is None:
            raise RuntimeError(
                "Unit of Work session is not active. "
                "Use 'async with uow:' to start a transaction."
            )
        return self._session

    def _init_repositories(self) -> None:
        """Initialize all repository instances with current session."""
        session = self._ensure_session()
        self.users = PostgresUserWriteRepository(session)
        self.users_read = PostgresUserReadRepository(session)
        self.roles = PostgresRoleWriteRepository(session)
        self.roles_read = PostgresRoleReadRepository(session)
        self.permissions = PostgresPermissionWriteRepository(session)
        self.permissions_read = PostgresPermissionReadRepository(session)
        self.assignments = AssignmentRepository(session)

    async def __aenter__(self) -> Self:
        """Enter the transaction context.

        Creates a new database session, initializes repositories,
        and prepares event collection.

        Returns:
            Self for use in async with statements.
        """
        self._session = self._session_factory()
        self._events = []
        self._init_repositories()
        logger.debug("Unit of Work started")
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> None:
        """Exit the transaction context.

        - If an exception occurred: rolls back and discards events.
        - If no exception: commits and publishes events.
        - Always closes the session.

        Args:
            exc_type: Exception type if an error occurred.
            exc_val: Exception value if an error occurred.
            exc_tb: Traceback if an error occurred.
        """
        try:
            if exc_type is not None:
                # Exception occurred, rollback
                await self.rollback()
            else:
                # Success, commit and publish events
                await self.commit()
        finally:
            # Always close session
            if self._session is not None:
                await self._session.close()
                self._session = None
            logger.debug("Unit of Work finished")

    async def commit(self) -> None:
        """Commit the current transaction and publish events.

        Persists all changes to the database, then publishes
        all collected domain events via the event bus.
        """
        session = self._ensure_session()
        await session.commit()
        logger.debug("Unit of Work committed")

        # Publish events AFTER successful commit
        await self._publish_events()

    async def rollback(self) -> None:
        """Rollback the current transaction.

        Discards all uncommitted changes and clears collected events.
        """
        session = self._ensure_session()
        await session.rollback()
        self._events.clear()
        logger.debug("Unit of Work rolled back")

    def collect_events(self, aggregate: object) -> None:
        """Collect domain events from an aggregate.

        Extracts all pending events from the aggregate, adds them
        to the internal event list, and clears the aggregate's events.

        Args:
            aggregate: An aggregate with 'events' attribute and
                      'clear_events()' method.
        """
        if hasattr(aggregate, "events"):
            self._events.extend(aggregate.events)
            if hasattr(aggregate, "clear_events"):
                aggregate.clear_events()

    def add_event(self, event: BaseDomainEvent) -> None:
        """Add a single domain event to be published after commit.

        Args:
            event: The domain event to add.
        """
        self._events.append(event)

    async def _publish_events(self) -> None:
        """Publish all collected domain events.

        Events are published in order. If publishing fails for an event,
        it's logged but doesn't affect other events (best-effort delivery).
        """
        events_to_publish = self._events.copy()
        self._events.clear()

        for event in events_to_publish:
            try:
                await self._event_bus.publish(event)
            except Exception as e:
                # Log but don't fail - events are best-effort after commit
                logger.error(
                    f"Failed to publish event {type(event).__name__}: {e}",
                    exc_info=True,
                )
