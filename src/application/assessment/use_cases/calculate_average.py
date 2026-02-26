"""Calculate average use case."""

from uuid import UUID

from src.application.assessment.dtos.statistics_dto import (
    CompetitorAverageDTO,
    CompetitorExamSummaryDTO,
)
from src.domain.assessment.exceptions import ExamNotFoundException
from src.domain.assessment.repositories.exam_repository import ExamRepository
from src.domain.assessment.repositories.grade_repository import GradeRepository
from src.domain.modality.exceptions import CompetitorNotFoundException
from src.domain.modality.repositories.competitor_repository import CompetitorRepository


class CalculateAverageUseCase:
    """Use case for calculating averages.

    This use case calculates various averages for competitors.
    """

    def __init__(
        self,
        grade_repository: GradeRepository,
        exam_repository: ExamRepository,
        competitor_repository: CompetitorRepository,
    ) -> None:
        self._grade_repository = grade_repository
        self._exam_repository = exam_repository
        self._competitor_repository = competitor_repository

    async def competitor_average(
        self,
        competitor_id: UUID,
        modality_id: UUID | None = None,
        competence_id: UUID | None = None,
    ) -> CompetitorAverageDTO:
        """Calculate average for a competitor.

        Args:
            competitor_id: ID of the competitor.
            modality_id: Optional modality filter.
            competence_id: Optional competence filter.

        Returns:
            CompetitorAverageDTO with the average.

        Raises:
            CompetitorNotFoundException: If competitor not found.
        """
        # Validate competitor exists
        competitor = await self._competitor_repository.get_by_id(competitor_id)
        if not competitor:
            raise CompetitorNotFoundException(str(competitor_id))

        # Calculate average
        average = await self._grade_repository.get_average_score(
            competitor_id=competitor_id,
            competence_id=competence_id,
        )

        return CompetitorAverageDTO(
            competitor_id=competitor_id,
            average=average,
            modality_id=modality_id,
            competence_id=competence_id,
        )

    async def exam_competitor_summary(
        self,
        competitor_id: UUID,
        exam_id: UUID,
        competence_weights: dict[UUID, float] | None = None,
    ) -> CompetitorExamSummaryDTO:
        """Get competitor's summary for an exam.

        Args:
            competitor_id: ID of the competitor.
            exam_id: ID of the exam.
            competence_weights: Optional weights for weighted average.

        Returns:
            CompetitorExamSummaryDTO with the summary.

        Raises:
            CompetitorNotFoundException: If competitor not found.
            ExamNotFoundException: If exam not found.
        """
        # Validate competitor exists
        competitor = await self._competitor_repository.get_by_id(competitor_id)
        if not competitor:
            raise CompetitorNotFoundException(str(competitor_id))

        # Validate exam exists
        exam = await self._exam_repository.get_by_id(exam_id)
        if not exam:
            raise ExamNotFoundException(str(exam_id))

        # Get grades for this competitor in this exam
        grades = await self._grade_repository.get_by_exam_and_competitor(
            exam_id=exam_id,
            competitor_id=competitor_id,
        )

        if not grades:
            return CompetitorExamSummaryDTO(
                competitor_id=competitor_id,
                exam_id=exam_id,
                grades_count=0,
                average=None,
                weighted_average=None,
            )

        # Calculate simple average
        scores = [g.score.value for g in grades]
        average = round(sum(scores) / len(scores), 2)

        # Calculate weighted average if weights provided
        weighted_average = None
        if competence_weights:
            total_weight = 0.0
            weighted_sum = 0.0
            for grade in grades:
                weight = competence_weights.get(grade.competence_id, 1.0)
                weighted_sum += grade.score.value * weight
                total_weight += weight
            if total_weight > 0:
                weighted_average = round(weighted_sum / total_weight, 2)

        return CompetitorExamSummaryDTO(
            competitor_id=competitor_id,
            exam_id=exam_id,
            grades_count=len(grades),
            average=average,
            weighted_average=weighted_average,
        )
