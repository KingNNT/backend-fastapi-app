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
