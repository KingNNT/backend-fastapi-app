"""Shared application interfaces — buses and contracts.

Note: IUnitOfWork stays in app/core/application/interfaces/ for now.
It will be split into base (shared) + IAM-specific in Phase 2.
"""

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

__all__ = [
    "IEventBus",
    "ICommand",
    "ICommandHandler",
    "ICommandBus",
    "IQuery",
    "IQueryHandler",
    "IQueryBus",
]
