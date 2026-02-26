"""Feedback repository interface."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.extras.entities.feedback import Feedback
from src.shared.constants.enums import FeedbackType


class FeedbackRepository(ABC):
    """Abstract repository for feedback."""

    @abstractmethod
    async def save(self, feedback: Feedback) -> Feedback:
        """Save a feedback."""
        ...

    @abstractmethod
    async def get_by_id(self, feedback_id: UUID) -> Feedback | None:
        """Get feedback by ID."""
        ...

    @abstractmethod
    async def get_by_competitor(
        self,
        competitor_id: UUID,
        feedback_type: FeedbackType | None = None,
        is_read: bool | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Feedback]:
        """Get feedback for a competitor."""
        ...

    @abstractmethod
    async def get_by_evaluator(
        self,
        evaluator_id: UUID,
        competitor_id: UUID | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Feedback]:
        """Get feedback given by an evaluator."""
        ...

    @abstractmethod
    async def get_by_exam(
        self,
        exam_id: UUID,
        competitor_id: UUID | None = None,
    ) -> list[Feedback]:
        """Get feedback for an exam."""
        ...

    @abstractmethod
    async def get_by_grade(
        self,
        grade_id: UUID,
    ) -> list[Feedback]:
        """Get feedback for a grade."""
        ...

    @abstractmethod
    async def get_unread_count(
        self,
        competitor_id: UUID,
    ) -> int:
        """Get unread feedback count for a competitor."""
        ...

    @abstractmethod
    async def mark_as_read(self, feedback_id: UUID) -> bool:
        """Mark feedback as read."""
        ...

    @abstractmethod
    async def update(self, feedback: Feedback) -> Feedback:
        """Update a feedback."""
        ...

    @abstractmethod
    async def delete(self, feedback_id: UUID) -> bool:
        """Delete a feedback."""
        ...
