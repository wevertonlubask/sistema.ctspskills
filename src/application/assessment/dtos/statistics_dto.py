"""Statistics DTOs for assessment."""

from dataclasses import dataclass
from uuid import UUID

from src.domain.assessment.services.grade_calculation_service import (
    ExamStatistics as DomainExamStatistics,
)
from src.domain.assessment.services.grade_calculation_service import (
    GradeStatistics as DomainGradeStatistics,
)


@dataclass
class GradeStatisticsDTO:
    """DTO for grade statistics."""

    average: float
    median: float
    std_deviation: float
    min_score: float
    max_score: float
    count: int

    @classmethod
    def from_domain(cls, stats: DomainGradeStatistics) -> "GradeStatisticsDTO":
        """Create DTO from domain statistics."""
        return cls(
            average=stats.average,
            median=stats.median,
            std_deviation=stats.std_deviation,
            min_score=stats.min_score,
            max_score=stats.max_score,
            count=stats.count,
        )


@dataclass
class CompetenceStatisticsDTO:
    """DTO for competence statistics within an exam."""

    competence_id: UUID
    average: float
    median: float
    std_deviation: float
    min_score: float
    max_score: float
    count: int


@dataclass
class ExamStatisticsDTO:
    """DTO for exam statistics."""

    exam_id: UUID
    total_competitors: int
    total_grades: int
    overall_average: float
    competence_stats: list[CompetenceStatisticsDTO]

    @classmethod
    def from_domain(cls, stats: DomainExamStatistics) -> "ExamStatisticsDTO":
        """Create DTO from domain statistics."""
        competence_stats = [
            CompetenceStatisticsDTO(
                competence_id=comp_id,
                average=comp_stats.average,
                median=comp_stats.median,
                std_deviation=comp_stats.std_deviation,
                min_score=comp_stats.min_score,
                max_score=comp_stats.max_score,
                count=comp_stats.count,
            )
            for comp_id, comp_stats in stats.competence_stats.items()
        ]
        return cls(
            exam_id=stats.exam_id,
            total_competitors=stats.total_competitors,
            total_grades=stats.total_grades,
            overall_average=stats.overall_average,
            competence_stats=competence_stats,
        )


@dataclass
class CompetitorAverageDTO:
    """DTO for competitor average score."""

    competitor_id: UUID
    average: float | None
    modality_id: UUID | None = None
    competence_id: UUID | None = None
    exam_id: UUID | None = None


@dataclass
class CompetitorExamSummaryDTO:
    """DTO for competitor's exam summary."""

    competitor_id: UUID
    exam_id: UUID
    grades_count: int
    average: float | None
    weighted_average: float | None
