"""Platform settings repository interface."""

from abc import ABC, abstractmethod

from src.domain.platform.entities.platform_settings import PlatformSettings


class PlatformSettingsRepository(ABC):
    """Repository interface for PlatformSettings entity."""

    @abstractmethod
    async def get(self) -> PlatformSettings | None:
        """Get platform settings (singleton).

        Returns:
            PlatformSettings if exists, None otherwise.
        """
        pass

    @abstractmethod
    async def get_or_create(self) -> PlatformSettings:
        """Get platform settings or create with defaults.

        Returns:
            PlatformSettings entity.
        """
        pass

    @abstractmethod
    async def update(self, settings: PlatformSettings) -> PlatformSettings:
        """Update platform settings.

        Args:
            settings: Settings to update.

        Returns:
            Updated settings.
        """
        pass
