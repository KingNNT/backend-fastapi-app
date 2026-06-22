"""Shared domain primitives — base classes, exceptions, IDs."""

from app.shared.domain.base_entity import BaseEntity, utc_now
from app.shared.domain.base_event import BaseDomainEvent
from app.shared.domain.base_exception import (
    DomainException,
    EntityAlreadyExists,
    EntityNotFound,
)
from app.shared.domain.error_codes import ErrorCode
from app.shared.domain.validation import BusinessRuleViolation, ValidationError

__all__ = [
    "BaseEntity",
    "utc_now",
    "BaseDomainEvent",
    "DomainException",
    "EntityNotFound",
    "EntityAlreadyExists",
    "ErrorCode",
    "ValidationError",
    "BusinessRuleViolation",
]
