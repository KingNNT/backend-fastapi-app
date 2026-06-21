import importlib.metadata
from functools import lru_cache

from pydantic import BaseModel, ConfigDict


class VersionInfo(BaseModel):
    model_config = ConfigDict(frozen=True)

    version: str
    build_date: str | None = None
    commit_hash: str | None = None
    python_version: str


@lru_cache()
def get_version_info() -> VersionInfo:
    """Get application version information."""
    import sys

    try:
        # Get version from package metadata
        version = importlib.metadata.version("backend-fastapi-app")
    except importlib.metadata.PackageNotFoundError:
        # Fallback to pyproject.toml version
        version = "0.1.0"

    return VersionInfo(
        version=version,
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
    )


@lru_cache()
def get_app_version() -> str:
    """Get application version string."""
    return get_version_info().version
