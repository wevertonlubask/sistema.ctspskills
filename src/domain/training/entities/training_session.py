"""TrainingSession entity - represents a training record."""

from datetime import date, datetime
from uuid import UUID

from src.domain.training.entities.evidence import Evidence
from src.domain.training.value_objects.training_hours import TrainingHours
from src.shared.constants.enums import TrainingStatus, TrainingType
from src.shared.domain.entity import Entity


class TrainingSession(Entity[UUID]):
    """Training session entity representing a competitor's training record.

    This is the aggregate root for training records. A training session
    captures when, where, and how long a competitor trained.

    Business Rules:
    - RN01: Only competitors enrolled in a modality can register training
    - RN04: Maximum 12 hours per day
    - RN11: Training must be validated by evaluator to count in statistics
    """

    def __init__(
        self,
        competitor_id: UUID,
        modality_id: UUID,
        enrollment_id: UUID,
        training_date: date,
        hours: TrainingHours,
        training_type: TrainingType = TrainingType.SENAI,
        location: str | None = None,
        description: str | None = None,
        status: TrainingStatus = TrainingStatus.PENDING,
        validated_by: UUID | None = None,
        validated_at: datetime | None = None,
        rejection_reason: str | None = None,
        id: UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        """Initialize training session.

        Args:
            competitor_id: ID of the competitor who trained.
            modality_id: ID of the modality being trained.
            enrollment_id: ID of the enrollment (links competitor to modality).
            training_date: Date when training occurred.
            hours: Training duration (value object).
            training_type: Where training occurred (SENAI/EXTERNAL).
            location: Specific location name.
            description: Description of activities.
            status: Validation status.
            validated_by: Evaluator who validated.
            validated_at: When validation occurred.
            rejection_reason: Reason if rejected.
            id: Optional UUID.
            created_at: Creation timestamp.
            updated_at: Update timestamp.
        """
        super().__init__(id=id, created_at=created_at, updated_at=updated_at)
        self._competitor_id = competitor_id
        self._modality_id = modality_id
        self._enrollment_id = enrollment_id
        self._training_date = training_date
        self._hours = hours
        self._training_type = training_type
        self._location = location
        self._description = description
        self._status = status
        self._validated_by = validated_by
        self._validated_at = validated_at
        self._rejection_reason = rejection_reason
        self._evidences: list[Evidence] = []

    @property
    def competitor_id(self) -> UUID:
        """Get competitor ID."""
        return self._competitor_id

    @property
    def modality_id(self) -> UUID:
        """Get modality ID."""
        return self._modality_id

    @property
    def enrollment_id(self) -> UUID:
        """Get enrollment ID."""
        return self._enrollment_id

    @property
    def training_date(self) -> date:
        """Get training date."""
        return self._training_date

    @property
    def hours(self) -> TrainingHours:
        """Get training hours."""
        return self._hours

    @property
    def training_type(self) -> TrainingType:
        """Get training type (SENAI/EXTERNAL)."""
        return self._training_type

    @property
    def location(self) -> str | None:
        """Get specific location."""
        return self._location

    @property
    def description(self) -> str | None:
        """Get activity description."""
        return self._description

    @property
    def status(self) -> TrainingStatus:
        """Get validation status."""
        return self._status

    @property
    def validated_by(self) -> UUID | None:
        """Get validating evaluator ID."""
        return self._validated_by

    @property
    def validated_at(self) -> datetime | None:
        """Get validation timestamp."""
        return self._validated_at

    @property
    def rejection_reason(self) -> str | None:
        """Get rejection reason if rejected."""
        return self._rejection_reason

    @property
    def evidences(self) -> list[Evidence]:
        """Get list of evidences."""
        return self._evidences.copy()

    @property
    def is_pending(self) -> bool:
        """Check if training is pending validation."""
        return self._status == TrainingStatus.PENDING

    @property
    def is_approved(self) -> bool:
        """Check if training is approved."""
        return self._status == TrainingStatus.APPROVED

    @property
    def is_rejected(self) -> bool:
        """Check if training is rejected."""
        return self._status == TrainingStatus.REJECTED

    @property
    def is_senai(self) -> bool:
        """Check if training was at SENAI."""
        return self._training_type == TrainingType.SENAI

    @property
    def is_external(self) -> bool:
        """Check if training was external."""
        return self._training_type == TrainingType.EXTERNAL

    def approve(self, evaluator_id: UUID) -> None:
        """Approve the training session.

        Args:
            evaluator_id: ID of the evaluator approving.
        """
        self._status = TrainingStatus.APPROVED
        self._validated_by = evaluator_id
        self._validated_at = datetime.utcnow()
        self._rejection_reason = None
        self._touch()

    def reject(self, evaluator_id: UUID, reason: str) -> None:
        """Reject the training session.

        Args:
            evaluator_id: ID of the evaluator rejecting.
            reason: Reason for rejection.
        """
        self._status = TrainingStatus.REJECTED
        self._validated_by = evaluator_id
        self._validated_at = datetime.utcnow()
        self._rejection_reason = reason
        self._touch()

    def reset_validation(self) -> None:
        """Reset validation status to pending."""
        self._status = TrainingStatus.PENDING
        self._validated_by = None
        self._validated_at = None
        self._rejection_reason = None
        self._touch()

    def update(
        self,
        training_date: date | None = None,
        hours: TrainingHours | None = None,
        training_type: TrainingType | None = None,
        location: str | None = None,
        description: str | None = None,
    ) -> None:
        """Update training session details.

        Note: Updates reset validation status to pending.
        """
        if training_date is not None:
            self._training_date = training_date
        if hours is not None:
            self._hours = hours
        if training_type is not None:
            self._training_type = training_type
        if location is not None:
            self._location = location
        if description is not None:
            self._description = description

        # Reset validation when details change
        self.reset_validation()

    def add_evidence(self, evidence: Evidence) -> None:
        """Add evidence to the training session."""
        self._evidences.append(evidence)
        self._touch()

    def remove_evidence(self, evidence_id: UUID) -> bool:
        """Remove evidence by ID.

        Returns:
            True if evidence was removed, False if not found.
        """
        for i, evidence in enumerate(self._evidences):
            if evidence.id == evidence_id:
                self._evidences.pop(i)
                self._touch()
                return True
        return False

    def has_evidence(self, evidence_id: UUID) -> bool:
        """Check if evidence exists."""
        return any(e.id == evidence_id for e in self._evidences)

    def __repr__(self) -> str:
        return (
            f"TrainingSession(id={self._id}, competitor={self._competitor_id}, "
            f"date={self._training_date}, hours={self._hours.value}, status={self._status})"
        )
