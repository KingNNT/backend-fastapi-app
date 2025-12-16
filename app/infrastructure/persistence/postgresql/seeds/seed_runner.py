#!/usr/bin/env python3
"""
Database seeder runner

DEPRECATED: This script is deprecated. Use the new Typer CLI instead:

    python -m app.infrastructure.cli.main db seed
    python -m app.infrastructure.cli.main db clear
    python -m app.infrastructure.cli.main db status

Or via Makefile:

    make seed
    make seed-clear
    make seed-status

This script is kept for backward compatibility but will be removed in a future release.
"""

import asyncio
import sys
import warnings
from pathlib import Path

# Emit deprecation warning
warnings.warn(
    "seed_runner.py is deprecated. "
    "Use 'python -m app.infrastructure.cli.main db' instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))

from app.infrastructure.persistence.postgresql.database import (  # noqa: E402
    postgres_db_manager,
)
from app.infrastructure.persistence.postgresql.seeds.user_seeder import (  # noqa: E402
    UserSeeder,
)


async def run_all_seeders():
    """Run all database seeders"""
    print("🚀 Starting database seeding...")
    print("=" * 50)

    try:
        # Connect to database
        await postgres_db_manager.connect()

        if postgres_db_manager.session_maker is None:
            raise RuntimeError("Database session maker is not initialized")

        async with postgres_db_manager.session_maker() as session:
            print("👥 Seeding users...")
            await UserSeeder.seed_users(session)

        print("=" * 50)
        print("✅ All seeders completed successfully!")

    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        sys.exit(1)
    finally:
        await postgres_db_manager.close()


async def clear_all_data():
    """Clear all seeded data"""
    print("🧹 Clearing all seeded data...")
    print("=" * 50)

    try:
        # Connect to database
        await postgres_db_manager.connect()

        if postgres_db_manager.session_maker is None:
            raise RuntimeError("Database session maker is not initialized")

        async with postgres_db_manager.session_maker() as session:
            # Clear employee data
            await UserSeeder.clear_users(session)

        print("=" * 50)
        print("✅ All data cleared successfully!")

    except Exception as e:
        print(f"❌ Error during clearing: {e}")
        sys.exit(1)
    finally:
        await postgres_db_manager.close()


def main():
    """Main function"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "clear":
            asyncio.run(clear_all_data())
        elif command == "seed":
            asyncio.run(run_all_seeders())
        else:
            print("Usage: python seed_runner.py [seed|clear]")
            sys.exit(1)
    else:
        # Default action is to seed
        asyncio.run(run_all_seeders())


if __name__ == "__main__":
    main()
