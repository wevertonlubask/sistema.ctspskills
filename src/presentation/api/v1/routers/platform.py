"""Platform settings router."""

from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.platform.dtos.platform_settings_dto import (
    UpdatePlatformSettingsDTO,
    UploadFaviconDTO,
    UploadLogoDTO,
)
from src.application.platform.use_cases import (
    GetPlatformSettingsUseCase,
    UpdatePlatformSettingsUseCase,
    UploadFaviconUseCase,
    UploadLogoUseCase,
)
from src.domain.identity.entities.user import User
from src.domain.platform.exceptions import InvalidFaviconException, InvalidLogoException
from src.infrastructure.database.repositories.platform_settings_repository_impl import (
    SQLAlchemyPlatformSettingsRepository,
)
from src.presentation.api.v1.dependencies.auth import require_super_admin
from src.presentation.api.v1.dependencies.database import get_db
from src.presentation.schemas.platform_schema import (
    PlatformSettingsResponse,
    UpdatePlatformSettingsRequest,
)

router = APIRouter()


@router.get(
    "",
    response_model=PlatformSettingsResponse,
    summary="Get platform settings",
    description="Get current platform settings. Public endpoint for login page branding.",
)
async def get_platform_settings(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PlatformSettingsResponse:
    """Get platform settings (public endpoint)."""
    repository = SQLAlchemyPlatformSettingsRepository(db)
    use_case = GetPlatformSettingsUseCase(repository=repository)
    result = await use_case.execute()
    await db.commit()

    return PlatformSettingsResponse(
        id=result.id,
        platform_name=result.platform_name,
        platform_subtitle=result.platform_subtitle,
        browser_title=result.browser_title,
        logo_url=result.logo_url,
        logo_collapsed_url=result.logo_collapsed_url,
        favicon_url=result.favicon_url,
        primary_color=result.primary_color,
        created_at=result.created_at,
        updated_at=result.updated_at,
    )


@router.put(
    "",
    response_model=PlatformSettingsResponse,
    summary="Update platform settings",
    description="Update platform settings. Requires super admin role.",
)
async def update_platform_settings(
    request: UpdatePlatformSettingsRequest,
    current_user: Annotated[User, Depends(require_super_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PlatformSettingsResponse:
    """Update platform settings (admin only)."""
    repository = SQLAlchemyPlatformSettingsRepository(db)
    use_case = UpdatePlatformSettingsUseCase(repository=repository)

    dto = UpdatePlatformSettingsDTO(
        platform_name=request.platform_name,
        platform_subtitle=request.platform_subtitle,
        browser_title=request.browser_title,
        primary_color=request.primary_color,
    )

    result = await use_case.execute(dto)
    await db.commit()

    return PlatformSettingsResponse(
        id=result.id,
        platform_name=result.platform_name,
        platform_subtitle=result.platform_subtitle,
        browser_title=result.browser_title,
        logo_url=result.logo_url,
        logo_collapsed_url=result.logo_collapsed_url,
        favicon_url=result.favicon_url,
        primary_color=result.primary_color,
        created_at=result.created_at,
        updated_at=result.updated_at,
    )


@router.post(
    "/logo",
    response_model=PlatformSettingsResponse,
    summary="Upload platform logo",
    description="Upload main logo for the platform. Requires super admin role.",
)
async def upload_logo(
    file: Annotated[UploadFile, File(description="Logo image file")],
    current_user: Annotated[User, Depends(require_super_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PlatformSettingsResponse:
    """Upload platform logo (admin only)."""
    content = await file.read()

    repository = SQLAlchemyPlatformSettingsRepository(db)
    use_case = UploadLogoUseCase(repository=repository)

    try:
        dto = UploadLogoDTO(
            file_content=content,
            file_name=file.filename or "logo",
            mime_type=file.content_type or "image/png",
            is_collapsed=False,
        )
        result = await use_case.execute(dto)
        await db.commit()
    except InvalidLogoException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

    return PlatformSettingsResponse(
        id=result.id,
        platform_name=result.platform_name,
        platform_subtitle=result.platform_subtitle,
        browser_title=result.browser_title,
        logo_url=result.logo_url,
        logo_collapsed_url=result.logo_collapsed_url,
        favicon_url=result.favicon_url,
        primary_color=result.primary_color,
        created_at=result.created_at,
        updated_at=result.updated_at,
    )


@router.post(
    "/logo-collapsed",
    response_model=PlatformSettingsResponse,
    summary="Upload collapsed logo",
    description="Upload logo for collapsed sidebar. Requires super admin role.",
)
async def upload_logo_collapsed(
    file: Annotated[UploadFile, File(description="Collapsed logo image file")],
    current_user: Annotated[User, Depends(require_super_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PlatformSettingsResponse:
    """Upload collapsed logo (admin only)."""
    content = await file.read()

    repository = SQLAlchemyPlatformSettingsRepository(db)
    use_case = UploadLogoUseCase(repository=repository)

    try:
        dto = UploadLogoDTO(
            file_content=content,
            file_name=file.filename or "logo_collapsed",
            mime_type=file.content_type or "image/png",
            is_collapsed=True,
        )
        result = await use_case.execute(dto)
        await db.commit()
    except InvalidLogoException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

    return PlatformSettingsResponse(
        id=result.id,
        platform_name=result.platform_name,
        platform_subtitle=result.platform_subtitle,
        browser_title=result.browser_title,
        logo_url=result.logo_url,
        logo_collapsed_url=result.logo_collapsed_url,
        favicon_url=result.favicon_url,
        primary_color=result.primary_color,
        created_at=result.created_at,
        updated_at=result.updated_at,
    )


@router.post(
    "/favicon",
    response_model=PlatformSettingsResponse,
    summary="Upload favicon",
    description="Upload favicon for browser tab. Requires super admin role.",
)
async def upload_favicon(
    file: Annotated[UploadFile, File(description="Favicon file")],
    current_user: Annotated[User, Depends(require_super_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PlatformSettingsResponse:
    """Upload favicon (admin only)."""
    content = await file.read()

    repository = SQLAlchemyPlatformSettingsRepository(db)
    use_case = UploadFaviconUseCase(repository=repository)

    try:
        dto = UploadFaviconDTO(
            file_content=content,
            file_name=file.filename or "favicon",
            mime_type=file.content_type or "image/x-icon",
        )
        result = await use_case.execute(dto)
        await db.commit()
    except InvalidFaviconException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

    return PlatformSettingsResponse(
        id=result.id,
        platform_name=result.platform_name,
        platform_subtitle=result.platform_subtitle,
        browser_title=result.browser_title,
        logo_url=result.logo_url,
        logo_collapsed_url=result.logo_collapsed_url,
        favicon_url=result.favicon_url,
        primary_color=result.primary_color,
        created_at=result.created_at,
        updated_at=result.updated_at,
    )
