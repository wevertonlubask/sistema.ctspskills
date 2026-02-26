"""Assessment domain exceptions."""

from src.shared.exceptions import DomainException, ErrorCode


class AssessmentException(DomainException):
    """Base exception for assessment domain."""

    pass


class ExamNotFoundException(AssessmentException):
    """Raised when exam is not found."""

    def __init__(self, exam_id: str | None = None) -> None:
        message = "Exam not found"
        if exam_id:
            message = f"Exam with ID {exam_id} not found"
        super().__init__(
            message=message,
            code=ErrorCode.ENTITY_NOT_FOUND,
            details={"entity_type": "Exam", "exam_id": exam_id},
        )


class GradeNotFoundException(AssessmentException):
    """Raised when grade is not found."""

    def __init__(self, grade_id: str | None = None) -> None:
        message = "Grade not found"
        if grade_id:
            message = f"Grade with ID {grade_id} not found"
        super().__init__(
            message=message,
            code=ErrorCode.ENTITY_NOT_FOUND,
            details={"entity_type": "Grade", "grade_id": grade_id},
        )


class GradeAlreadyExistsException(AssessmentException):
    """Raised when trying to create a duplicate grade."""

    def __init__(
        self,
        exam_id: str,
        competitor_id: str,
        competence_id: str,
    ) -> None:
        message = (
            f"Grade already exists for exam {exam_id}, "
            f"competitor {competitor_id}, competence {competence_id}"
        )
        super().__init__(
            message=message,
            code=ErrorCode.RESOURCE_ALREADY_EXISTS,
            details={
                "entity_type": "Grade",
                "exam_id": exam_id,
                "competitor_id": competitor_id,
                "competence_id": competence_id,
            },
        )


class InvalidScoreException(AssessmentException):
    """Raised when score is invalid (RN03)."""

    def __init__(
        self,
        score: float,
        min_score: float = 0.0,
        max_score: float = 100.0,
    ) -> None:
        message = f"Score {score} is invalid. Must be between {min_score} and {max_score} (RN03)"
        super().__init__(
            message=message,
            code=ErrorCode.BUSINESS_RULE_VIOLATION,
            details={
                "rule": "RN03",
                "score": score,
                "min_score": min_score,
                "max_score": max_score,
            },
        )


class CompetenceNotInExamException(AssessmentException):
    """Raised when competence is not part of the exam (RN08)."""

    def __init__(self, competence_id: str, exam_id: str) -> None:
        message = (
            f"Competence {competence_id} is not part of exam {exam_id}. "
            "Grades can only be given for competences included in the exam (RN08)."
        )
        super().__init__(
            message=message,
            code=ErrorCode.BUSINESS_RULE_VIOLATION,
            details={
                "rule": "RN08",
                "competence_id": competence_id,
                "exam_id": exam_id,
            },
        )


class EvaluatorCannotGradeException(AssessmentException):
    """Raised when evaluator doesn't have permission to grade (RN02)."""

    def __init__(self, evaluator_id: str, competitor_id: str) -> None:
        message = (
            f"Evaluator {evaluator_id} is not authorized to grade competitor {competitor_id}. "
            "Evaluator must be assigned to the competitor's modality (RN02)."
        )
        super().__init__(
            message=message,
            code=ErrorCode.PERMISSION_DENIED,
            details={
                "rule": "RN02",
                "evaluator_id": evaluator_id,
                "competitor_id": competitor_id,
            },
        )


class InsufficientGradesForStatisticsException(AssessmentException):
    """Raised when there are not enough grades for statistics calculation."""

    def __init__(self, min_required: int, actual: int) -> None:
        message = (
            f"Insufficient grades for statistics calculation. "
            f"Requires at least {min_required}, but only {actual} available."
        )
        super().__init__(
            message=message,
            code=ErrorCode.BUSINESS_RULE_VIOLATION,
            details={
                "min_required": min_required,
                "actual": actual,
            },
        )


class ExamNotActiveException(AssessmentException):
    """Raised when trying to grade on an inactive exam."""

    def __init__(self, exam_id: str) -> None:
        message = f"Exam {exam_id} is not active. Cannot register grades on inactive exams."
        super().__init__(
            message=message,
            code=ErrorCode.BUSINESS_RULE_VIOLATION,
            details={"exam_id": exam_id},
        )


class CompetitorNotInModalityException(AssessmentException):
    """Raised when competitor is not enrolled in the exam's modality."""

    def __init__(self, competitor_id: str, modality_id: str) -> None:
        message = (
            f"Competitor {competitor_id} is not enrolled in modality {modality_id}. "
            "Grades can only be given to enrolled competitors."
        )
        super().__init__(
            message=message,
            code=ErrorCode.BUSINESS_RULE_VIOLATION,
            details={
                "competitor_id": competitor_id,
                "modality_id": modality_id,
            },
        )
