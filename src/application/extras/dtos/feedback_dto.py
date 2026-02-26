"""Feedback DTOs."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.domain.extras.entities.feedback import Feedback
from src.shared.constants.enums import FeedbackType


@dataclass
class CreateFeedbackDTO:
    """DTO for creating feedback."""

    competitor_id: UUID
    content: str
    feedback_type: FeedbackType = FeedbackType.GENERAL
    exam_id: UUID | None = None
    competence_id: UUID | None = None
    grade_id: UUID | None = None
    training_id: UUID | None = None
    rating: int | None = None
    is_private: bool = False


@dataclass
class FeedbackDTO:
    """DTO for feedback responses."""

    id: UUID
    competitor_id: UUID
    evaluator_id: UUID
    content: str
    feedback_type: str
    exam_id: UUID | None
    competence_id: UUID | None
    grade_id: UUID | None
    training_id: UUID | None
    rating: int | None
    is_private: bool
    is_read: bool
    read_at: datetime | None
    related_context: str
    created_at: datetime
    evaluator_name: str | None = None

    @classmethod
    def from_entity(cls, entity: Feedback, evaluator_name: str | None = None) -> "FeedbackDTO":
        return cls(
            id=entity.id,
            competitor_id=entity.competitor_id,
            evaluator_id=entity.evaluator_id,
            content=entity.content,
            feedback_type=entity.feedback_type.value,
            exam_id=entity.exam_id,
            competence_id=entity.competence_id,
            grade_id=entity.grade_id,
            training_id=entity.training_id,
            rating=entity.rating,
            is_private=entity.is_private,
            is_read=entity.is_read,
            read_at=entity.read_at,
            related_context=entity.related_context,
            created_at=entity.created_at,
            evaluator_name=evaluator_name,
        )


@dataclass
class FeedbackListDTO:
    """DTO for feedback list."""

    feedbacks: list[FeedbackDTO]
    total: int
    unread_count: int
