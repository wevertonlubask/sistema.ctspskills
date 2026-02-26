"""SQLAlchemy implementation of PlatformSettingsRepository."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.platform.entities.platform_settings import PlatformSettings
from src.domain.platform.repositories.platform_settings_repository import (
    PlatformSettingsRepository,
)
from src.infrastructure.database.models.platform_model import PlatformSettingsModel


class SQLAlchemyPlatformSettingsRepository(PlatformSettingsRepository):
    """SQLAlchemy implementation of PlatformSettingsRepository."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy async session.
        """
        self._session = session

    def _model_to_entity(self, model: PlatformSettingsModel) -> PlatformSettings:
        """Convert database model to domain entity.

        Args:
            model: Database model.

        Returns:
            Domain entity.
        """
        return PlatformSettings(
            id=model.id,
            platform_name=model.platform_name,
            platform_subtitle=model.platform_subtitle,
            browser_title=model.browser_title,
            logo_url=model.logo_url,
            logo_collapsed_url=model.logo_collapsed_url,
            favicon_url=model.favicon_url,
            primary_color=model.primary_color,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _entity_to_model(self, entity: PlatformSettings) -> PlatformSettingsModel:
        """Convert domain entity to database model.

        Args:
            entity: Domain entity.

        Returns:
            Database model.
        """
        return PlatformSettingsModel(
            id=entity.id,
            singleton_key="settings",
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

    async def get(self) -> PlatformSettings | None:
        """Get platform settings (singleton).

        Returns:
            PlatformSettings if exists, None otherwise.
        """
        stmt = select(PlatformSettingsModel).where(
            PlatformSettingsModel.singleton_key == "settings"
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._model_to_entity(model)

    async def get_or_create(self) -> PlatformSettings:
        """Get platform settings or create with defaults.

        Returns:
            PlatformSettings entity.
        """
        settings = await self.get()

        if settings is not None:
            return settings

        # Create with default values
        default_settings = PlatformSettings.create_default()
        model = self._entity_to_model(default_settings)

        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)

        return self._model_to_entity(model)

    async def update(self, settings: PlatformSettings) -> PlatformSettings:
        """Update platform settings.

        Args:
            settings: Settings to update.

        Returns:
            Updated settings.
        """
        stmt = select(PlatformSettingsModel).where(
            PlatformSettingsModel.singleton_key == "settings"
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            # Create if doesn't exist
            model = self._entity_to_model(settings)
            self._session.add(model)
        else:
            # Update existing
            model.platform_name = settings.platform_name
            model.platform_subtitle = settings.platform_subtitle
            model.browser_title = settings.browser_title
            model.logo_url = settings.logo_url
            model.logo_collapsed_url = settings.logo_collapsed_url
            model.favicon_url = settings.favicon_url
            model.primary_color = settings.primary_color
            model.updated_at = settings.updated_at

        await self._session.flush()
        await self._session.refresh(model)

        return self._model_to_entity(model)
