"""Grade calculation service for statistics."""

import statistics
from dataclasses import dataclass
from uuid import UUID

from src.domain.assessment.exceptions import (
    ExamNotFoundException,
    InsufficientGradesForStatisticsException,
)
from src.domain.assessment.repositories.exam_repository import ExamRepository
from src.domain.assessment.repositories.grade_repository import GradeRepository


@dataclass(frozen=True)
class GradeStatistics:
    """Statistics for a set of grades."""

    average: float
    median: float
    std_deviation: float
    min_score: float
    max_score: float
    count: int

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "average": self.average,
            "median": self.median,
            "std_deviation": self.std_deviation,
            "min_score": self.min_score,
            "max_score": self.max_score,
            "count": self.count,
        }


@dataclass(frozen=True)
class ExamStatistics:
    """Statistics for an entire exam."""

    exam_id: UUID
    total_competitors: int
    total_grades: int
    overall_average: float
    competence_stats: dict[UUID, GradeStatistics]

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "exam_id": str(self.exam_id),
            "total_competitors": self.total_competitors,
            "total_grades": self.total_grades,
            "overall_average": self.overall_average,
            "competence_stats": {str(k): v.to_dict() for k, v in self.competence_stats.items()},
        }


class GradeCalculationService:
    """Domain service for grade statistics calculation.

    Provides methods to calculate averages, medians, standard deviations,
    and other statistics for grades across various dimensions.
    """

    MIN_GRADES_FOR_STATS = 1  # Minimum grades needed for statistics

    def __init__(
        self,
        grade_repository: GradeRepository,
        exam_repository: ExamRepository,
    ) -> None:
        """Initialize the service.

        Args:
            grade_repository: Grade repository instance.
            exam_repository: Exam repository instance.
        """
        self._grade_repository = grade_repository
        self._exam_repository = exam_repository

    def _calculate_statistics(self, scores: list[float]) -> GradeStatistics:
        """Calculate statistics from a list of scores.

        Args:
            scores: List of score values.

        Returns:
            GradeStatistics instance.

        Raises:
            InsufficientGradesForStatisticsException: If not enough grades.
        """
        if len(scores) < self.MIN_GRADES_FOR_STATS:
            raise InsufficientGradesForStatisticsException(
                min_required=self.MIN_GRADES_FOR_STATS,
                actual=len(scores),
            )

        avg = round(statistics.mean(scores), 2)
        med = round(statistics.median(scores), 2)

        # Standard deviation requires at least 2 values
        if len(scores) >= 2:
            std = round(statistics.stdev(scores), 2)
        else:
            std = 0.0

        return GradeStatistics(
            average=avg,
            median=med,
            std_deviation=std,
            min_score=min(scores),
            max_score=max(scores),
            count=len(scores),
        )

    async def calculate_exam_average(
        self,
        exam_id: UUID,
        competitor_id: UUID | None = None,
    ) -> float | None:
        """Calculate average score for an exam.

        Args:
            exam_id: Exam UUID.
            competitor_id: Optional competitor filter.

        Returns:
            Average score or None if no grades.
        """
        return await self._grade_repository.get_average_score(
            exam_id=exam_id,
            competitor_id=competitor_id,
        )

    async def calculate_competitor_average(
        self,
        competitor_id: UUID,
        modality_id: UUID | None = None,
        competence_id: UUID | None = None,
    ) -> float | None:
        """Calculate average score for a competitor.

        Args:
            competitor_id: Competitor UUID.
            modality_id: Optional modality filter (filters exams).
            competence_id: Optional competence filter.

        Returns:
            Average score or None if no grades.
        """
        # For modality filtering, we'd need to join with exams
        # For now, just use competence filter
        return await self._grade_repository.get_average_score(
            competitor_id=competitor_id,
            competence_id=competence_id,
        )

    async def calculate_competence_statistics(
        self,
        exam_id: UUID,
        competence_id: UUID,
    ) -> GradeStatistics:
        """Calculate statistics for a competence in an exam.

        Args:
            exam_id: Exam UUID.
            competence_id: Competence UUID.

        Returns:
            GradeStatistics for the competence.

        Raises:
            InsufficientGradesForStatisticsException: If not enough grades.
        """
        scores = await self._grade_repository.get_scores_for_statistics(
            exam_id=exam_id,
            competence_id=competence_id,
        )
        return self._calculate_statistics(scores)

    async def calculate_exam_statistics(
        self,
        exam_id: UUID,
    ) -> ExamStatistics:
        """Calculate comprehensive statistics for an exam.

        Args:
            exam_id: Exam UUID.

        Returns:
            ExamStatistics with overall and per-competence statistics.

        Raises:
            ExamNotFoundException: If exam not found.
        """
        exam = await self._exam_repository.get_by_id(exam_id)
        if not exam:
            raise ExamNotFoundException(str(exam_id))

        # Get all scores for the exam
        all_scores = await self._grade_repository.get_scores_for_statistics(
            exam_id=exam_id,
        )

        # Calculate overall average
        overall_avg = round(statistics.mean(all_scores), 2) if all_scores else 0.0

        # Count unique competitors
        grades = await self._grade_repository.get_by_exam(exam_id)
        competitor_ids = {g.competitor_id for g in grades}

        # Calculate per-competence statistics
        competence_stats: dict[UUID, GradeStatistics] = {}
        for competence_id in exam.competence_ids:
            try:
                stats = await self.calculate_competence_statistics(
                    exam_id=exam_id,
                    competence_id=competence_id,
                )
                competence_stats[competence_id] = stats
            except InsufficientGradesForStatisticsException:
                # No grades for this competence yet
                pass

        return ExamStatistics(
            exam_id=exam_id,
            total_competitors=len(competitor_ids),
            total_grades=len(all_scores),
            overall_average=overall_avg,
            competence_stats=competence_stats,
        )

    async def calculate_weighted_average(
        self,
        competitor_id: UUID,
        exam_id: UUID,
        competence_weights: dict[UUID, float],
    ) -> float | None:
        """Calculate weighted average for a competitor in an exam.

        Args:
            competitor_id: Competitor UUID.
            exam_id: Exam UUID.
            competence_weights: Dictionary mapping competence_id to weight.

        Returns:
            Weighted average or None if no grades.
        """
        grades = await self._grade_repository.get_by_exam_and_competitor(
            exam_id=exam_id,
            competitor_id=competitor_id,
        )

        if not grades:
            return None

        total_weight = 0.0
        weighted_sum = 0.0

        for grade in grades:
            weight = competence_weights.get(grade.competence_id, 1.0)
            weighted_sum += grade.score.value * weight
            total_weight += weight

        if total_weight == 0:
            return None

        return round(weighted_sum / total_weight, 2)
