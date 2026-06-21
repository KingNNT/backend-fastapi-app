"""RoleId value object - represents a unique role identifier."""

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True)
class RoleId:
    """
    Role identifier value object.
    Immutable and self-validating.
    """

    value: UUID

    def __post_init__(self) -> None:
        if not isinstance(self.value, UUID):
            raise ValueError(f"RoleId must be a UUID, got {type(self.value)}")

    @classmethod
    def generate(cls) -> "RoleId":
        """Generate a new random RoleId."""
        return cls(value=uuid4())

    @classmethod
    def from_string(cls, value: str) -> "RoleId":
        """Create RoleId from string representation."""
        return cls(value=UUID(value))

    def __str__(self) -> str:
        return str(self.value)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, RoleId):
            return self.value == other.value
        return False

    def __hash__(self) -> int:
        return hash(self.value)
