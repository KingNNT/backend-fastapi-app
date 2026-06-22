"""Validation and business rule exceptions."""

from dataclasses import dataclass, field
from typing import Any, Optional

from app.shared.domain.base_exception import DomainException
from app.shared.domain.error_codes import ErrorCode


@dataclass
class ValidationError(DomainException):
    """Exception raised when validation fails."""

    message: str = "Validation error"
    error_code: ErrorCode = ErrorCode.VALIDATION_ERROR
    field_name: Optional[str] = None
    field_value: Any = None
    validation_errors: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.field_name:
            self.context["field_name"] = self.field_name
        if self.field_value is not None:
            self.context["field_value"] = str(self.field_value)
        if self.validation_errors:
            self.context["validation_errors"] = self.validation_errors
        super().__post_init__()

    @classmethod
    def from_field(
        cls, field_name: str, message: str, value: Any = None
    ) -> "ValidationError":
        """Create a validation error for a specific field."""
        return cls(
            message=f"Validation error for field '{field_name}': {message}",
            field_name=field_name,
            field_value=value,
        )

    @classmethod
    def from_multiple(cls, errors: list[dict[str, Any]]) -> "ValidationError":
        """Create a validation error from multiple field errors."""
        return cls(
            message="Multiple validation errors",
            validation_errors=errors,
        )


@dataclass
class BusinessRuleViolation(DomainException):
    """Exception raised when a business rule is violated."""

    message: str = "Business rule violation"
    error_code: ErrorCode = ErrorCode.BUSINESS_RULE_VIOLATION
    rule_name: Optional[str] = None

    def __post_init__(self) -> None:
        if self.rule_name:
            self.context["rule_name"] = self.rule_name
        super().__post_init__()

    @classmethod
    def with_rule(cls, rule_name: str, message: str) -> "BusinessRuleViolation":
        """Create a business rule violation with a specific rule name."""
        return cls(
            message=message,
            rule_name=rule_name,
        )
