"""Get platform settings use case."""

from src.application.platform.dtos.platform_settings_dto import PlatformSettingsDTO
from src.domain.platform.repositories.platform_settings_repository import (
    PlatformSettingsRepository,
)


class GetPlatformSettingsUseCase:
    """Use case for retrieving platform settings."""

    def __init__(self, repository: PlatformSettingsRepository) -> None:
        """Initialize use case.

        Args:
            repository: Platform settings repository.
        """
        self._repository = repository

    async def execute(self) -> PlatformSettingsDTO:
        """Get platform settings (creates defaults if not exist).

        Returns:
            PlatformSettingsDTO with current settings.
        """
        settings = await self._repository.get_or_create()
        return PlatformSettingsDTO.from_entity(settings)
