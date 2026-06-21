"""Permission entity - represents a permission in the domain."""

from dataclasses import dataclass, field
from typing import Optional

from app.core.domain.value_objects.permission_name import PermissionName
from app.shared.domain.base_entity import BaseEntity
from app.shared.domain.ids.permission_id import PermissionId


@dataclass
class Permission(BaseEntity):
    """
    Permission entity with identity.
    Stored in PostgreSQL.
    """

    id: PermissionId = field(default_factory=PermissionId.generate)
    name: PermissionName = field(
        default_factory=lambda: PermissionName("default:permission")
    )
    description: Optional[str] = None

    def __post_init__(self) -> None:
        # Ensure value objects are properly typed
        if isinstance(self.name, str):
            object.__setattr__(self, "name", PermissionName(self.name))
        if isinstance(self.id, str):
            object.__setattr__(self, "id", PermissionId.from_string(self.id))

    def update_name(self, new_name: PermissionName) -> None:
        """Update permission's name."""
        self.name = new_name
        self.mark_updated()

    def update_description(self, new_description: Optional[str]) -> None:
        """Update permission's description."""
        self.description = new_description
        self.mark_updated()

    @property
    def name_str(self) -> str:
        """Get name as string."""
        return str(self.name)

    @property
    def id_str(self) -> str:
        """Get id as string."""
        return str(self.id)
