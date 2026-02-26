"""SQLAlchemy Modality repository implementation."""

from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.modality.entities.competence import Competence
from src.domain.modality.entities.modality import Modality
from src.domain.modality.repositories.modality_repository import ModalityRepository
from src.domain.modality.value_objects.modality_code import ModalityCode
from src.infrastructure.database.models.modality_model import (
    CompetenceModel,
    ModalityModel,
)


class SQLAlchemyModalityRepository(ModalityRepository):
    """SQLAlchemy implementation of ModalityRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _competence_model_to_entity(self, model: CompetenceModel) -> Competence:
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

    def _model_to_entity(self, model: ModalityModel) -> Modality:
        """Convert ModalityModel to Modality entity."""
        competences = [self._competence_model_to_entity(c) for c in model.competences]

        return Modality(
            id=model.id,
            code=ModalityCode(model.code),
            name=model.name,
            description=model.description or "",
            is_active=model.is_active,
            min_training_hours=model.min_training_hours,
            competences=competences,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _entity_to_model(self, entity: Modality) -> ModalityModel:
        """Convert Modality entity to ModalityModel."""
        return ModalityModel(
            id=entity.id,
            code=entity.code.value,
            name=entity.name,
            description=entity.description,
            is_active=entity.is_active,
            min_training_hours=entity.min_training_hours,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def get_by_id(self, id: UUID) -> Modality | None:
        """Get modality by ID."""
        stmt = (
            select(ModalityModel)
            .where(ModalityModel.id == id)
            .options(selectinload(ModalityModel.competences))
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def get_by_code(self, code: str) -> Modality | None:
        """Get modality by code."""
        stmt = (
            select(ModalityModel)
            .where(ModalityModel.code == code.upper())
            .options(selectinload(ModalityModel.competences))
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False,
    ) -> list[Modality]:
        """Get all modalities with pagination."""
        stmt = select(ModalityModel).options(selectinload(ModalityModel.competences))

        if active_only:
            stmt = stmt.where(ModalityModel.is_active == True)  # noqa: E712

        stmt = stmt.offset(skip).limit(limit).order_by(ModalityModel.name)

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    async def add(self, entity: Modality) -> Modality:
        """Add a new modality."""
        model = self._entity_to_model(entity)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model, ["competences"])
        return self._model_to_entity(model)

    async def update(self, entity: Modality) -> Modality:
        """Update an existing modality."""
        stmt = select(ModalityModel).where(ModalityModel.id == entity.id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            model.code = entity.code.value
            model.name = entity.name
            model.description = entity.description
            model.is_active = entity.is_active
            model.min_training_hours = entity.min_training_hours
            model.updated_at = entity.updated_at
            await self._session.flush()
            await self._session.refresh(model, ["competences"])
            return self._model_to_entity(model)

        raise ValueError(f"Modality with id {entity.id} not found")

    async def delete(self, id: UUID) -> bool:
        """Delete a modality by ID."""
        stmt = select(ModalityModel).where(ModalityModel.id == id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False

    async def exists(self, id: UUID) -> bool:
        """Check if modality exists."""
        stmt = select(func.count(ModalityModel.id)).where(ModalityModel.id == id)
        result = await self._session.execute(stmt)
        return (result.scalar() or 0) > 0

    async def count(self, active_only: bool = False) -> int:
        """Count total number of modalities."""
        stmt = select(func.count(ModalityModel.id))
        if active_only:
            stmt = stmt.where(ModalityModel.is_active == True)  # noqa: E712
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def code_exists(self, code: str, exclude_id: UUID | None = None) -> bool:
        """Check if modality code already exists."""
        stmt = select(func.count(ModalityModel.id)).where(ModalityModel.code == code.upper())
        if exclude_id:
            stmt = stmt.where(ModalityModel.id != exclude_id)
        result = await self._session.execute(stmt)
        return (result.scalar() or 0) > 0

    async def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Modality]:
        """Search modalities by name or code."""
        search_pattern = f"%{query}%"
        stmt = (
            select(ModalityModel)
            .where(
                or_(
                    ModalityModel.name.ilike(search_pattern),
                    ModalityModel.code.ilike(search_pattern),
                )
            )
            .options(selectinload(ModalityModel.competences))
            .offset(skip)
            .limit(limit)
            .order_by(ModalityModel.name)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]
