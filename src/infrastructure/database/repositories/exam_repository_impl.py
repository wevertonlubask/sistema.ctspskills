"""SQLAlchemy Exam repository implementation."""

from datetime import date
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.assessment.entities.exam import Exam
from src.domain.assessment.repositories.exam_repository import ExamRepository
from src.infrastructure.database.models.assessment_model import (
    ExamModel,
)
from src.infrastructure.database.models.modality_model import CompetenceModel
from src.shared.constants.enums import AssessmentType


class SQLAlchemyExamRepository(ExamRepository):
    """SQLAlchemy implementation of ExamRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _model_to_entity(self, model: ExamModel) -> Exam:
        """Convert ExamModel to Exam entity."""
        competence_ids = [c.id for c in model.competences] if model.competences else []
        return Exam(
            id=model.id,
            name=model.name,
            description=model.description,
            modality_id=model.modality_id,
            assessment_type=AssessmentType(model.assessment_type),
            exam_date=model.exam_date,
            is_active=model.is_active,
            created_by=model.created_by,
            competence_ids=competence_ids,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _entity_to_model(self, entity: Exam) -> ExamModel:
        """Convert Exam entity to ExamModel."""
        model = ExamModel(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            modality_id=entity.modality_id,
            assessment_type=entity.assessment_type.value,
            exam_date=entity.exam_date,
            is_active=entity.is_active,
            created_by=entity.created_by,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
        # Initialize competences to avoid lazy loading issues
        model.competences = []
        return model

    async def _load_competences(self, model: ExamModel, competence_ids: list[UUID]) -> None:
        """Load competences for an exam model."""
        if competence_ids:
            stmt = select(CompetenceModel).where(CompetenceModel.id.in_(competence_ids))
            result = await self._session.execute(stmt)
            competences = list(result.scalars().all())
            # Clear and extend to avoid triggering lazy load
            model.competences.clear()
            model.competences.extend(competences)
        else:
            model.competences.clear()

    async def get_by_id(self, exam_id: UUID) -> Exam | None:
        """Get exam by ID."""
        stmt = (
            select(ExamModel)
            .options(selectinload(ExamModel.competences))
            .where(ExamModel.id == exam_id)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def add(self, exam: Exam) -> Exam:
        """Add a new exam."""
        model = self._entity_to_model(exam)
        self._session.add(model)
        await self._session.flush()

        # Add competences
        await self._load_competences(model, exam.competence_ids)
        await self._session.flush()

        # Re-fetch with eager loading to avoid lazy load issues
        stmt = (
            select(ExamModel)
            .options(selectinload(ExamModel.competences))
            .where(ExamModel.id == model.id)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one()

        return self._model_to_entity(model)

    async def update(self, exam: Exam) -> Exam:
        """Update an existing exam."""
        stmt = (
            select(ExamModel)
            .options(selectinload(ExamModel.competences))
            .where(ExamModel.id == exam.id)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            model.name = exam.name
            model.description = exam.description
            model.assessment_type = exam.assessment_type.value
            model.exam_date = exam.exam_date
            model.is_active = exam.is_active
            model.updated_at = exam.updated_at

            # Update competences
            await self._load_competences(model, exam.competence_ids)

            await self._session.flush()

            # Re-fetch with eager loading to avoid lazy load issues
            stmt = (
                select(ExamModel)
                .options(selectinload(ExamModel.competences))
                .where(ExamModel.id == model.id)
            )
            result = await self._session.execute(stmt)
            model = result.scalar_one()

            return self._model_to_entity(model)

        raise ValueError(f"Exam with id {exam.id} not found")

    async def delete(self, exam_id: UUID) -> bool:
        """Delete an exam."""
        stmt = select(ExamModel).where(ExamModel.id == exam_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False

    async def exists(self, exam_id: UUID) -> bool:
        """Check if exam exists."""
        stmt = select(func.count(ExamModel.id)).where(ExamModel.id == exam_id)
        result = await self._session.execute(stmt)
        return (result.scalar() or 0) > 0

    async def get_all(
        self,
        active_only: bool = True,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Exam]:
        """Get all exams."""
        stmt = select(ExamModel).options(selectinload(ExamModel.competences))

        if active_only:
            stmt = stmt.where(ExamModel.is_active == True)  # noqa: E712

        stmt = stmt.order_by(ExamModel.exam_date.desc())
        stmt = stmt.offset(skip).limit(limit)

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    async def get_by_modality(
        self,
        modality_id: UUID,
        active_only: bool = True,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Exam]:
        """Get exams by modality."""
        stmt = (
            select(ExamModel)
            .options(selectinload(ExamModel.competences))
            .where(ExamModel.modality_id == modality_id)
        )

        if active_only:
            stmt = stmt.where(ExamModel.is_active == True)  # noqa: E712

        stmt = stmt.order_by(ExamModel.exam_date.desc())
        stmt = stmt.offset(skip).limit(limit)

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    async def get_by_date_range(
        self,
        modality_id: UUID | None,
        start_date: date,
        end_date: date,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Exam]:
        """Get exams within a date range."""
        stmt = (
            select(ExamModel)
            .options(selectinload(ExamModel.competences))
            .where(
                ExamModel.exam_date >= start_date,
                ExamModel.exam_date <= end_date,
            )
        )

        if modality_id:
            stmt = stmt.where(ExamModel.modality_id == modality_id)

        stmt = stmt.order_by(ExamModel.exam_date.desc())
        stmt = stmt.offset(skip).limit(limit)

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    async def get_by_creator(
        self,
        creator_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Exam]:
        """Get exams created by a specific user."""
        stmt = (
            select(ExamModel)
            .options(selectinload(ExamModel.competences))
            .where(ExamModel.created_by == creator_id)
            .order_by(ExamModel.exam_date.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    async def count(
        self,
        modality_id: UUID | None = None,
        active_only: bool = True,
    ) -> int:
        """Count exams with optional filters."""
        stmt = select(func.count(ExamModel.id))

        if modality_id:
            stmt = stmt.where(ExamModel.modality_id == modality_id)
        if active_only:
            stmt = stmt.where(ExamModel.is_active == True)  # noqa: E712

        result = await self._session.execute(stmt)
        return result.scalar() or 0
