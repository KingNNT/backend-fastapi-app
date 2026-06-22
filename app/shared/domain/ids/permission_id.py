"""PermissionId value object - represents a unique permission identifier."""

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True)
class PermissionId:
    """
    Permission identifier value object.
    Immutable and self-validating.
    """

    value: UUID

    def __post_init__(self) -> None:
        if not isinstance(self.value, UUID):
            raise ValueError(f"PermissionId must be a UUID, got {type(self.value)}")

    @classmethod
    def generate(cls) -> "PermissionId":
        """Generate a new random PermissionId."""
        return cls(value=uuid4())

    @classmethod
    def from_string(cls, value: str) -> "PermissionId":
        """Create PermissionId from string representation."""
        return cls(value=UUID(value))

    def __str__(self) -> str:
        return str(self.value)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, PermissionId):
            return self.value == other.value
        return False

    def __hash__(self) -> int:
        return hash(self.value)
