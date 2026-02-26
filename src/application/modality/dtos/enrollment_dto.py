"""Enrollment DTOs."""

from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID

from src.domain.modality.entities.enrollment import Enrollment, EnrollmentStatus


@dataclass(frozen=True)
class EnrollmentDTO:
    """Enrollment data transfer object."""

    id: UUID
    competitor_id: UUID
    modality_id: UUID
    evaluator_id: UUID | None
    enrolled_at: date
    status: EnrollmentStatus
    notes: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, enrollment: Enrollment) -> "EnrollmentDTO":
        """Create DTO from Enrollment entity."""
        return cls(
            id=enrollment.id,
            competitor_id=enrollment.competitor_id,
            modality_id=enrollment.modality_id,
            evaluator_id=enrollment.evaluator_id,
            enrolled_at=enrollment.enrolled_at,
            status=enrollment.status,
            notes=enrollment.notes,
            created_at=enrollment.created_at,
            updated_at=enrollment.updated_at,
        )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "competitor_id": str(self.competitor_id),
            "modality_id": str(self.modality_id),
            "evaluator_id": str(self.evaluator_id) if self.evaluator_id else None,
            "enrolled_at": self.enrolled_at.isoformat(),
            "status": self.status.value,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass(frozen=True)
class EnrollCompetitorDTO:
    """DTO for enrolling a competitor in a modality."""

    competitor_id: UUID
    evaluator_id: UUID | None = None
    notes: str | None = None


@dataclass(frozen=True)
class AssignEvaluatorDTO:
    """DTO for assigning an evaluator to an enrollment."""

    evaluator_id: UUID
