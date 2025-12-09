"""User event handlers - react to user domain events."""

import logging

from app.core.application.commands.handlers.log_handlers import CreateLogHandler
from app.core.application.commands.log.create_log import CreateLogCommand
from app.core.domain.events.user_events import (
    UserActivated,
    UserCreated,
    UserDeactivated,
    UserDeleted,
    UserUpdated,
)

logger = logging.getLogger(__name__)


class UserEventHandler:
    """Handler for user-related domain events."""

    def __init__(self, create_log_handler: CreateLogHandler) -> None:
        self._create_log_handler = create_log_handler

    async def on_user_created(self, event: UserCreated) -> None:
        """Handle UserCreated event - create audit log."""
        logger.info(f"User created: {event.user_id}")
        command = CreateLogCommand(
            action="user_created",
            user_id=event.user_id,
            metadata={
                "email": event.email,
                "username": event.username,
                "event_id": str(event.event_id),
            },
        )
        await self._create_log_handler.handle(command)

    async def on_user_updated(self, event: UserUpdated) -> None:
        """Handle UserUpdated event - create audit log."""
        logger.info(f"User updated: {event.user_id}")
        command = CreateLogCommand(
            action="user_updated",
            user_id=event.user_id,
            metadata={
                "changes": event.changes,
                "event_id": str(event.event_id),
            },
        )
        await self._create_log_handler.handle(command)

    async def on_user_deleted(self, event: UserDeleted) -> None:
        """Handle UserDeleted event - create audit log."""
        logger.info(f"User deleted: {event.user_id}")
        command = CreateLogCommand(
            action="user_deleted",
            user_id=event.user_id,
            metadata={
                "deleted_by": event.deleted_by,
                "event_id": str(event.event_id),
            },
        )
        await self._create_log_handler.handle(command)

    async def on_user_deactivated(self, event: UserDeactivated) -> None:
        """Handle UserDeactivated event - create audit log."""
        logger.info(f"User deactivated: {event.user_id}")
        command = CreateLogCommand(
            action="user_deactivated",
            user_id=event.user_id,
            metadata={
                "reason": event.reason,
                "event_id": str(event.event_id),
            },
        )
        await self._create_log_handler.handle(command)

    async def on_user_activated(self, event: UserActivated) -> None:
        """Handle UserActivated event - create audit log."""
        logger.info(f"User activated: {event.user_id}")
        command = CreateLogCommand(
            action="user_activated",
            user_id=event.user_id,
            metadata={
                "event_id": str(event.event_id),
            },
        )
        await self._create_log_handler.handle(command)
