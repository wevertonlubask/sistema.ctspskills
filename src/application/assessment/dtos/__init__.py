"""Assessment DTOs."""

from src.application.assessment.dtos.exam_dto import (
    CreateExamDTO,
    ExamDTO,
    ExamListDTO,
    UpdateExamDTO,
)
from src.application.assessment.dtos.grade_dto import (
    GradeAuditDTO,
    GradeDTO,
    GradeHistoryDTO,
    GradeListDTO,
    RegisterGradeDTO,
    UpdateGradeDTO,
)
from src.application.assessment.dtos.statistics_dto import (
    CompetenceStatisticsDTO,
    CompetitorAverageDTO,
    CompetitorExamSummaryDTO,
    ExamStatisticsDTO,
    GradeStatisticsDTO,
)

__all__ = [
    "ExamDTO",
    "CreateExamDTO",
    "UpdateExamDTO",
    "ExamListDTO",
    "GradeDTO",
    "GradeAuditDTO",
    "RegisterGradeDTO",
    "UpdateGradeDTO",
    "GradeListDTO",
    "GradeHistoryDTO",
    "GradeStatisticsDTO",
    "CompetenceStatisticsDTO",
    "ExamStatisticsDTO",
    "CompetitorAverageDTO",
    "CompetitorExamSummaryDTO",
]
