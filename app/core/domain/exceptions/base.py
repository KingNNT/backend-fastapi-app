"""Base domain exception classes."""

from dataclasses import dataclass, field
from typing import Any, Optional

from app.core.domain.exceptions.error_codes import ErrorCode


@dataclass
class DomainException(Exception):
    """
    Base exception for all domain-level errors.
    Should be caught and converted to HTTP responses in the presentation layer.
    """

    message: str
    error_code: ErrorCode = ErrorCode.DOMAIN_ERROR
    context: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"[{self.error_code.value}] {self.message}"


@dataclass
class EntityNotFound(DomainException):
    """Base exception for entity not found errors."""

    entity_type: str = "Entity"
    entity_id: Optional[str] = None
    error_code: ErrorCode = ErrorCode.ENTITY_NOT_FOUND

    def __post_init__(self) -> None:
        if not self.message:
            self.message = f"{self.entity_type} with id '{self.entity_id}' not found"
        super().__post_init__()


@dataclass
class EntityAlreadyExists(DomainException):
    """Base exception for entity already exists errors."""

    entity_type: str = "Entity"
    field_name: str = "id"
    field_value: Optional[str] = None
    error_code: ErrorCode = ErrorCode.ENTITY_ALREADY_EXISTS

    def __post_init__(self) -> None:
        if not self.message:
            self.message = (
                f"{self.entity_type} with {self.field_name} "
                f"'{self.field_value}' already exists"
            )
        super().__post_init__()
