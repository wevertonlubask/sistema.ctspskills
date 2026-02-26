"""SQLAlchemy Competitor repository implementation."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.modality.entities.competitor import Competitor
from src.domain.modality.repositories.competitor_repository import CompetitorRepository
from src.infrastructure.database.models.modality_model import (
    CompetitorModel,
    EnrollmentModel,
)


class SQLAlchemyCompetitorRepository(CompetitorRepository):
    """SQLAlchemy implementation of CompetitorRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _model_to_entity(self, model: CompetitorModel) -> Competitor:
        """Convert CompetitorModel to Competitor entity."""
        return Competitor(
            id=model.id,
            user_id=model.user_id,
            full_name=model.full_name,
            birth_date=model.birth_date,
            document_number=model.document_number,
            phone=model.phone,
            emergency_contact=model.emergency_contact,
            emergency_phone=model.emergency_phone,
            notes=model.notes,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _entity_to_model(self, entity: Competitor) -> CompetitorModel:
        """Convert Competitor entity to CompetitorModel."""
        return CompetitorModel(
            id=entity.id,
            user_id=entity.user_id,
            full_name=entity.full_name,
            birth_date=entity.birth_date,
            document_number=entity.document_number,
            phone=entity.phone,
            emergency_contact=entity.emergency_contact,
            emergency_phone=entity.emergency_phone,
            notes=entity.notes,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def get_by_id(self, id: UUID) -> Competitor | None:
        """Get competitor by ID."""
        stmt = select(CompetitorModel).where(CompetitorModel.id == id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def get_by_user_id(self, user_id: UUID) -> Competitor | None:
        """Get competitor by user ID."""
        stmt = select(CompetitorModel).where(CompetitorModel.user_id == user_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False,
    ) -> list[Competitor]:
        """Get all competitors with pagination."""
        stmt = select(CompetitorModel)

        if active_only:
            stmt = stmt.where(CompetitorModel.is_active == True)  # noqa: E712

        stmt = stmt.offset(skip).limit(limit).order_by(CompetitorModel.full_name)

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    async def get_by_modality(
        self,
        modality_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Competitor]:
        """Get competitors enrolled in a modality."""
        stmt = (
            select(CompetitorModel)
            .join(EnrollmentModel, CompetitorModel.id == EnrollmentModel.competitor_id)
            .where(EnrollmentModel.modality_id == modality_id)
            .where(EnrollmentModel.status == "active")
            .offset(skip)
            .limit(limit)
            .order_by(CompetitorModel.full_name)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    async def add(self, entity: Competitor) -> Competitor:
        """Add a new competitor."""
        model = self._entity_to_model(entity)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._model_to_entity(model)

    async def update(self, entity: Competitor) -> Competitor:
        """Update an existing competitor."""
        stmt = select(CompetitorModel).where(CompetitorModel.id == entity.id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            model.full_name = entity.full_name
            model.birth_date = entity.birth_date
            model.document_number = entity.document_number
            model.phone = entity.phone
            model.emergency_contact = entity.emergency_contact
            model.emergency_phone = entity.emergency_phone
            model.notes = entity.notes
            model.is_active = entity.is_active
            model.updated_at = entity.updated_at
            await self._session.flush()
            await self._session.refresh(model)
            return self._model_to_entity(model)

        raise ValueError(f"Competitor with id {entity.id} not found")

    async def delete(self, id: UUID) -> bool:
        """Delete a competitor by ID."""
        stmt = select(CompetitorModel).where(CompetitorModel.id == id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False

    async def exists(self, id: UUID) -> bool:
        """Check if competitor exists."""
        stmt = select(func.count(CompetitorModel.id)).where(CompetitorModel.id == id)
        result = await self._session.execute(stmt)
        return (result.scalar() or 0) > 0

    async def count(self, active_only: bool = False) -> int:
        """Count total number of competitors."""
        stmt = select(func.count(CompetitorModel.id))
        if active_only:
            stmt = stmt.where(CompetitorModel.is_active == True)  # noqa: E712
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Competitor]:
        """Search competitors by name."""
        search_pattern = f"%{query}%"
        stmt = (
            select(CompetitorModel)
            .where(CompetitorModel.full_name.ilike(search_pattern))
            .offset(skip)
            .limit(limit)
            .order_by(CompetitorModel.full_name)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]
