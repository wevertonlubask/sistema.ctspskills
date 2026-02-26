"""Enrollment entity - represents competitor enrollment in a modality."""

from datetime import date, datetime
from enum import Enum
from uuid import UUID

from src.shared.domain.entity import Entity


class EnrollmentStatus(str, Enum):
    """Enrollment status."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    COMPLETED = "completed"


class Enrollment(Entity[UUID]):
    """Enrollment entity representing a competitor's enrollment in a modality.

    This is the association between Competitor and Modality with additional
    enrollment-specific data.
    """

    def __init__(
        self,
        competitor_id: UUID,
        modality_id: UUID,
        evaluator_id: UUID | None = None,
        enrolled_at: date | None = None,
        status: EnrollmentStatus = EnrollmentStatus.ACTIVE,
        notes: str | None = None,
        id: UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        super().__init__(id=id, created_at=created_at, updated_at=updated_at)
        self._competitor_id = competitor_id
        self._modality_id = modality_id
        self._evaluator_id = evaluator_id
        self._enrolled_at = enrolled_at or date.today()
        self._status = status
        self._notes = notes

    @property
    def competitor_id(self) -> UUID:
        """Get competitor ID."""
        return self._competitor_id

    @property
    def modality_id(self) -> UUID:
        """Get modality ID."""
        return self._modality_id

    @property
    def evaluator_id(self) -> UUID | None:
        """Get assigned evaluator ID."""
        return self._evaluator_id

    @property
    def enrolled_at(self) -> date:
        """Get enrollment date."""
        return self._enrolled_at

    @property
    def status(self) -> EnrollmentStatus:
        """Get enrollment status."""
        return self._status

    @property
    def notes(self) -> str | None:
        """Get enrollment notes."""
        return self._notes

    @property
    def is_active(self) -> bool:
        """Check if enrollment is active."""
        return self._status == EnrollmentStatus.ACTIVE

    def assign_evaluator(self, evaluator_id: UUID) -> None:
        """Assign an evaluator to this enrollment.

        Args:
            evaluator_id: The evaluator's user ID.
        """
        self._evaluator_id = evaluator_id
        self._touch()

    def remove_evaluator(self) -> None:
        """Remove the assigned evaluator."""
        self._evaluator_id = None
        self._touch()

    def activate(self) -> None:
        """Activate the enrollment."""
        self._status = EnrollmentStatus.ACTIVE
        self._touch()

    def deactivate(self) -> None:
        """Deactivate the enrollment."""
        self._status = EnrollmentStatus.INACTIVE
        self._touch()

    def suspend(self) -> None:
        """Suspend the enrollment."""
        self._status = EnrollmentStatus.SUSPENDED
        self._touch()

    def complete(self) -> None:
        """Mark enrollment as completed."""
        self._status = EnrollmentStatus.COMPLETED
        self._touch()

    def update_notes(self, notes: str | None) -> None:
        """Update enrollment notes."""
        self._notes = notes
        self._touch()

    def __repr__(self) -> str:
        return f"Enrollment(id={self._id}, competitor={self._competitor_id}, modality={self._modality_id})"
