"""SQLAlchemy TrainingTypeConfig repository implementation."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.training.entities.training_type_config import TrainingTypeConfig
from src.domain.training.repositories.training_type_config_repository import (
    TrainingTypeConfigRepository,
)
from src.infrastructure.database.models.training_model import TrainingTypeConfigModel


class SQLAlchemyTrainingTypeConfigRepository(TrainingTypeConfigRepository):
    """SQLAlchemy implementation of TrainingTypeConfigRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _model_to_entity(self, model: TrainingTypeConfigModel) -> TrainingTypeConfig:
        """Convert TrainingTypeConfigModel to TrainingTypeConfig entity."""
        return TrainingTypeConfig(
            id=model.id,
            code=model.code,
            name=model.name,
            description=model.description,
            is_active=model.is_active,
            display_order=model.display_order,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _entity_to_model(self, entity: TrainingTypeConfig) -> TrainingTypeConfigModel:
        """Convert TrainingTypeConfig entity to TrainingTypeConfigModel."""
        return TrainingTypeConfigModel(
            id=entity.id,
            code=entity.code,
            name=entity.name,
            description=entity.description,
            is_active=entity.is_active,
            display_order=entity.display_order,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def get_by_id(self, id: UUID) -> TrainingTypeConfig | None:
        """Get training type by ID."""
        stmt = select(TrainingTypeConfigModel).where(TrainingTypeConfigModel.id == id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def get_by_code(self, code: str) -> TrainingTypeConfig | None:
        """Get training type by code."""
        stmt = select(TrainingTypeConfigModel).where(TrainingTypeConfigModel.code == code.lower())
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False,
    ) -> list[TrainingTypeConfig]:
        """Get all training types with pagination."""
        stmt = select(TrainingTypeConfigModel)

        if active_only:
            stmt = stmt.where(TrainingTypeConfigModel.is_active == True)  # noqa: E712

        stmt = stmt.order_by(TrainingTypeConfigModel.display_order)
        stmt = stmt.offset(skip).limit(limit)

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    async def add(self, entity: TrainingTypeConfig) -> TrainingTypeConfig:
        """Add a new training type."""
        model = self._entity_to_model(entity)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._model_to_entity(model)

    async def update(self, entity: TrainingTypeConfig) -> TrainingTypeConfig:
        """Update an existing training type."""
        stmt = select(TrainingTypeConfigModel).where(TrainingTypeConfigModel.id == entity.id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            model.name = entity.name
            model.description = entity.description
            model.is_active = entity.is_active
            model.display_order = entity.display_order
            model.updated_at = entity.updated_at
            await self._session.flush()
            await self._session.refresh(model)
            return self._model_to_entity(model)

        raise ValueError(f"TrainingTypeConfig with id {entity.id} not found")

    async def delete(self, id: UUID) -> bool:
        """Delete a training type by ID."""
        stmt = select(TrainingTypeConfigModel).where(TrainingTypeConfigModel.id == id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False

    async def exists(self, id: UUID) -> bool:
        """Check if training type exists."""
        stmt = select(func.count(TrainingTypeConfigModel.id)).where(
            TrainingTypeConfigModel.id == id
        )
        result = await self._session.execute(stmt)
        return (result.scalar() or 0) > 0

    async def count(self, active_only: bool = False) -> int:
        """Count total number of training types."""
        stmt = select(func.count(TrainingTypeConfigModel.id))
        if active_only:
            stmt = stmt.where(TrainingTypeConfigModel.is_active == True)  # noqa: E712
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def code_exists(self, code: str, exclude_id: UUID | None = None) -> bool:
        """Check if training type code already exists."""
        stmt = select(func.count(TrainingTypeConfigModel.id)).where(
            TrainingTypeConfigModel.code == code.lower()
        )
        if exclude_id:
            stmt = stmt.where(TrainingTypeConfigModel.id != exclude_id)
        result = await self._session.execute(stmt)
        return (result.scalar() or 0) > 0
