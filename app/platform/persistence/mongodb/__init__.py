"""MongoDB connection manager (platform-level)."""

from app.platform.persistence.mongodb.database import mongo_db_manager

__all__ = ["mongo_db_manager"]
