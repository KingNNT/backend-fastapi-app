"""System DTOs for the presentation layer."""

from pydantic import BaseModel, Field


class HealthCheckResponse(BaseModel):
    """Response DTO for health check."""

    status: str = Field(..., description="Health status")
    message: str = Field(..., description="Health message")


class VersionResponse(BaseModel):
    """Response DTO for version information."""

    name: str = Field(..., description="Application name")
    version: str = Field(..., description="Application version")
    environment: str = Field(..., description="Current environment")
