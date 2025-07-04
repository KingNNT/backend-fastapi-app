"""FastAPI dependencies for dependency injection.

This module contains dependency functions that can be used
with FastAPI's Depends() to inject services and other components.
"""

from app.internal.services.user import UserService


def get_user_service() -> UserService:
    """Get UserService instance.

    Returns:
        UserService: Instance of the user service
    """
    return UserService()


# Example of future dependencies:

# def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
#     """Get current authenticated user from JWT token."""
#     pass

# def get_database() -> Database:
#     """Get database connection."""
#     pass

# def get_redis_client() -> Redis:
#     """Get Redis client for caching."""
#     pass
