"""Feedback entity."""

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from src.shared.constants.enums import FeedbackType
from src.shared.domain.aggregate_root import AggregateRoot


class Feedback(AggregateRoot[UUID]):
    """Feedback entity for evaluator-competitor communication."""

    def __init__(
        self,
        competitor_id: UUID,
        evaluator_id: UUID,
        content: str,
        feedback_type: FeedbackType = FeedbackType.GENERAL,
        exam_id: UUID | None = None,
        competence_id: UUID | None = None,
        grade_id: UUID | None = None,
        training_id: UUID | None = None,
        rating: int | None = None,
        is_private: bool = False,
        is_read: bool = False,
        read_at: datetime | None = None,
        id: UUID | None = None,
        created_at: datetime | None = None,
    ) -> None:
        super().__init__(id=id or uuid4())
        self._competitor_id = competitor_id
        self._evaluator_id = evaluator_id
        self._content = content
        self._feedback_type = feedback_type
        self._exam_id = exam_id
        self._competence_id = competence_id
        self._grade_id = grade_id
        self._training_id = training_id
        self._rating = self._validate_rating(rating)
        self._is_private = is_private
        self._is_read = is_read
        self._read_at = read_at
        self._created_at = created_at or datetime.utcnow()

    def _validate_rating(self, rating: int | None) -> int | None:
        """Validate rating is between 1 and 5."""
        if rating is None:
            return None
        return max(1, min(5, rating))

    @property
    def competitor_id(self) -> UUID:
        return self._competitor_id

    @property
    def evaluator_id(self) -> UUID:
        return self._evaluator_id

    @property
    def content(self) -> str:
        return self._content

    @property
    def feedback_type(self) -> FeedbackType:
        return self._feedback_type

    @property
    def exam_id(self) -> UUID | None:
        return self._exam_id

    @property
    def competence_id(self) -> UUID | None:
        return self._competence_id

    @property
    def grade_id(self) -> UUID | None:
        return self._grade_id

    @property
    def training_id(self) -> UUID | None:
        return self._training_id

    @property
    def rating(self) -> int | None:
        return self._rating

    @property
    def is_private(self) -> bool:
        return self._is_private

    @property
    def is_read(self) -> bool:
        return self._is_read

    @property
    def read_at(self) -> datetime | None:
        return self._read_at

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def related_context(self) -> str:
        """Get the context of the feedback."""
        if self._grade_id:
            return "grade"
        if self._exam_id:
            return "exam"
        if self._training_id:
            return "training"
        if self._competence_id:
            return "competence"
        return "general"

    def mark_as_read(self) -> None:
        """Mark feedback as read."""
        if not self._is_read:
            self._is_read = True
            self._read_at = datetime.utcnow()

    def update_content(self, content: str) -> None:
        """Update feedback content."""
        self._content = content

    def set_rating(self, rating: int) -> None:
        """Set feedback rating."""
        self._rating = self._validate_rating(rating)

    @classmethod
    def create_positive(
        cls,
        competitor_id: UUID,
        evaluator_id: UUID,
        content: str,
        **kwargs: Any,
    ) -> "Feedback":
        """Create positive feedback."""
        return cls(
            competitor_id=competitor_id,
            evaluator_id=evaluator_id,
            content=content,
            feedback_type=FeedbackType.POSITIVE,
            **kwargs,
        )

    @classmethod
    def create_constructive(
        cls,
        competitor_id: UUID,
        evaluator_id: UUID,
        content: str,
        **kwargs: Any,
    ) -> "Feedback":
        """Create constructive feedback."""
        return cls(
            competitor_id=competitor_id,
            evaluator_id=evaluator_id,
            content=content,
            feedback_type=FeedbackType.CONSTRUCTIVE,
            **kwargs,
        )

    @classmethod
    def create_for_grade(
        cls,
        competitor_id: UUID,
        evaluator_id: UUID,
        grade_id: UUID,
        content: str,
        feedback_type: FeedbackType = FeedbackType.GENERAL,
    ) -> "Feedback":
        """Create feedback for a grade."""
        return cls(
            competitor_id=competitor_id,
            evaluator_id=evaluator_id,
            content=content,
            feedback_type=feedback_type,
            grade_id=grade_id,
        )
