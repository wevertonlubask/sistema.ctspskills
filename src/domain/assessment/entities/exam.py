"""Exam entity for assessment management."""

from datetime import date, datetime
from uuid import UUID

from src.shared.constants.enums import AssessmentType
from src.shared.domain.aggregate_root import AggregateRoot


class Exam(AggregateRoot[UUID]):
    """Exam aggregate root representing an assessment session.

    An exam defines which competences are being evaluated, when, and by whom.
    Grades are linked to exams but managed as separate aggregates.
    """

    def __init__(
        self,
        name: str,
        modality_id: UUID,
        assessment_type: AssessmentType,
        exam_date: date,
        created_by: UUID,
        description: str | None = None,
        competence_ids: list[UUID] | None = None,
        is_active: bool = True,
        id: UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        """Initialize Exam entity.

        Args:
            name: Exam name/title.
            modality_id: ID of the modality this exam belongs to.
            assessment_type: Type of assessment (simulation, practical, etc.).
            exam_date: Date when the exam takes/took place.
            created_by: ID of the user who created the exam.
            description: Optional description of the exam.
            competence_ids: List of competence IDs being evaluated.
            is_active: Whether the exam is active.
            id: Optional ID (auto-generated if not provided).
            created_at: Optional creation timestamp.
            updated_at: Optional update timestamp.
        """
        super().__init__(id=id, created_at=created_at, updated_at=updated_at)
        self._name = name.strip()
        self._modality_id = modality_id
        self._assessment_type = assessment_type
        self._exam_date = exam_date
        self._created_by = created_by
        self._description = description.strip() if description else None
        self._competence_ids = list(competence_ids) if competence_ids else []
        self._is_active = is_active

    @property
    def name(self) -> str:
        """Get exam name."""
        return self._name

    @property
    def modality_id(self) -> UUID:
        """Get modality ID."""
        return self._modality_id

    @property
    def assessment_type(self) -> AssessmentType:
        """Get assessment type."""
        return self._assessment_type

    @property
    def exam_date(self) -> date:
        """Get exam date."""
        return self._exam_date

    @property
    def created_by(self) -> UUID:
        """Get creator user ID."""
        return self._created_by

    @property
    def description(self) -> str | None:
        """Get exam description."""
        return self._description

    @property
    def competence_ids(self) -> list[UUID]:
        """Get list of competence IDs."""
        return self._competence_ids.copy()

    @property
    def is_active(self) -> bool:
        """Check if exam is active."""
        return self._is_active

    def update(
        self,
        name: str | None = None,
        description: str | None = None,
        exam_date: date | None = None,
        assessment_type: AssessmentType | None = None,
    ) -> None:
        """Update exam details.

        Args:
            name: New name (optional).
            description: New description (optional).
            exam_date: New exam date (optional).
            assessment_type: New assessment type (optional).
        """
        if name is not None:
            self._name = name.strip()
        if description is not None:
            self._description = description.strip() if description else None
        if exam_date is not None:
            self._exam_date = exam_date
        if assessment_type is not None:
            self._assessment_type = assessment_type
        self._touch()

    def add_competence(self, competence_id: UUID) -> bool:
        """Add a competence to the exam.

        Args:
            competence_id: ID of the competence to add.

        Returns:
            True if added, False if already present.
        """
        if competence_id not in self._competence_ids:
            self._competence_ids.append(competence_id)
            self._touch()
            return True
        return False

    def remove_competence(self, competence_id: UUID) -> bool:
        """Remove a competence from the exam.

        Args:
            competence_id: ID of the competence to remove.

        Returns:
            True if removed, False if not found.
        """
        if competence_id in self._competence_ids:
            self._competence_ids.remove(competence_id)
            self._touch()
            return True
        return False

    def has_competence(self, competence_id: UUID) -> bool:
        """Check if exam includes a specific competence.

        Args:
            competence_id: ID of the competence to check.

        Returns:
            True if competence is in the exam.
        """
        return competence_id in self._competence_ids

    def activate(self) -> None:
        """Activate the exam."""
        if not self._is_active:
            self._is_active = True
            self._touch()

    def deactivate(self) -> None:
        """Deactivate the exam."""
        if self._is_active:
            self._is_active = False
            self._touch()

    def __repr__(self) -> str:
        return (
            f"Exam(id={self._id}, name={self._name}, "
            f"modality_id={self._modality_id}, date={self._exam_date})"
        )
