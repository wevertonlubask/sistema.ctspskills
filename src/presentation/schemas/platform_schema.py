"""Platform settings schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PlatformSettingsResponse(BaseModel):
    """Platform settings response schema."""

    id: UUID = Field(..., description="Settings unique identifier")
    platform_name: str = Field(..., description="Platform name displayed in header")
    platform_subtitle: str | None = Field(None, description="Subtitle below the name")
    browser_title: str = Field(..., description="Browser tab title")
    logo_url: str | None = Field(None, description="URL to main logo")
    logo_collapsed_url: str | None = Field(None, description="URL to collapsed sidebar logo")
    favicon_url: str | None = Field(None, description="URL to favicon")
    primary_color: str | None = Field(None, description="Primary color hex code")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "platform_name": "SPSkills",
                "platform_subtitle": "Sistema de Treinamento",
                "browser_title": "SPSkills - Treinamento",
                "logo_url": "/uploads/platform/logo_123.png",
                "logo_collapsed_url": "/uploads/platform/logo_collapsed_123.png",
                "favicon_url": "/uploads/platform/favicon_123.ico",
                "primary_color": "#3B82F6",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            }
        },
    }


class UpdatePlatformSettingsRequest(BaseModel):
    """Request schema for updating platform settings."""

    platform_name: str | None = Field(None, min_length=1, max_length=100)
    platform_subtitle: str | None = Field(None, max_length=200)
    browser_title: str | None = Field(None, min_length=1, max_length=100)
    primary_color: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")

    model_config = {
        "json_schema_extra": {
            "example": {
                "platform_name": "My Platform",
                "platform_subtitle": "Training System",
                "browser_title": "My Platform - Home",
                "primary_color": "#3B82F6",
            }
        }
    }
