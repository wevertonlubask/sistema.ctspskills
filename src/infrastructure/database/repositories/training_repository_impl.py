"""SQLAlchemy Training repository implementation."""

from datetime import date
from uuid import UUID

from sqlalchemy import and_, func, inspect, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.training.entities.evidence import Evidence, EvidenceType
from src.domain.training.entities.training_session import TrainingSession
from src.domain.training.repositories.training_repository import TrainingRepository
from src.domain.training.value_objects.training_hours import TrainingHours
from src.infrastructure.database.models.modality_model import EnrollmentModel
from src.infrastructure.database.models.training_model import (
    EvidenceModel,
    TrainingSessionModel,
)
from src.shared.constants.enums import TrainingStatus, TrainingType


class SQLAlchemyTrainingRepository(TrainingRepository):
    """SQLAlchemy implementation of TrainingRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _evidence_model_to_entity(self, model: EvidenceModel) -> Evidence:
        """Convert EvidenceModel to Evidence entity."""
        return Evidence(
            id=model.id,
            training_session_id=model.training_session_id,
            file_name=model.file_name,
            file_path=model.file_path,
            file_size=model.file_size,
            mime_type=model.mime_type,
            evidence_type=EvidenceType(model.evidence_type),
            description=model.description,
            uploaded_by=model.uploaded_by,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _model_to_entity(self, model: TrainingSessionModel) -> TrainingSession:
        """Convert TrainingSessionModel to TrainingSession entity."""
        training = TrainingSession(
            id=model.id,
            competitor_id=model.competitor_id,
            modality_id=model.modality_id,
            enrollment_id=model.enrollment_id,
            training_date=model.training_date,
            hours=TrainingHours.create_total(model.hours),
            training_type=TrainingType(model.training_type),
            location=model.location,
            description=model.description,
            status=TrainingStatus(model.status),
            validated_by=model.validated_by,
            validated_at=model.validated_at,
            rejection_reason=model.rejection_reason,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
        # Load evidences only if the relationship is loaded (avoid lazy loading in async)
        state = inspect(model)
        if "evidences" in state.dict and model.evidences:
            for evidence_model in model.evidences:
                training._evidences.append(self._evidence_model_to_entity(evidence_model))
        return training

    def _entity_to_model(self, entity: TrainingSession) -> TrainingSessionModel:
        """Convert TrainingSession entity to TrainingSessionModel."""
        return TrainingSessionModel(
            id=entity.id,
            competitor_id=entity.competitor_id,
            modality_id=entity.modality_id,
            enrollment_id=entity.enrollment_id,
            training_date=entity.training_date,
            hours=entity.hours.value,
            training_type=entity.training_type.value,
            location=entity.location,
            description=entity.description,
            status=entity.status.value,
            validated_by=entity.validated_by,
            validated_at=entity.validated_at,
            rejection_reason=entity.rejection_reason,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def create(self, training: TrainingSession) -> TrainingSession:
        """Create a new training session."""
        model = self._entity_to_model(training)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._model_to_entity(model)

    async def get_by_id(self, training_id: UUID) -> TrainingSession | None:
        """Get training session by ID."""
        stmt = (
            select(TrainingSessionModel)
            .options(selectinload(TrainingSessionModel.evidences))
            .where(TrainingSessionModel.id == training_id)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def update(self, training: TrainingSession) -> TrainingSession:
        """Update a training session."""
        stmt = select(TrainingSessionModel).where(TrainingSessionModel.id == training.id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            model.training_date = training.training_date
            model.hours = training.hours.value
            model.training_type = training.training_type.value
            model.location = training.location
            model.description = training.description
            model.status = training.status.value
            model.validated_by = training.validated_by
            model.validated_at = training.validated_at
            model.rejection_reason = training.rejection_reason
            model.updated_at = training.updated_at
            await self._session.flush()
            await self._session.refresh(model)
            return self._model_to_entity(model)

        raise ValueError(f"Training session with id {training.id} not found")

    async def delete(self, training_id: UUID) -> bool:
        """Delete a training session."""
        stmt = select(TrainingSessionModel).where(TrainingSessionModel.id == training_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False

    async def get_by_competitor(
        self,
        competitor_id: UUID,
        skip: int = 0,
        limit: int = 100,
        status: TrainingStatus | None = None,
        modality_id: UUID | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[TrainingSession]:
        """Get training sessions by competitor."""
        stmt = (
            select(TrainingSessionModel)
            .options(selectinload(TrainingSessionModel.evidences))
            .where(TrainingSessionModel.competitor_id == competitor_id)
        )

        if status:
            stmt = stmt.where(TrainingSessionModel.status == status.value)
        if modality_id:
            stmt = stmt.where(TrainingSessionModel.modality_id == modality_id)
        if start_date:
            stmt = stmt.where(TrainingSessionModel.training_date >= start_date)
        if end_date:
            stmt = stmt.where(TrainingSessionModel.training_date <= end_date)

        stmt = stmt.order_by(TrainingSessionModel.training_date.desc())
        stmt = stmt.offset(skip).limit(limit)

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    async def get_by_modality(
        self,
        modality_id: UUID,
        skip: int = 0,
        limit: int = 100,
        status: TrainingStatus | None = None,
    ) -> list[TrainingSession]:
        """Get training sessions by modality."""
        stmt = (
            select(TrainingSessionModel)
            .options(selectinload(TrainingSessionModel.evidences))
            .where(TrainingSessionModel.modality_id == modality_id)
        )

        if status:
            stmt = stmt.where(TrainingSessionModel.status == status.value)

        stmt = stmt.order_by(TrainingSessionModel.training_date.desc())
        stmt = stmt.offset(skip).limit(limit)

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    async def get_by_evaluator(
        self,
        evaluator_id: UUID,
        skip: int = 0,
        limit: int = 100,
        status: TrainingStatus | None = None,
    ) -> list[TrainingSession]:
        """Get training sessions pending validation by an evaluator."""
        # Get training sessions for competitors assigned to this evaluator
        stmt = (
            select(TrainingSessionModel)
            .options(selectinload(TrainingSessionModel.evidences))
            .join(
                EnrollmentModel,
                and_(
                    EnrollmentModel.id == TrainingSessionModel.enrollment_id,
                    EnrollmentModel.evaluator_id == evaluator_id,
                ),
            )
        )

        if status:
            stmt = stmt.where(TrainingSessionModel.status == status.value)

        stmt = stmt.order_by(TrainingSessionModel.training_date.desc())
        stmt = stmt.offset(skip).limit(limit)

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    async def get_daily_hours(
        self,
        competitor_id: UUID,
        training_date: date,
        exclude_training_id: UUID | None = None,
    ) -> float:
        """Get total training hours for a competitor on a specific date."""
        stmt = select(func.coalesce(func.sum(TrainingSessionModel.hours), 0.0)).where(
            TrainingSessionModel.competitor_id == competitor_id,
            TrainingSessionModel.training_date == training_date,
            TrainingSessionModel.status != TrainingStatus.REJECTED.value,
        )

        if exclude_training_id:
            stmt = stmt.where(TrainingSessionModel.id != exclude_training_id)

        result = await self._session.execute(stmt)
        return float(result.scalar() or 0.0)

    async def get_total_hours(
        self,
        competitor_id: UUID,
        modality_id: UUID | None = None,
        training_type: TrainingType | None = None,
        approved_only: bool = True,
    ) -> float:
        """Get total training hours for a competitor."""
        stmt = select(func.coalesce(func.sum(TrainingSessionModel.hours), 0.0)).where(
            TrainingSessionModel.competitor_id == competitor_id,
        )

        if modality_id:
            stmt = stmt.where(TrainingSessionModel.modality_id == modality_id)
        if training_type:
            stmt = stmt.where(TrainingSessionModel.training_type == training_type.value)
        if approved_only:
            stmt = stmt.where(TrainingSessionModel.status == TrainingStatus.APPROVED.value)

        result = await self._session.execute(stmt)
        return float(result.scalar() or 0.0)

    async def get_pending_count(
        self,
        evaluator_id: UUID | None = None,
        modality_id: UUID | None = None,
    ) -> int:
        """Get count of pending trainings."""
        stmt = select(func.count(TrainingSessionModel.id)).where(
            TrainingSessionModel.status == TrainingStatus.PENDING.value
        )

        if evaluator_id:
            stmt = stmt.join(
                EnrollmentModel,
                and_(
                    EnrollmentModel.id == TrainingSessionModel.enrollment_id,
                    EnrollmentModel.evaluator_id == evaluator_id,
                ),
            )
        if modality_id:
            stmt = stmt.where(TrainingSessionModel.modality_id == modality_id)

        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def count(
        self,
        competitor_id: UUID | None = None,
        modality_id: UUID | None = None,
        status: TrainingStatus | None = None,
    ) -> int:
        """Count training sessions with filters."""
        stmt = select(func.count(TrainingSessionModel.id))

        if competitor_id:
            stmt = stmt.where(TrainingSessionModel.competitor_id == competitor_id)
        if modality_id:
            stmt = stmt.where(TrainingSessionModel.modality_id == modality_id)
        if status:
            stmt = stmt.where(TrainingSessionModel.status == status.value)

        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: TrainingStatus | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[TrainingSession]:
        """Get all training sessions with optional filters."""
        stmt = select(TrainingSessionModel).options(selectinload(TrainingSessionModel.evidences))

        if status:
            stmt = stmt.where(TrainingSessionModel.status == status.value)
        if start_date:
            stmt = stmt.where(TrainingSessionModel.training_date >= start_date)
        if end_date:
            stmt = stmt.where(TrainingSessionModel.training_date <= end_date)

        stmt = stmt.order_by(TrainingSessionModel.training_date.desc())
        stmt = stmt.offset(skip).limit(limit)

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    async def count_all(
        self,
        status: TrainingStatus | None = None,
    ) -> int:
        """Count all training sessions."""
        stmt = select(func.count(TrainingSessionModel.id))

        if status:
            stmt = stmt.where(TrainingSessionModel.status == status.value)

        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[TrainingSession]:
        """Search training sessions."""
        search_pattern = f"%{query}%"
        stmt = (
            select(TrainingSessionModel)
            .options(selectinload(TrainingSessionModel.evidences))
            .where(
                or_(
                    TrainingSessionModel.description.ilike(search_pattern),
                    TrainingSessionModel.location.ilike(search_pattern),
                )
            )
            .order_by(TrainingSessionModel.training_date.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]
