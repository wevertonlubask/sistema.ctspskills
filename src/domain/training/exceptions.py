"""Training domain exceptions."""

from src.shared.exceptions import DomainException, ErrorCode


class TrainingException(DomainException):
    """Base exception for training domain."""

    pass


class TrainingNotFoundException(TrainingException):
    """Raised when training session is not found."""

    def __init__(self, training_id: str | None = None) -> None:
        message = "Training session not found"
        if training_id:
            message = f"Training session with ID {training_id} not found"
        super().__init__(
            message=message,
            code=ErrorCode.ENTITY_NOT_FOUND,
            details={"entity_type": "TrainingSession", "training_id": training_id},
        )


class EvidenceNotFoundException(TrainingException):
    """Raised when evidence is not found."""

    def __init__(self, evidence_id: str | None = None) -> None:
        message = "Evidence not found"
        if evidence_id:
            message = f"Evidence with ID {evidence_id} not found"
        super().__init__(
            message=message,
            code=ErrorCode.ENTITY_NOT_FOUND,
            details={"entity_type": "Evidence", "evidence_id": evidence_id},
        )


class MaxDailyHoursExceededException(TrainingException):
    """Raised when daily training hours exceed the maximum (RN04)."""

    def __init__(self, date: str, current_hours: float, max_hours: float = 12.0) -> None:
        message = (
            f"Maximum daily training hours ({max_hours}h) exceeded for {date}. "
            f"Current registered hours: {current_hours}h"
        )
        super().__init__(
            message=message,
            code=ErrorCode.BUSINESS_RULE_VIOLATION,
            details={
                "rule": "RN04",
                "date": date,
                "current_hours": current_hours,
                "max_hours": max_hours,
            },
        )


class CompetitorNotEnrolledException(TrainingException):
    """Raised when competitor is not enrolled in the modality (RN01)."""

    def __init__(self, competitor_id: str, modality_id: str) -> None:
        message = (
            f"Competitor {competitor_id} is not enrolled in modality {modality_id}. "
            "Training can only be registered for enrolled modalities (RN01)."
        )
        super().__init__(
            message=message,
            code=ErrorCode.BUSINESS_RULE_VIOLATION,
            details={"rule": "RN01", "competitor_id": competitor_id, "modality_id": modality_id},
        )


class TrainingAlreadyValidatedException(TrainingException):
    """Raised when trying to modify a validated training."""

    def __init__(self) -> None:
        super().__init__(
            message="Cannot modify a training session that has already been validated",
            code=ErrorCode.BUSINESS_RULE_VIOLATION,
            details={"rule": "training_validation"},
        )


class InvalidTrainingDateException(TrainingException):
    """Raised when training date is invalid."""

    def __init__(self, reason: str) -> None:
        super().__init__(
            message=f"Invalid training date: {reason}",
            code=ErrorCode.INVALID_VALUE,
            details={"field": "training_date", "reason": reason},
        )


class InvalidEvidenceException(TrainingException):
    """Raised when evidence file is invalid."""

    def __init__(self, reason: str) -> None:
        super().__init__(
            message=f"Invalid evidence: {reason}",
            code=ErrorCode.INVALID_VALUE,
            details={"reason": reason},
        )


class EvaluatorNotAssignedException(TrainingException):
    """Raised when evaluator is not assigned to the enrollment (RN07)."""

    def __init__(self) -> None:
        super().__init__(
            message="Evaluator is not assigned to this competitor's enrollment. "
            "Only assigned evaluators can validate training (RN07).",
            code=ErrorCode.PERMISSION_DENIED,
            details={"rule": "RN07"},
        )
