"""Specifications - reusable business rule validators."""

from app.core.domain.specifications.base import (
    AndSpecification,
    NotSpecification,
    OrSpecification,
    Specification,
)
from app.core.domain.specifications.user_specs import (
    ActiveUserSpecification,
    CanUpdateUserSpecification,
    HasFullNameSpecification,
    NotDeletedUserSpecification,
    UniqueEmailSpecification,
    UniqueUsernameSpecification,
)

__all__ = [
    "Specification",
    "AndSpecification",
    "OrSpecification",
    "NotSpecification",
    "ActiveUserSpecification",
    "NotDeletedUserSpecification",
    "HasFullNameSpecification",
    "UniqueEmailSpecification",
    "UniqueUsernameSpecification",
    "CanUpdateUserSpecification",
]
