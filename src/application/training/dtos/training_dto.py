"""Training DTOs."""

from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID

from src.application.training.dtos.evidence_dto import EvidenceDTO
from src.domain.training.entities.training_session import TrainingSession
from src.shared.constants.enums import TrainingStatus, TrainingType


@dataclass
class RegisterTrainingDTO:
    """DTO for registering a training session."""

    modality_id: UUID
    training_date: date
    hours: float
    training_type: TrainingType = TrainingType.SENAI
    location: str | None = None
    description: str | None = None


@dataclass
class ValidateTrainingDTO:
    """DTO for validating a training session."""

    approved: bool
    rejection_reason: str | None = None


@dataclass
class TrainingDTO:
    """DTO for training session data."""

    id: UUID
    competitor_id: UUID
    modality_id: UUID
    enrollment_id: UUID
    training_date: date
    hours: float
    training_type: TrainingType
    location: str | None
    description: str | None
    status: TrainingStatus
    validated_by: UUID | None
    validated_at: datetime | None
    rejection_reason: str | None
    evidences: list[EvidenceDTO]
    created_at: datetime
    updated_at: datetime
    competitor_name: str | None = None
    modality_name: str | None = None

    @classmethod
    def from_entity(
        cls,
        entity: TrainingSession,
        competitor_name: str | None = None,
        modality_name: str | None = None,
    ) -> "TrainingDTO":
        """Create DTO from entity."""
        return cls(
            id=entity.id,
            competitor_id=entity.competitor_id,
            modality_id=entity.modality_id,
            enrollment_id=entity.enrollment_id,
            training_date=entity.training_date,
            hours=entity.hours.value,
            training_type=entity.training_type,
            location=entity.location,
            description=entity.description,
            status=entity.status,
            validated_by=entity.validated_by,
            validated_at=entity.validated_at,
            rejection_reason=entity.rejection_reason,
            evidences=[EvidenceDTO.from_entity(e) for e in entity.evidences],
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            competitor_name=competitor_name,
            modality_name=modality_name,
        )


@dataclass
class TrainingListDTO:
    """DTO for paginated list of trainings."""

    trainings: list[TrainingDTO]
    total: int
    skip: int
    limit: int

    @property
    def has_more(self) -> bool:
        """Check if there are more results."""
        return self.skip + len(self.trainings) < self.total


@dataclass
class TrainingStatisticsDTO:
    """DTO for training statistics."""

    competitor_id: UUID
    modality_id: UUID | None = None
    senai_hours: float = 0.0
    external_hours: float = 0.0
    total_approved_hours: float = 0.0
    total_sessions: int = 0
    pending_sessions: int = 0
    approved_sessions: int = 0
    rejected_sessions: int = 0
