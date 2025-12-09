"""Base specification pattern for business rules."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class Specification(ABC, Generic[T]):
    """
    Base specification class for business rule validation.
    Implements the Specification pattern from DDD.
    """

    @abstractmethod
    def is_satisfied_by(self, candidate: T) -> bool:
        """Check if the candidate satisfies this specification."""
        ...

    def and_(self, other: "Specification[T]") -> "AndSpecification[T]":
        """Combine with another specification using AND logic."""
        return AndSpecification(self, other)

    def or_(self, other: "Specification[T]") -> "OrSpecification[T]":
        """Combine with another specification using OR logic."""
        return OrSpecification(self, other)

    def not_(self) -> "NotSpecification[T]":
        """Negate this specification."""
        return NotSpecification(self)


class AndSpecification(Specification[T]):
    """Composite specification using AND logic."""

    def __init__(self, left: Specification[T], right: Specification[T]) -> None:
        self._left = left
        self._right = right

    def is_satisfied_by(self, candidate: T) -> bool:
        return self._left.is_satisfied_by(candidate) and self._right.is_satisfied_by(
            candidate
        )


class OrSpecification(Specification[T]):
    """Composite specification using OR logic."""

    def __init__(self, left: Specification[T], right: Specification[T]) -> None:
        self._left = left
        self._right = right

    def is_satisfied_by(self, candidate: T) -> bool:
        return self._left.is_satisfied_by(candidate) or self._right.is_satisfied_by(
            candidate
        )


class NotSpecification(Specification[T]):
    """Negated specification."""

    def __init__(self, spec: Specification[T]) -> None:
        self._spec = spec

    def is_satisfied_by(self, candidate: T) -> bool:
        return not self._spec.is_satisfied_by(candidate)
