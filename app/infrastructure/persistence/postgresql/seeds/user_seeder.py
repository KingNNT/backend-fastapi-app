import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.infrastructure.persistence.postgresql.models.user import UserModel
from app.platform.persistence.postgresql.database import postgres_db_manager


class UserSeeder:
    """Seeder class for User data"""

    @staticmethod
    async def seed_users(session: AsyncSession):
        """Seed user data"""
        print("🌱 Seeding User data...")

        # Check if user already exist
        result = await session.execute(select(UserModel))
        existing_user = result.scalars().all()

        if existing_user:
            print(f"⚠️  Found {len(existing_user)} existing user. Skipping seed.")
            return

        # Create sample users (timestamps use default_factory from BaseModel)
        sample_users = [
            UserModel(
                email="john@example.com",
                username="johndoe",
                password="hashed_password",
                full_name="John Doe",
                is_active=True,
            ),
        ]

        # Add user to session
        for user in sample_users:
            session.add(user)

        # Commit changes
        await session.commit()

        print(f"✅ Successfully seeded {len(sample_users)} users")

    @staticmethod
    async def clear_users(session: AsyncSession):
        """Clear all user data"""
        print("🧹 Clearing User data...")

        # Delete all user
        result = await session.execute(select(UserModel))
        users = result.scalars().all()

        for user in users:
            await session.delete(user)

        await session.commit()
        print(f"✅ Cleared {len(users)} users")


async def main():
    """Main seeder function"""
    await postgres_db_manager.connect()

    if postgres_db_manager.session_maker is None:
        raise RuntimeError("Database session maker is not initialized")

    async with postgres_db_manager.session_maker() as session:
        await UserSeeder.seed_users(session)

    await postgres_db_manager.close()


if __name__ == "__main__":
    asyncio.run(main())
