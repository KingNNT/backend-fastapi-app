"""Role aggregate - consistency boundary for role operations."""

from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID

from app.core.domain.entities.role import Role
from app.core.domain.events.role_events import (
    RoleCreated,
    RoleDeleted,
    RoleUpdated,
)
from app.core.domain.value_objects.role_name import RoleName
from app.shared.domain.base_event import BaseDomainEvent
from app.shared.domain.ids.role_id import RoleId


@dataclass
class RoleAggregate:
    """
    Role aggregate root - ensures consistency for role operations.
    All modifications to role data must go through this aggregate.
    """

    _role: Role
    _events: list[BaseDomainEvent] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        name: RoleName,
        description: Optional[str] = None,
    ) -> "RoleAggregate":
        """Factory method to create a new role aggregate."""
        role = Role(
            id=RoleId.generate(),
            name=name,
            description=description,
        )
        aggregate = cls(_role=role)
        aggregate._events.append(
            RoleCreated(
                role_id=role.id_str,
                name=role.name_str,
                description=description,
            )
        )
        return aggregate

    @classmethod
    def reconstitute(cls, role: Role) -> "RoleAggregate":
        """Reconstitute aggregate from existing role entity (from repository)."""
        return cls(_role=role)

    @property
    def role(self) -> Role:
        """Get the underlying role entity."""
        return self._role

    @property
    def id(self) -> RoleId:
        """Get role ID."""
        return self._role.id

    @property
    def id_str(self) -> str:
        """Get role ID as string."""
        return self._role.id_str

    @property
    def events(self) -> list[BaseDomainEvent]:
        """Get domain events raised by this aggregate."""
        return self._events.copy()

    def clear_events(self) -> None:
        """Clear domain events after they've been dispatched."""
        self._events.clear()

    def update_name(self, new_name: RoleName) -> None:
        """Update role's name."""
        old_name = self._role.name_str
        self._role.update_name(new_name)
        self._events.append(
            RoleUpdated(
                role_id=self._role.id_str,
                changes={"name": {"old": old_name, "new": str(new_name)}},
            )
        )

    def update_description(self, new_description: Optional[str]) -> None:
        """Update role's description."""
        old_description = self._role.description
        self._role.update_description(new_description)
        self._events.append(
            RoleUpdated(
                role_id=self._role.id_str,
                changes={
                    "description": {"old": old_description, "new": new_description}
                },
            )
        )

    def soft_delete(self, deleted_by: Optional[UUID] = None) -> None:
        """Soft delete the role."""
        self._role.soft_delete(deleted_by=deleted_by)
        self._events.append(
            RoleDeleted(
                role_id=self._role.id_str,
                deleted_by=str(deleted_by) if deleted_by else None,
            )
        )
