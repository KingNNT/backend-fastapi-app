"""LogId value object - represents a unique log identifier for MongoDB."""

from dataclasses import dataclass


@dataclass(frozen=True)
class LogId:
    """
    Log identifier value object.
    Uses string to be compatible with MongoDB ObjectId.
    Immutable and self-validating.
    """

    value: str

    def __post_init__(self) -> None:
        if not self.value or not isinstance(self.value, str):
            raise ValueError("LogId must be a non-empty string")
        # MongoDB ObjectId is 24 hex characters
        if len(self.value) == 24:
            try:
                int(self.value, 16)
            except ValueError:
                raise ValueError(f"Invalid MongoDB ObjectId format: {self.value}")

    @classmethod
    def from_string(cls, value: str) -> "LogId":
        """Create LogId from string representation."""
        return cls(value=value)

    def __str__(self) -> str:
        return self.value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, LogId):
            return self.value == other.value
        return False

    def __hash__(self) -> int:
        return hash(self.value)
