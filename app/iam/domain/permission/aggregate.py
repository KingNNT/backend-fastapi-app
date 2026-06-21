"""Permission aggregate - consistency boundary for permission operations."""

from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID

from app.iam.domain.permission.entity import Permission
from app.iam.domain.permission.events import (
    PermissionCreated,
    PermissionDeleted,
    PermissionUpdated,
)
from app.iam.domain.permission.value_objects import PermissionName
from app.shared.domain.base_event import BaseDomainEvent
from app.shared.domain.ids.permission_id import PermissionId


@dataclass
class PermissionAggregate:
    """
    Permission aggregate root - ensures consistency for permission operations.
    All modifications to permission data must go through this aggregate.
    """

    _permission: Permission
    _events: list[BaseDomainEvent] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        name: PermissionName,
        description: Optional[str] = None,
    ) -> "PermissionAggregate":
        """Factory method to create a new permission aggregate."""
        permission = Permission(
            id=PermissionId.generate(),
            name=name,
            description=description,
        )
        aggregate = cls(_permission=permission)
        aggregate._events.append(
            PermissionCreated(
                permission_id=permission.id_str,
                name=permission.name_str,
                description=description,
            )
        )
        return aggregate

    @classmethod
    def reconstitute(cls, permission: Permission) -> "PermissionAggregate":
        """Reconstitute aggregate from existing permission entity (from repository)."""
        return cls(_permission=permission)

    @property
    def permission(self) -> Permission:
        """Get the underlying permission entity."""
        return self._permission

    @property
    def id(self) -> PermissionId:
        """Get permission ID."""
        return self._permission.id

    @property
    def id_str(self) -> str:
        """Get permission ID as string."""
        return self._permission.id_str

    @property
    def events(self) -> list[BaseDomainEvent]:
        """Get domain events raised by this aggregate."""
        return self._events.copy()

    def clear_events(self) -> None:
        """Clear domain events after they've been dispatched."""
        self._events.clear()

    def update_name(self, new_name: PermissionName) -> None:
        """Update permission's name."""
        old_name = self._permission.name_str
        self._permission.update_name(new_name)
        self._events.append(
            PermissionUpdated(
                permission_id=self._permission.id_str,
                changes={"name": {"old": old_name, "new": str(new_name)}},
            )
        )

    def update_description(self, new_description: Optional[str]) -> None:
        """Update permission's description."""
        old_description = self._permission.description
        self._permission.update_description(new_description)
        self._events.append(
            PermissionUpdated(
                permission_id=self._permission.id_str,
                changes={
                    "description": {"old": old_description, "new": new_description}
                },
            )
        )

    def soft_delete(self, deleted_by: Optional[UUID] = None) -> None:
        """Soft delete the permission."""
        self._permission.soft_delete(deleted_by=deleted_by)
        self._events.append(
            PermissionDeleted(
                permission_id=self._permission.id_str,
                deleted_by=str(deleted_by) if deleted_by else None,
            )
        )
