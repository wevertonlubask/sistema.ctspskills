"""Update platform settings use case."""

from src.application.platform.dtos.platform_settings_dto import (
    PlatformSettingsDTO,
    UpdatePlatformSettingsDTO,
)
from src.domain.platform.repositories.platform_settings_repository import (
    PlatformSettingsRepository,
)


class UpdatePlatformSettingsUseCase:
    """Use case for updating platform settings."""

    def __init__(self, repository: PlatformSettingsRepository) -> None:
        """Initialize use case.

        Args:
            repository: Platform settings repository.
        """
        self._repository = repository

    async def execute(self, dto: UpdatePlatformSettingsDTO) -> PlatformSettingsDTO:
        """Update platform settings.

        Args:
            dto: Update data.

        Returns:
            Updated PlatformSettingsDTO.
        """
        settings = await self._repository.get_or_create()

        if dto.platform_name is not None:
            settings.update_platform_name(dto.platform_name)
        if dto.platform_subtitle is not None:
            settings.update_platform_subtitle(dto.platform_subtitle)
        if dto.browser_title is not None:
            settings.update_browser_title(dto.browser_title)
        if dto.primary_color is not None:
            settings.update_primary_color(dto.primary_color)

        updated = await self._repository.update(settings)
        return PlatformSettingsDTO.from_entity(updated)
