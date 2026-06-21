"""Command bus interface - defines command dispatching contract."""

from typing import Any, Protocol, TypeVar

T = TypeVar("T")


class ICommand(Protocol):
    """Marker interface for commands."""

    pass


class ICommandHandler(Protocol[T]):
    """Interface for command handlers."""

    async def handle(self, command: T) -> Any:
        """Handle the command and return result."""
        ...


class ICommandBus(Protocol):
    """
    Interface for command bus implementations.
    Used to dispatch commands to their handlers.
    """

    async def dispatch(self, command: ICommand) -> Any:
        """Dispatch a command to its handler."""
        ...

    def register(
        self,
        command_type: type[ICommand],
        handler: ICommandHandler,
    ) -> None:
        """Register a handler for a command type."""
        ...
