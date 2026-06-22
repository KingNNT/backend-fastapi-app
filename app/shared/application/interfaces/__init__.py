"""Shared application interfaces — buses, UoW base, and contracts."""

from app.shared.application.interfaces.command_bus import (
    ICommand,
    ICommandBus,
    ICommandHandler,
)
from app.shared.application.interfaces.event_bus import IEventBus
from app.shared.application.interfaces.query_bus import (
    IQuery,
    IQueryBus,
    IQueryHandler,
)
from app.shared.application.interfaces.unit_of_work import IUnitOfWork

__all__ = [
    "IEventBus",
    "ICommand",
    "ICommandHandler",
    "ICommandBus",
    "IQuery",
    "IQueryHandler",
    "IQueryBus",
    "IUnitOfWork",
]
