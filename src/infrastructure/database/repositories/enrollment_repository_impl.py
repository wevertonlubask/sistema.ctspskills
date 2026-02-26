"""SQLAlchemy Enrollment repository implementation."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.modality.entities.enrollment import Enrollment, EnrollmentStatus
from src.domain.modality.repositories.enrollment_repository import EnrollmentRepository
from src.infrastructure.database.models.modality_model import EnrollmentModel


class SQLAlchemyEnrollmentRepository(EnrollmentRepository):
    """SQLAlchemy implementation of EnrollmentRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _model_to_entity(self, model: EnrollmentModel) -> Enrollment:
        """Convert EnrollmentModel to Enrollment entity."""
        return Enrollment(
            id=model.id,
            competitor_id=model.competitor_id,
            modality_id=model.modality_id,
            evaluator_id=model.evaluator_id,
            enrolled_at=model.enrolled_at,
            status=EnrollmentStatus(model.status),
            notes=model.notes,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _entity_to_model(self, entity: Enrollment) -> EnrollmentModel:
        """Convert Enrollment entity to EnrollmentModel."""
        return EnrollmentModel(
            id=entity.id,
            competitor_id=entity.competitor_id,
            modality_id=entity.modality_id,
            evaluator_id=entity.evaluator_id,
            enrolled_at=entity.enrolled_at,
            status=entity.status.value,
            notes=entity.notes,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def get_by_id(self, id: UUID) -> Enrollment | None:
        """Get enrollment by ID."""
        stmt = select(EnrollmentModel).where(EnrollmentModel.id == id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def get_by_competitor_and_modality(
        self,
        competitor_id: UUID,
        modality_id: UUID,
    ) -> Enrollment | None:
        """Get enrollment by competitor and modality."""
        stmt = select(EnrollmentModel).where(
            EnrollmentModel.competitor_id == competitor_id,
            EnrollmentModel.modality_id == modality_id,
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def get_by_competitor(
        self,
        competitor_id: UUID,
        status: EnrollmentStatus | None = None,
    ) -> list[Enrollment]:
        """Get all enrollments for a competitor."""
        stmt = select(EnrollmentModel).where(EnrollmentModel.competitor_id == competitor_id)
        if status:
            stmt = stmt.where(EnrollmentModel.status == status.value)
        stmt = stmt.order_by(EnrollmentModel.enrolled_at.desc())

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    async def get_by_modality(
        self,
        modality_id: UUID,
        status: EnrollmentStatus | None = None,
    ) -> list[Enrollment]:
        """Get all enrollments for a modality."""
        stmt = select(EnrollmentModel).where(EnrollmentModel.modality_id == modality_id)
        if status:
            stmt = stmt.where(EnrollmentModel.status == status.value)
        stmt = stmt.order_by(EnrollmentModel.enrolled_at.desc())

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    async def get_by_evaluator(
        self,
        evaluator_id: UUID,
        status: EnrollmentStatus | None = None,
    ) -> list[Enrollment]:
        """Get all enrollments assigned to an evaluator."""
        stmt = select(EnrollmentModel).where(EnrollmentModel.evaluator_id == evaluator_id)
        if status:
            stmt = stmt.where(EnrollmentModel.status == status.value)
        stmt = stmt.order_by(EnrollmentModel.enrolled_at.desc())

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    async def add(self, entity: Enrollment) -> Enrollment:
        """Add a new enrollment."""
        model = self._entity_to_model(entity)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._model_to_entity(model)

    async def update(self, entity: Enrollment) -> Enrollment:
        """Update an existing enrollment."""
        stmt = select(EnrollmentModel).where(EnrollmentModel.id == entity.id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            model.evaluator_id = entity.evaluator_id
            model.status = entity.status.value
            model.notes = entity.notes
            model.updated_at = entity.updated_at
            await self._session.flush()
            await self._session.refresh(model)
            return self._model_to_entity(model)

        raise ValueError(f"Enrollment with id {entity.id} not found")

    async def delete(self, id: UUID) -> bool:
        """Delete an enrollment by ID."""
        stmt = select(EnrollmentModel).where(EnrollmentModel.id == id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False

    async def exists(self, id: UUID) -> bool:
        """Check if enrollment exists."""
        stmt = select(func.count(EnrollmentModel.id)).where(EnrollmentModel.id == id)
        result = await self._session.execute(stmt)
        return (result.scalar() or 0) > 0

    async def is_enrolled(
        self,
        competitor_id: UUID,
        modality_id: UUID,
    ) -> bool:
        """Check if competitor is enrolled in modality."""
        stmt = select(func.count(EnrollmentModel.id)).where(
            EnrollmentModel.competitor_id == competitor_id,
            EnrollmentModel.modality_id == modality_id,
        )
        result = await self._session.execute(stmt)
        return (result.scalar() or 0) > 0

    async def is_evaluator_assigned(
        self,
        evaluator_id: UUID,
        modality_id: UUID,
    ) -> bool:
        """Check if evaluator is assigned to any enrollment in modality."""
        stmt = select(func.count(EnrollmentModel.id)).where(
            EnrollmentModel.evaluator_id == evaluator_id,
            EnrollmentModel.modality_id == modality_id,
            EnrollmentModel.status == EnrollmentStatus.ACTIVE.value,
        )
        result = await self._session.execute(stmt)
        return (result.scalar() or 0) > 0

    async def get_active_enrollment(
        self,
        competitor_id: UUID,
        modality_id: UUID,
    ) -> Enrollment | None:
        """Get active enrollment for competitor in modality."""
        stmt = select(EnrollmentModel).where(
            EnrollmentModel.competitor_id == competitor_id,
            EnrollmentModel.modality_id == modality_id,
            EnrollmentModel.status == EnrollmentStatus.ACTIVE.value,
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None
