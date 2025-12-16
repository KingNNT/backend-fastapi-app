"""Role entity - represents a role in the domain."""

from dataclasses import dataclass, field
from typing import Optional

from app.core.domain.entities.base import BaseEntity
from app.core.domain.value_objects.role_id import RoleId
from app.core.domain.value_objects.role_name import RoleName


@dataclass
class Role(BaseEntity):
    """
    Role entity with identity.
    Stored in PostgreSQL.
    """

    id: RoleId = field(default_factory=RoleId.generate)
    name: RoleName = field(default_factory=lambda: RoleName("default_role"))
    description: Optional[str] = None

    def __post_init__(self) -> None:
        # Ensure value objects are properly typed
        if isinstance(self.name, str):
            object.__setattr__(self, "name", RoleName(self.name))
        if isinstance(self.id, str):
            object.__setattr__(self, "id", RoleId.from_string(self.id))

    def update_name(self, new_name: RoleName) -> None:
        """Update role's name."""
        self.name = new_name
        self.mark_updated()

    def update_description(self, new_description: Optional[str]) -> None:
        """Update role's description."""
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
