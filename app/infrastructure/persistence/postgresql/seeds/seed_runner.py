#!/usr/bin/env python3
"""
Database seeder runner

This script runs all seeders to populate the database with sample data.
"""

import asyncio
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))

from app.infrastructure.persistence.postgresql.database import postgres_db_manager
from app.infrastructure.persistence.postgresql.seeds.user_seeder import UserSeeder


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
