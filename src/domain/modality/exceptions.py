"""Modality domain exceptions."""

from uuid import UUID

from src.shared.exceptions import DomainException, ErrorCode


class ModalityNotFoundException(DomainException):
    """Raised when a modality is not found."""

    def __init__(self, identifier: str, field: str = "id") -> None:
        super().__init__(
            message=f"Modality with {field} '{identifier}' not found",
            code=ErrorCode.ENTITY_NOT_FOUND,
            details={field: identifier},
        )


class ModalityCodeAlreadyExistsException(DomainException):
    """Raised when trying to create a modality with an existing code."""

    def __init__(self, code: str) -> None:
        super().__init__(
            message=f"Modality with code '{code}' already exists",
            code=ErrorCode.RESOURCE_ALREADY_EXISTS,
            details={"code": code},
        )


class CompetitorNotFoundException(DomainException):
    """Raised when a competitor is not found."""

    def __init__(self, identifier: str, field: str = "id") -> None:
        super().__init__(
            message=f"Competitor with {field} '{identifier}' not found",
            code=ErrorCode.ENTITY_NOT_FOUND,
            details={field: identifier},
        )


class CompetitorAlreadyEnrolledException(DomainException):
    """Raised when a competitor is already enrolled in a modality."""

    def __init__(self, competitor_id: UUID, modality_id: UUID) -> None:
        super().__init__(
            message="Competitor is already enrolled in this modality",
            code=ErrorCode.RESOURCE_CONFLICT,
            details={
                "competitor_id": str(competitor_id),
                "modality_id": str(modality_id),
            },
        )


class CompetitorNotEnrolledException(DomainException):
    """Raised when a competitor is not enrolled in a modality (RN01)."""

    def __init__(self, competitor_id: UUID, modality_id: UUID) -> None:
        super().__init__(
            message="Competitor is not enrolled in this modality",
            code=ErrorCode.BUSINESS_RULE_VIOLATION,
            details={
                "competitor_id": str(competitor_id),
                "modality_id": str(modality_id),
                "rule": "RN01",
            },
        )


class EvaluatorNotAssignedException(DomainException):
    """Raised when evaluator is not assigned to a modality (RN02)."""

    def __init__(self, evaluator_id: UUID, modality_id: UUID) -> None:
        super().__init__(
            message="Evaluator is not assigned to this modality",
            code=ErrorCode.BUSINESS_RULE_VIOLATION,
            details={
                "evaluator_id": str(evaluator_id),
                "modality_id": str(modality_id),
                "rule": "RN02",
            },
        )


class CompetenceNotFoundException(DomainException):
    """Raised when a competence is not found."""

    def __init__(self, identifier: str, field: str = "id") -> None:
        super().__init__(
            message=f"Competence with {field} '{identifier}' not found",
            code=ErrorCode.ENTITY_NOT_FOUND,
            details={field: identifier},
        )


class EnrollmentNotFoundException(DomainException):
    """Raised when an enrollment is not found."""

    def __init__(self, identifier: str | None = None) -> None:
        super().__init__(
            message="Enrollment not found",
            code=ErrorCode.ENTITY_NOT_FOUND,
            details={"identifier": identifier} if identifier else {},
        )
