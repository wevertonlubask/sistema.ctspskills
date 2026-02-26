"""Upload logo use case."""

from pathlib import Path
from uuid import uuid4

from src.application.platform.dtos.platform_settings_dto import (
    PlatformSettingsDTO,
    UploadLogoDTO,
)
from src.config.settings import get_settings
from src.domain.platform.entities.platform_settings import PlatformSettings
from src.domain.platform.exceptions import InvalidLogoException
from src.domain.platform.repositories.platform_settings_repository import (
    PlatformSettingsRepository,
)


class UploadLogoUseCase:
    """Use case for uploading platform logo."""

    def __init__(self, repository: PlatformSettingsRepository) -> None:
        """Initialize use case.

        Args:
            repository: Platform settings repository.
        """
        self._repository = repository
        self._settings = get_settings()

    async def execute(self, dto: UploadLogoDTO) -> PlatformSettingsDTO:
        """Upload and save a logo file.

        Args:
            dto: Upload data with file content and metadata.

        Returns:
            Updated PlatformSettingsDTO.

        Raises:
            InvalidLogoException: If file type or size is invalid.
        """
        # Validate file type
        if not PlatformSettings.is_valid_logo_type(dto.mime_type):
            raise InvalidLogoException(
                f"File type '{dto.mime_type}' is not allowed. "
                f"Allowed: {', '.join(PlatformSettings.ALLOWED_LOGO_TYPES)}"
            )

        # Validate file size
        file_size = len(dto.file_content)
        if not PlatformSettings.is_valid_file_size(file_size):
            max_mb = PlatformSettings.MAX_LOGO_SIZE / (1024 * 1024)
            raise InvalidLogoException(f"File exceeds maximum size of {max_mb}MB")

        # Generate unique filename
        extension = self._get_extension(dto.mime_type)
        prefix = "logo_collapsed" if dto.is_collapsed else "logo"
        filename = f"{prefix}_{uuid4()}{extension}"
        relative_path = f"platform/{filename}"
        full_path = Path(self._settings.upload_dir) / relative_path

        # Ensure directory exists
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        with open(full_path, "wb") as f:
            f.write(dto.file_content)

        # Update settings
        settings = await self._repository.get_or_create()
        url = f"/uploads/{relative_path}"

        if dto.is_collapsed:
            settings.update_logo_collapsed_url(url)
        else:
            settings.update_logo_url(url)

        updated = await self._repository.update(settings)
        return PlatformSettingsDTO.from_entity(updated)

    def _get_extension(self, mime_type: str) -> str:
        """Get file extension from MIME type."""
        extensions = {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/svg+xml": ".svg",
            "image/webp": ".webp",
        }
        return extensions.get(mime_type, ".png")
