"""Domain events - records of things that happened in the domain."""

from app.core.domain.events.base import BaseDomainEvent
from app.core.domain.events.log_events import LogCreated
from app.core.domain.events.permission_events import (
    PermissionAssignedToUser,
    PermissionCreated,
    PermissionDeleted,
    PermissionRemovedFromUser,
    PermissionUpdated,
)
from app.core.domain.events.role_events import (
    PermissionAssignedToRole,
    PermissionRemovedFromRole,
    RoleAssignedToUser,
    RoleCreated,
    RoleDeleted,
    RoleRemovedFromUser,
    RoleUpdated,
)
from app.core.domain.events.user_events import (
    UserActivated,
    UserCreated,
    UserDeactivated,
    UserDeleted,
    UserEmailUpdated,
    UserPasswordUpdated,
    UserUpdated,
)

__all__ = [
    "BaseDomainEvent",
    # User events
    "UserCreated",
    "UserUpdated",
    "UserDeleted",
    "UserDeactivated",
    "UserActivated",
    "UserEmailUpdated",
    "UserPasswordUpdated",
    # Log events
    "LogCreated",
    # Role events
    "RoleCreated",
    "RoleUpdated",
    "RoleDeleted",
    "PermissionAssignedToRole",
    "PermissionRemovedFromRole",
    "RoleAssignedToUser",
    "RoleRemovedFromUser",
    # Permission events
    "PermissionCreated",
    "PermissionUpdated",
    "PermissionDeleted",
    "PermissionAssignedToUser",
    "PermissionRemovedFromUser",
]
