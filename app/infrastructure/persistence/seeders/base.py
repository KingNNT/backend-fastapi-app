"""Base seeder protocol for database seeding."""

from typing import Protocol, runtime_checkable


@runtime_checkable
class ISeeder(Protocol):
    """Protocol for database seeders following DDD patterns."""

    @property
    def entity_name(self) -> str:
        """Return the entity name (e.g., 'user', 'log')."""
        ...

    @property
    def database_type(self) -> str:
        """Return database type ('postgresql' or 'mongodb')."""
        ...

    async def seed(self, count: int = 10, dry_run: bool = False) -> int:
        """Seed entities.

        Args:
            count: Number of entities to seed.
            dry_run: If True, preview without making changes.

        Returns:
            Number of seeded records.
        """
        ...

    async def clear(self, dry_run: bool = False) -> int:
        """Clear entities.

        Args:
            dry_run: If True, preview without making changes.

        Returns:
            Number of cleared records.
        """
        ...

    async def count(self) -> int:
        """Count existing entities.

        Returns:
            Current number of entities in the database.
        """
        ...
