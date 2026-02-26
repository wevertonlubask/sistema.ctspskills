"""SQLAlchemy Competence repository implementation."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.modality.entities.competence import Competence
from src.domain.modality.repositories.competence_repository import CompetenceRepository
from src.infrastructure.database.models.modality_model import CompetenceModel


class SQLAlchemyCompetenceRepository(CompetenceRepository):
    """SQLAlchemy implementation of CompetenceRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _model_to_entity(self, model: CompetenceModel) -> Competence:
        """Convert CompetenceModel to Competence entity."""
        return Competence(
            id=model.id,
            name=model.name,
            description=model.description or "",
            modality_id=model.modality_id,
            weight=model.weight,
            max_score=model.max_score,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _entity_to_model(self, entity: Competence) -> CompetenceModel:
        """Convert Competence entity to CompetenceModel."""
        return CompetenceModel(
            id=entity.id,
            modality_id=entity.modality_id,
            name=entity.name,
            description=entity.description,
            weight=entity.weight,
            max_score=entity.max_score,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def get_by_id(self, id: UUID) -> Competence | None:
        """Get competence by ID."""
        stmt = select(CompetenceModel).where(CompetenceModel.id == id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def get_by_modality(
        self,
        modality_id: UUID,
        active_only: bool = False,
    ) -> list[Competence]:
        """Get all competences for a modality."""
        stmt = select(CompetenceModel).where(CompetenceModel.modality_id == modality_id)
        if active_only:
            stmt = stmt.where(CompetenceModel.is_active == True)  # noqa: E712
        stmt = stmt.order_by(CompetenceModel.name)

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    async def get_by_name_and_modality(
        self,
        name: str,
        modality_id: UUID,
    ) -> Competence | None:
        """Get competence by name within a modality."""
        stmt = select(CompetenceModel).where(
            CompetenceModel.modality_id == modality_id,
            CompetenceModel.name == name,
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def add(self, entity: Competence) -> Competence:
        """Add a new competence."""
        model = self._entity_to_model(entity)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._model_to_entity(model)

    async def update(self, entity: Competence) -> Competence:
        """Update an existing competence."""
        stmt = select(CompetenceModel).where(CompetenceModel.id == entity.id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            model.name = entity.name
            model.description = entity.description
            model.weight = entity.weight
            model.max_score = entity.max_score
            model.is_active = entity.is_active
            model.updated_at = entity.updated_at
            await self._session.flush()
            await self._session.refresh(model)
            return self._model_to_entity(model)

        raise ValueError(f"Competence with id {entity.id} not found")

    async def delete(self, id: UUID) -> bool:
        """Delete a competence by ID."""
        stmt = select(CompetenceModel).where(CompetenceModel.id == id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False

    async def exists(self, id: UUID) -> bool:
        """Check if competence exists."""
        stmt = select(func.count(CompetenceModel.id)).where(CompetenceModel.id == id)
        result = await self._session.execute(stmt)
        return (result.scalar() or 0) > 0

    async def count_by_modality(
        self,
        modality_id: UUID,
        active_only: bool = False,
    ) -> int:
        """Count competences in a modality."""
        stmt = select(func.count(CompetenceModel.id)).where(
            CompetenceModel.modality_id == modality_id
        )
        if active_only:
            stmt = stmt.where(CompetenceModel.is_active == True)  # noqa: E712
        result = await self._session.execute(stmt)
        return result.scalar() or 0
