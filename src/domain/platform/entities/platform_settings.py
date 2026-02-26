"""Platform settings entity."""

from datetime import datetime
from uuid import UUID, uuid4

from src.shared.domain.entity import Entity
from src.shared.utils.date_utils import utc_now


class PlatformSettings(Entity[UUID]):
    """Platform settings entity (singleton).

    Stores global platform configuration including branding,
    logos, and visual customization options.
    """

    # Allowed image types for logos
    ALLOWED_LOGO_TYPES = ["image/jpeg", "image/png", "image/svg+xml", "image/webp"]
    ALLOWED_FAVICON_TYPES = [
        "image/x-icon",
        "image/png",
        "image/svg+xml",
        "image/vnd.microsoft.icon",
    ]
    MAX_LOGO_SIZE = 2 * 1024 * 1024  # 2MB

    def __init__(
        self,
        platform_name: str = "SPSkills",
        platform_subtitle: str | None = "Sistema de Treinamento",
        browser_title: str = "SPSkills",
        logo_url: str | None = None,
        logo_collapsed_url: str | None = None,
        favicon_url: str | None = None,
        primary_color: str | None = None,
        id: UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        """Initialize platform settings.

        Args:
            platform_name: Name of the platform displayed in header.
            platform_subtitle: Subtitle displayed below the name.
            browser_title: Title shown in browser tab.
            logo_url: URL/path to main logo.
            logo_collapsed_url: URL/path to collapsed sidebar logo.
            favicon_url: URL/path to favicon.
            primary_color: Hex color for branding (e.g., #3B82F6).
            id: Unique identifier.
            created_at: Creation timestamp.
            updated_at: Last update timestamp.
        """
        super().__init__(
            id=id or uuid4(),
            created_at=created_at or utc_now(),
            updated_at=updated_at or utc_now(),
        )
        self._platform_name = platform_name
        self._platform_subtitle = platform_subtitle
        self._browser_title = browser_title
        self._logo_url = logo_url
        self._logo_collapsed_url = logo_collapsed_url
        self._favicon_url = favicon_url
        self._primary_color = primary_color

    @property
    def platform_name(self) -> str:
        """Get platform name."""
        return self._platform_name

    @property
    def platform_subtitle(self) -> str | None:
        """Get platform subtitle."""
        return self._platform_subtitle

    @property
    def browser_title(self) -> str:
        """Get browser title."""
        return self._browser_title

    @property
    def logo_url(self) -> str | None:
        """Get logo URL."""
        return self._logo_url

    @property
    def logo_collapsed_url(self) -> str | None:
        """Get collapsed logo URL."""
        return self._logo_collapsed_url

    @property
    def favicon_url(self) -> str | None:
        """Get favicon URL."""
        return self._favicon_url

    @property
    def primary_color(self) -> str | None:
        """Get primary color."""
        return self._primary_color

    def update_platform_name(self, name: str) -> None:
        """Update platform name."""
        if name and len(name.strip()) > 0:
            self._platform_name = name.strip()
            self._touch()

    def update_platform_subtitle(self, subtitle: str | None) -> None:
        """Update platform subtitle."""
        self._platform_subtitle = subtitle.strip() if subtitle else None
        self._touch()

    def update_browser_title(self, title: str) -> None:
        """Update browser title."""
        if title and len(title.strip()) > 0:
            self._browser_title = title.strip()
            self._touch()

    def update_logo_url(self, url: str | None) -> None:
        """Update logo URL."""
        self._logo_url = url
        self._touch()

    def update_logo_collapsed_url(self, url: str | None) -> None:
        """Update collapsed logo URL."""
        self._logo_collapsed_url = url
        self._touch()

    def update_favicon_url(self, url: str | None) -> None:
        """Update favicon URL."""
        self._favicon_url = url
        self._touch()

    def update_primary_color(self, color: str | None) -> None:
        """Update primary color."""
        self._primary_color = color
        self._touch()

    @classmethod
    def is_valid_logo_type(cls, mime_type: str) -> bool:
        """Check if MIME type is valid for logos."""
        return mime_type in cls.ALLOWED_LOGO_TYPES

    @classmethod
    def is_valid_favicon_type(cls, mime_type: str) -> bool:
        """Check if MIME type is valid for favicons."""
        return mime_type in cls.ALLOWED_FAVICON_TYPES

    @classmethod
    def is_valid_file_size(cls, size: int) -> bool:
        """Check if file size is within limits."""
        return 0 < size <= cls.MAX_LOGO_SIZE

    @classmethod
    def create_default(cls) -> "PlatformSettings":
        """Create settings with default values."""
        return cls()
