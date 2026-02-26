"""Get exam statistics use case."""

from uuid import UUID

from src.application.assessment.dtos.statistics_dto import (
    ExamStatisticsDTO,
    GradeStatisticsDTO,
)
from src.domain.assessment.exceptions import ExamNotFoundException
from src.domain.assessment.repositories.exam_repository import ExamRepository
from src.domain.assessment.repositories.grade_repository import GradeRepository
from src.domain.assessment.services.grade_calculation_service import GradeCalculationService


class GetExamStatisticsUseCase:
    """Use case for getting exam statistics.

    This use case calculates comprehensive statistics for an exam.
    """

    def __init__(
        self,
        exam_repository: ExamRepository,
        grade_repository: GradeRepository,
    ) -> None:
        self._exam_repository = exam_repository
        self._grade_repository = grade_repository
        self._calculation_service = GradeCalculationService(
            grade_repository=grade_repository,
            exam_repository=exam_repository,
        )

    async def execute(
        self,
        exam_id: UUID,
    ) -> ExamStatisticsDTO:
        """Get statistics for an exam.

        Args:
            exam_id: ID of the exam.

        Returns:
            ExamStatisticsDTO with comprehensive statistics.

        Raises:
            ExamNotFoundException: If exam not found.
        """
        # Validate exam exists
        exam = await self._exam_repository.get_by_id(exam_id)
        if not exam:
            raise ExamNotFoundException(str(exam_id))

        # Calculate statistics using domain service
        stats = await self._calculation_service.calculate_exam_statistics(exam_id)

        return ExamStatisticsDTO.from_domain(stats)

    async def competence_statistics(
        self,
        exam_id: UUID,
        competence_id: UUID,
    ) -> GradeStatisticsDTO:
        """Get statistics for a specific competence in an exam.

        Args:
            exam_id: ID of the exam.
            competence_id: ID of the competence.

        Returns:
            GradeStatisticsDTO with competence statistics.

        Raises:
            ExamNotFoundException: If exam not found.
            InsufficientGradesForStatisticsException: If not enough grades.
        """
        # Validate exam exists
        exam = await self._exam_repository.get_by_id(exam_id)
        if not exam:
            raise ExamNotFoundException(str(exam_id))

        # Calculate statistics using domain service
        stats = await self._calculation_service.calculate_competence_statistics(
            exam_id=exam_id,
            competence_id=competence_id,
        )

        return GradeStatisticsDTO.from_domain(stats)
