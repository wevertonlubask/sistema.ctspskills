"""Platform settings DTOs."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.domain.platform.entities.platform_settings import PlatformSettings


@dataclass
class PlatformSettingsDTO:
    """Platform settings data transfer object."""

    id: UUID
    platform_name: str
    platform_subtitle: str | None
    browser_title: str
    logo_url: str | None
    logo_collapsed_url: str | None
    favicon_url: str | None
    primary_color: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, entity: PlatformSettings) -> "PlatformSettingsDTO":
        """Create DTO from entity."""
        return cls(
            id=entity.id,
            platform_name=entity.platform_name,
            platform_subtitle=entity.platform_subtitle,
            browser_title=entity.browser_title,
            logo_url=entity.logo_url,
            logo_collapsed_url=entity.logo_collapsed_url,
            favicon_url=entity.favicon_url,
            primary_color=entity.primary_color,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )


@dataclass
class UpdatePlatformSettingsDTO:
    """DTO for updating platform settings."""

    platform_name: str | None = None
    platform_subtitle: str | None = None
    browser_title: str | None = None
    primary_color: str | None = None


@dataclass
class UploadLogoDTO:
    """DTO for uploading logo."""

    file_content: bytes
    file_name: str
    mime_type: str
    is_collapsed: bool = False


@dataclass
class UploadFaviconDTO:
    """DTO for uploading favicon."""

    file_content: bytes
    file_name: str
    mime_type: str
