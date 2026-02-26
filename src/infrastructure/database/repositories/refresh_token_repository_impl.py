"""SQLAlchemy RefreshToken repository implementation."""

from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.identity.entities.refresh_token import RefreshToken
from src.domain.identity.repositories.refresh_token_repository import RefreshTokenRepository
from src.infrastructure.database.models.user_model import RefreshTokenModel
from src.shared.utils.date_utils import utc_now


class SQLAlchemyRefreshTokenRepository(RefreshTokenRepository):
    """SQLAlchemy implementation of RefreshTokenRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _model_to_entity(self, model: RefreshTokenModel) -> RefreshToken:
        """Convert RefreshTokenModel to RefreshToken entity."""
        return RefreshToken(
            id=model.id,
            user_id=model.user_id,
            token=model.token,
            expires_at=model.expires_at,
            user_agent=model.user_agent,
            ip_address=model.ip_address,
            is_revoked=model.is_revoked,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _entity_to_model(self, entity: RefreshToken) -> RefreshTokenModel:
        """Convert RefreshToken entity to RefreshTokenModel."""
        return RefreshTokenModel(
            id=entity.id,
            user_id=entity.user_id,
            token=entity.token,
            expires_at=entity.expires_at,
            user_agent=entity.user_agent,
            ip_address=entity.ip_address,
            is_revoked=entity.is_revoked,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def get_by_id(self, id: UUID) -> RefreshToken | None:
        """Get refresh token by ID."""
        stmt = select(RefreshTokenModel).where(RefreshTokenModel.id == id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def get_by_token(self, token: str) -> RefreshToken | None:
        """Get refresh token by token string."""
        stmt = select(RefreshTokenModel).where(RefreshTokenModel.token == token)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def get_by_user_id(self, user_id: UUID) -> list[RefreshToken]:
        """Get all refresh tokens for a user."""
        stmt = (
            select(RefreshTokenModel)
            .where(RefreshTokenModel.user_id == user_id)
            .order_by(RefreshTokenModel.created_at.desc())
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    async def add(self, entity: RefreshToken) -> RefreshToken:
        """Add a new refresh token."""
        model = self._entity_to_model(entity)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._model_to_entity(model)

    async def update(self, entity: RefreshToken) -> RefreshToken:
        """Update an existing refresh token."""
        stmt = select(RefreshTokenModel).where(RefreshTokenModel.id == entity.id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            model.is_revoked = entity.is_revoked
            model.updated_at = entity.updated_at
            await self._session.flush()
            await self._session.refresh(model)
            return self._model_to_entity(model)

        raise ValueError(f"RefreshToken with id {entity.id} not found")

    async def delete(self, id: UUID) -> bool:
        """Delete a refresh token by ID."""
        stmt = delete(RefreshTokenModel).where(RefreshTokenModel.id == id)
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.rowcount > 0  # type: ignore[attr-defined, no-any-return]

    async def exists(self, id: UUID) -> bool:
        """Check if refresh token exists."""
        stmt = select(RefreshTokenModel.id).where(RefreshTokenModel.id == id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def revoke_all_for_user(self, user_id: UUID) -> int:
        """Revoke all refresh tokens for a user."""
        stmt = (
            update(RefreshTokenModel)
            .where(RefreshTokenModel.user_id == user_id)
            .where(RefreshTokenModel.is_revoked == False)  # noqa: E712
            .values(is_revoked=True, updated_at=utc_now())
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.rowcount  # type: ignore[attr-defined, no-any-return]

    async def delete_expired(self) -> int:
        """Delete all expired tokens."""
        stmt = delete(RefreshTokenModel).where(RefreshTokenModel.expires_at < utc_now())
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.rowcount  # type: ignore[attr-defined, no-any-return]
