"""Database seeding commands."""

import logging
import logging.config
from enum import Enum
from typing import Any

import typer

from app.infrastructure.cli.utils.async_runner import run_async
from app.infrastructure.cli.utils.console import Console
from app.infrastructure.configs.logging import get_log_config
from app.infrastructure.persistence.seeders import LogSeeder, UserSeeder

# Configure logging for CLI
logging.config.dictConfig(get_log_config())

# Seeder registry - use concrete classes directly to avoid Protocol constructor issues
SEEDERS: dict[str, Any] = {
    "user": UserSeeder,
    "log": LogSeeder,
}

app = typer.Typer(help="Database seeding commands")


class EntityType(str, Enum):
    """Entity types for seeding."""

    user = "user"
    log = "log"
    all = "all"


def get_seeders(entity: EntityType, use_test_db: bool) -> list:
    """Get seeder instances based on entity type.

    Args:
        entity: Entity type to seed.
        use_test_db: If True, use test database.

    Returns:
        List of seeder instances.
    """
    if entity == EntityType.all:
        return [seeder_cls(use_test_db=use_test_db) for seeder_cls in SEEDERS.values()]
    return [SEEDERS[entity.value](use_test_db=use_test_db)]


@app.command()
def seed(
    entity: EntityType = typer.Option(
        EntityType.all,
        "--entity",
        "-e",
        help="Entity to seed (user, log, all)",
    ),
    count: int = typer.Option(
        10,
        "--count",
        "-c",
        help="Number of records to seed per entity",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        "-d",
        help="Preview without making changes",
    ),
    test_db: bool = typer.Option(
        False,
        "--test-db",
        "-t",
        help="Use test database instead of development",
    ),
) -> None:
    """Seed database with sample data."""
    if dry_run:
        Console.dry_run("Running in dry-run mode - no changes will be made")

    db_label = "test" if test_db else "development"
    Console.info(f"Seeding {entity.value} to {db_label} database...", verbose)

    seeders = get_seeders(entity, test_db)
    total_seeded = 0

    for seeder in seeders:
        Console.info(
            f"Seeding {seeder.entity_name} ({seeder.database_type})...", verbose
        )
        try:
            seeded = _run_seed(seeder, count, dry_run)
            total_seeded += seeded
            Console.success(f"Seeded {seeded} {seeder.entity_name}(s)")
        except Exception as e:
            Console.error(f"Failed to seed {seeder.entity_name}: {e}")
            raise typer.Exit(1)

    Console.success(f"Total seeded: {total_seeded} record(s)")


@run_async
async def _run_seed(seeder, count: int, dry_run: bool) -> int:
    """Run seeder asynchronously."""
    return await seeder.seed(count=count, dry_run=dry_run)


@app.command()
def clear(
    entity: EntityType = typer.Option(
        EntityType.all,
        "--entity",
        "-e",
        help="Entity to clear (user, log, all)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        "-d",
        help="Preview without making changes",
    ),
    test_db: bool = typer.Option(
        False,
        "--test-db",
        "-t",
        help="Use test database instead of development",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Skip confirmation prompt",
    ),
) -> None:
    """Clear seeded data from database."""
    if not force and not dry_run:
        confirm = typer.confirm(
            f"Are you sure you want to clear {entity.value} data?",
            default=False,
        )
        if not confirm:
            Console.warning("Operation cancelled")
            raise typer.Exit(0)

    if dry_run:
        Console.dry_run("Running in dry-run mode - no changes will be made")

    db_label = "test" if test_db else "development"
    Console.info(f"Clearing {entity.value} from {db_label} database...", verbose)

    seeders = get_seeders(entity, test_db)
    total_cleared = 0

    for seeder in seeders:
        Console.info(
            f"Clearing {seeder.entity_name} ({seeder.database_type})...", verbose
        )
        try:
            cleared = _run_clear(seeder, dry_run)
            total_cleared += cleared
            Console.success(f"Cleared {cleared} {seeder.entity_name}(s)")
        except Exception as e:
            Console.error(f"Failed to clear {seeder.entity_name}: {e}")
            raise typer.Exit(1)

    Console.success(f"Total cleared: {total_cleared} record(s)")


@run_async
async def _run_clear(seeder, dry_run: bool) -> int:
    """Run clear asynchronously."""
    return await seeder.clear(dry_run=dry_run)


@app.command()
def status(
    entity: EntityType = typer.Option(
        EntityType.all,
        "--entity",
        "-e",
        help="Entity to check (user, log, all)",
    ),
    test_db: bool = typer.Option(
        False,
        "--test-db",
        "-t",
        help="Use test database instead of development",
    ),
) -> None:
    """Show current seeding status (record counts)."""
    db_label = "test" if test_db else "development"
    print(f"\nDatabase Status ({db_label}):")
    print("=" * 50)

    seeders = get_seeders(entity, test_db)
    widths = [15, 15, 10]

    Console.table_header(["Entity", "Database", "Count"], widths)

    for seeder in seeders:
        try:
            record_count = _run_count(seeder)
            Console.table_row(
                [seeder.entity_name, seeder.database_type, str(record_count)],
                widths,
            )
        except Exception as e:
            Console.table_row(
                [seeder.entity_name, seeder.database_type, f"Error: {e}"],
                widths,
            )

    print()


@run_async
async def _run_count(seeder) -> int:
    """Run count asynchronously."""
    return await seeder.count()
