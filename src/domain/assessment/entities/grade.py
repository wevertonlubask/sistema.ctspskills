"""Grade entity for assessment management."""

from datetime import datetime
from uuid import UUID

from src.domain.assessment.value_objects.score import Score
from src.shared.domain.aggregate_root import AggregateRoot


class Grade(AggregateRoot[UUID]):
    """Grade aggregate root representing a competitor's score on a competence.

    Each grade links an exam, competitor, and competence with a score.
    Includes audit fields for tracking who created/updated the grade.
    """

    def __init__(
        self,
        exam_id: UUID,
        competitor_id: UUID,
        competence_id: UUID,
        score: Score,
        created_by: UUID,
        notes: str | None = None,
        updated_by: UUID | None = None,
        id: UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        """Initialize Grade entity.

        Args:
            exam_id: ID of the exam.
            competitor_id: ID of the competitor.
            competence_id: ID of the competence being graded.
            score: Score value object (0-100).
            created_by: ID of the user who created the grade.
            notes: Optional notes/comments about the grade.
            updated_by: ID of the last user who updated the grade.
            id: Optional ID (auto-generated if not provided).
            created_at: Optional creation timestamp.
            updated_at: Optional update timestamp.
        """
        super().__init__(id=id, created_at=created_at, updated_at=updated_at)
        self._exam_id = exam_id
        self._competitor_id = competitor_id
        self._competence_id = competence_id
        self._score = score
        self._created_by = created_by
        self._notes = notes.strip() if notes else None
        self._updated_by = updated_by or created_by

    @property
    def exam_id(self) -> UUID:
        """Get exam ID."""
        return self._exam_id

    @property
    def competitor_id(self) -> UUID:
        """Get competitor ID."""
        return self._competitor_id

    @property
    def competence_id(self) -> UUID:
        """Get competence ID."""
        return self._competence_id

    @property
    def score(self) -> Score:
        """Get score value object."""
        return self._score

    @property
    def notes(self) -> str | None:
        """Get grade notes."""
        return self._notes

    @property
    def created_by(self) -> UUID:
        """Get creator user ID."""
        return self._created_by

    @property
    def updated_by(self) -> UUID:
        """Get last updater user ID."""
        return self._updated_by

    def update_score(self, new_score: Score, updated_by: UUID) -> float:
        """Update the grade score.

        Args:
            new_score: New Score value object.
            updated_by: ID of the user making the update.

        Returns:
            The old score value (for audit logging).
        """
        old_score = self._score.value
        self._score = new_score
        self._updated_by = updated_by
        self._touch()
        return old_score

    def update_notes(self, notes: str | None, updated_by: UUID) -> str | None:
        """Update the grade notes.

        Args:
            notes: New notes (can be None to clear).
            updated_by: ID of the user making the update.

        Returns:
            The old notes value (for audit logging).
        """
        old_notes = self._notes
        self._notes = notes.strip() if notes else None
        self._updated_by = updated_by
        self._touch()
        return old_notes

    def absolute_score(self, max_score: float) -> float:
        """Get score as absolute value.

        Args:
            max_score: Maximum score for the competence.

        Returns:
            Absolute score value.
        """
        return self._score.to_absolute(max_score)

    def __repr__(self) -> str:
        return (
            f"Grade(id={self._id}, exam_id={self._exam_id}, "
            f"competitor_id={self._competitor_id}, score={self._score.value})"
        )
