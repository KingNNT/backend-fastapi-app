import asyncio
from uuid import uuid4
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.databases.sql.manager import db_manager
from app.internal.models.sql.user import User


class UserSeeder:
    """Seeder class for Employee data"""

    @staticmethod
    def get_sample_data():
        """Return sample user data"""
        return [
            User(
                first_name="Jennifer",
                last_name="Martinez",
            )
        ]

    @staticmethod
    async def seed_users(session: AsyncSession):
        """Seed user data"""
        print("🌱 Seeding User data...")

        # Check if user already exist
        result = await session.execute(select(User))
        existing_user = result.scalars().all()

        if existing_user:
            print(f"⚠️  Found {len(existing_user)} existing user. Skipping seed.")
            return

        # Create sample user
        sample_users = [
            User(
                id=uuid4(),
                first_name="John",
                last_name="Doe",
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
        ]

        # Add user to session
        for user in sample_users:
            session.add(user)

        # Commit changes
        await session.commit()

        print(f"✅ Successfully seeded {len(sample_users)} employees")

    @staticmethod
    async def clear_users(session: AsyncSession):
        """Clear all user data"""
        print("🧹 Clearing User data...")

        # Delete all user
        result = await session.execute(select(User))
        users = result.scalars().all()

        for user in users:
            await session.delete(user)

        await session.commit()
        print(f"✅ Cleared {len(users)} employees")


async def main():
    """Main seeder function"""
    await db_manager.connect()

    if db_manager.session_maker is None:
        raise RuntimeError("Database session maker is not initialized")

    async with db_manager.session_maker() as session:
        await UserSeeder.seed_users(session)

    await db_manager.close()


if __name__ == "__main__":
    asyncio.run(main())
