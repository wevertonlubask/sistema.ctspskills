"""Platform use cases module."""

from src.application.platform.use_cases.get_platform_settings import GetPlatformSettingsUseCase
from src.application.platform.use_cases.update_platform_settings import (
    UpdatePlatformSettingsUseCase,
)
from src.application.platform.use_cases.upload_favicon import UploadFaviconUseCase
from src.application.platform.use_cases.upload_logo import UploadLogoUseCase

__all__ = [
    "GetPlatformSettingsUseCase",
    "UpdatePlatformSettingsUseCase",
    "UploadLogoUseCase",
    "UploadFaviconUseCase",
]
