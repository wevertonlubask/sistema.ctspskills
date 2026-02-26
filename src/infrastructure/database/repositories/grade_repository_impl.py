"""SQLAlchemy Grade repository implementation."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.assessment.entities.grade import Grade
from src.domain.assessment.repositories.grade_repository import GradeRepository
from src.domain.assessment.value_objects.score import Score
from src.infrastructure.database.models.assessment_model import GradeModel


class SQLAlchemyGradeRepository(GradeRepository):
    """SQLAlchemy implementation of GradeRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _model_to_entity(self, model: GradeModel) -> Grade:
        """Convert GradeModel to Grade entity."""
        return Grade(
            id=model.id,
            exam_id=model.exam_id,
            competitor_id=model.competitor_id,
            competence_id=model.competence_id,
            score=Score(model.score),
            notes=model.notes,
            created_by=model.created_by,
            updated_by=model.updated_by,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _entity_to_model(self, entity: Grade) -> GradeModel:
        """Convert Grade entity to GradeModel."""
        return GradeModel(
            id=entity.id,
            exam_id=entity.exam_id,
            competitor_id=entity.competitor_id,
            competence_id=entity.competence_id,
            score=entity.score.value,
            notes=entity.notes,
            created_by=entity.created_by,
            updated_by=entity.updated_by,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def get_by_id(self, grade_id: UUID) -> Grade | None:
        """Get grade by ID."""
        stmt = select(GradeModel).where(GradeModel.id == grade_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def add(self, grade: Grade) -> Grade:
        """Add a new grade."""
        model = self._entity_to_model(grade)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._model_to_entity(model)

    async def update(self, grade: Grade) -> Grade:
        """Update an existing grade."""
        stmt = select(GradeModel).where(GradeModel.id == grade.id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            model.score = grade.score.value
            model.notes = grade.notes
            model.updated_by = grade.updated_by
            model.updated_at = grade.updated_at
            await self._session.flush()
            await self._session.refresh(model)
            return self._model_to_entity(model)

        raise ValueError(f"Grade with id {grade.id} not found")

    async def delete(self, grade_id: UUID) -> bool:
        """Delete a grade."""
        stmt = select(GradeModel).where(GradeModel.id == grade_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False

    async def exists(self, grade_id: UUID) -> bool:
        """Check if grade exists."""
        stmt = select(func.count(GradeModel.id)).where(GradeModel.id == grade_id)
        result = await self._session.execute(stmt)
        return (result.scalar() or 0) > 0

    async def exists_for_exam_competitor_competence(
        self,
        exam_id: UUID,
        competitor_id: UUID,
        competence_id: UUID,
    ) -> bool:
        """Check if a grade exists for the given combination."""
        stmt = select(func.count(GradeModel.id)).where(
            GradeModel.exam_id == exam_id,
            GradeModel.competitor_id == competitor_id,
            GradeModel.competence_id == competence_id,
        )
        result = await self._session.execute(stmt)
        return (result.scalar() or 0) > 0

    async def get_by_exam(
        self,
        exam_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Grade]:
        """Get all grades for an exam."""
        stmt = (
            select(GradeModel)
            .where(GradeModel.exam_id == exam_id)
            .order_by(GradeModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    async def get_by_competitor(
        self,
        competitor_id: UUID,
        exam_id: UUID | None = None,
        competence_id: UUID | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Grade]:
        """Get grades for a competitor."""
        stmt = select(GradeModel).where(GradeModel.competitor_id == competitor_id)

        if exam_id:
            stmt = stmt.where(GradeModel.exam_id == exam_id)
        if competence_id:
            stmt = stmt.where(GradeModel.competence_id == competence_id)

        stmt = stmt.order_by(GradeModel.created_at.desc())
        stmt = stmt.offset(skip).limit(limit)

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    async def get_by_exam_and_competitor(
        self,
        exam_id: UUID,
        competitor_id: UUID,
    ) -> list[Grade]:
        """Get all grades for a competitor in an exam."""
        stmt = (
            select(GradeModel)
            .where(
                GradeModel.exam_id == exam_id,
                GradeModel.competitor_id == competitor_id,
            )
            .order_by(GradeModel.competence_id)
        )

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    async def get_by_exam_and_competence(
        self,
        exam_id: UUID,
        competence_id: UUID,
    ) -> list[Grade]:
        """Get all grades for a competence in an exam."""
        stmt = (
            select(GradeModel)
            .where(
                GradeModel.exam_id == exam_id,
                GradeModel.competence_id == competence_id,
            )
            .order_by(GradeModel.score.desc())
        )

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    async def get_by_competitor_and_competence(
        self,
        competitor_id: UUID,
        competence_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Grade]:
        """Get grades for a competitor on a specific competence."""
        stmt = (
            select(GradeModel)
            .where(
                GradeModel.competitor_id == competitor_id,
                GradeModel.competence_id == competence_id,
            )
            .order_by(GradeModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    async def get_scores_for_statistics(
        self,
        exam_id: UUID,
        competence_id: UUID | None = None,
    ) -> list[float]:
        """Get score values for statistics calculation."""
        stmt = select(GradeModel.score).where(GradeModel.exam_id == exam_id)

        if competence_id:
            stmt = stmt.where(GradeModel.competence_id == competence_id)

        result = await self._session.execute(stmt)
        return [row[0] for row in result.all()]

    async def count(
        self,
        exam_id: UUID | None = None,
        competitor_id: UUID | None = None,
        competence_id: UUID | None = None,
    ) -> int:
        """Count grades with optional filters."""
        stmt = select(func.count(GradeModel.id))

        if exam_id:
            stmt = stmt.where(GradeModel.exam_id == exam_id)
        if competitor_id:
            stmt = stmt.where(GradeModel.competitor_id == competitor_id)
        if competence_id:
            stmt = stmt.where(GradeModel.competence_id == competence_id)

        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def get_average_score(
        self,
        exam_id: UUID | None = None,
        competitor_id: UUID | None = None,
        competence_id: UUID | None = None,
    ) -> float | None:
        """Calculate average score with filters."""
        stmt = select(func.avg(GradeModel.score))

        if exam_id:
            stmt = stmt.where(GradeModel.exam_id == exam_id)
        if competitor_id:
            stmt = stmt.where(GradeModel.competitor_id == competitor_id)
        if competence_id:
            stmt = stmt.where(GradeModel.competence_id == competence_id)

        result = await self._session.execute(stmt)
        avg = result.scalar()
        return round(float(avg), 2) if avg is not None else None
