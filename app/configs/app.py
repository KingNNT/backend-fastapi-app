from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # Application settings
    name: str = Field(default="backend-fastapi-app", description="Application name")
    version: str = Field(default="0.1.0", description="Application version")
    description: str = Field(
        default="Template for backend application use FastAPI",
        description="Application description",
    )

    # Server settings
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")

    # Environment settings
    environment: Literal["development", "staging", "production"] = Field(
        default="development", description="Environment name"
    )
    debug: bool = Field(default=False, description="Debug mode")

    # Security settings
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for signing",
    )
    cors_origins: list[str] = Field(default=["*"], description="CORS allowed origins")

    # MongoDB settings
    mongodb_url: str = Field(
        default="mongodb://localhost:27017", description="MongoDB connection URL"
    )
    mongodb_database: str = Field(
        default="backend_fastapi_app", description="MongoDB database name"
    )

    # PostgreSQL  settings
    postgres_user: str = Field(default="admin", description="PostgreSQL username")
    postgres_password: str = Field(default="example", description="PostgreSQL password")
    postgres_db: str = Field(
        default="database_develop", description="PostgreSQL database name"
    )
    postgres_host: str = Field(default="postgresql", description="PostgreSQL host")
    postgres_port: int = Field(default=5432, description="PostgreSQL port")

    @property
    def postgre_database_url(self) -> str:
        """Construct PostgreSQL database URL from components."""
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    # Redis settings
    redis_host: str = Field(default="redis", description="Redis host")
    redis_port: int = Field(default=6379, description="Redis port")
    redis_db: int = Field(default=0, description="Redis database")

    # Logging settings
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", description="Logging level"
    )

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache()
def get_app_config() -> AppConfig:
    return AppConfig()
