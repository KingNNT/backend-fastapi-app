"""Get user query."""

from dataclasses import dataclass


@dataclass(frozen=True)
class GetUserByIdQuery:
    """Query to get a user by ID."""

    user_id: str


@dataclass(frozen=True)
class GetUserByEmailQuery:
    """Query to get a user by email."""

    email: str


@dataclass(frozen=True)
class GetUserByUsernameQuery:
    """Query to get a user by username."""

    username: str
