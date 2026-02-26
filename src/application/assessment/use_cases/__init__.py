"""Assessment use cases."""

from src.application.assessment.use_cases.calculate_average import CalculateAverageUseCase
from src.application.assessment.use_cases.create_exam import CreateExamUseCase
from src.application.assessment.use_cases.get_competitor_grades import GetCompetitorGradesUseCase
from src.application.assessment.use_cases.get_exam import GetExamUseCase
from src.application.assessment.use_cases.get_exam_statistics import GetExamStatisticsUseCase
from src.application.assessment.use_cases.get_grade_history import GetGradeHistoryUseCase
from src.application.assessment.use_cases.list_exams import ListExamsUseCase
from src.application.assessment.use_cases.register_grade import RegisterGradeUseCase
from src.application.assessment.use_cases.update_exam import UpdateExamUseCase
from src.application.assessment.use_cases.update_grade import UpdateGradeUseCase

__all__ = [
    "CreateExamUseCase",
    "UpdateExamUseCase",
    "ListExamsUseCase",
    "GetExamUseCase",
    "RegisterGradeUseCase",
    "UpdateGradeUseCase",
    "GetCompetitorGradesUseCase",
    "CalculateAverageUseCase",
    "GetGradeHistoryUseCase",
    "GetExamStatisticsUseCase",
]
