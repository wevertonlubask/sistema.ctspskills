"""Feedback use cases."""

from typing import Any
from uuid import UUID

from src.application.extras.dtos.feedback_dto import (
    CreateFeedbackDTO,
    FeedbackDTO,
    FeedbackListDTO,
)
from src.domain.extras.entities.feedback import Feedback
from src.domain.extras.exceptions import FeedbackNotFoundException
from src.domain.extras.repositories.feedback_repository import FeedbackRepository
from src.shared.constants.enums import FeedbackType


class CreateFeedbackUseCase:
    """Use case for creating feedback."""

    def __init__(self, feedback_repository: FeedbackRepository) -> None:
        self._feedback_repository = feedback_repository

    async def execute(
        self,
        evaluator_id: UUID,
        dto: CreateFeedbackDTO,
    ) -> FeedbackDTO:
        """Create feedback for a competitor.

        Args:
            evaluator_id: Evaluator user UUID.
            dto: Feedback data.

        Returns:
            Created feedback DTO.
        """
        feedback = Feedback(
            competitor_id=dto.competitor_id,
            evaluator_id=evaluator_id,
            content=dto.content,
            feedback_type=dto.feedback_type,
            exam_id=dto.exam_id,
            competence_id=dto.competence_id,
            grade_id=dto.grade_id,
            training_id=dto.training_id,
            rating=dto.rating,
            is_private=dto.is_private,
        )

        saved = await self._feedback_repository.save(feedback)
        return FeedbackDTO.from_entity(saved)

    async def create_positive(
        self,
        evaluator_id: UUID,
        competitor_id: UUID,
        content: str,
        **kwargs: Any,
    ) -> FeedbackDTO:
        """Create positive feedback."""
        dto = CreateFeedbackDTO(
            competitor_id=competitor_id,
            content=content,
            feedback_type=FeedbackType.POSITIVE,
            **kwargs,
        )
        return await self.execute(evaluator_id, dto)

    async def create_constructive(
        self,
        evaluator_id: UUID,
        competitor_id: UUID,
        content: str,
        **kwargs: Any,
    ) -> FeedbackDTO:
        """Create constructive feedback."""
        dto = CreateFeedbackDTO(
            competitor_id=competitor_id,
            content=content,
            feedback_type=FeedbackType.CONSTRUCTIVE,
            **kwargs,
        )
        return await self.execute(evaluator_id, dto)


class ListFeedbackUseCase:
    """Use case for listing feedback."""

    def __init__(self, feedback_repository: FeedbackRepository) -> None:
        self._feedback_repository = feedback_repository

    async def execute(
        self,
        competitor_id: UUID,
        feedback_type: FeedbackType | None = None,
        is_read: bool | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> FeedbackListDTO:
        """List feedback for a competitor.

        Args:
            competitor_id: Competitor UUID.
            feedback_type: Optional feedback type filter.
            is_read: Optional read status filter.
            skip: Number of items to skip.
            limit: Maximum items to return.

        Returns:
            Feedback list DTO.
        """
        feedbacks = await self._feedback_repository.get_by_competitor(
            competitor_id=competitor_id,
            feedback_type=feedback_type,
            is_read=is_read,
            skip=skip,
            limit=limit,
        )

        unread_count = await self._feedback_repository.get_unread_count(competitor_id)

        return FeedbackListDTO(
            feedbacks=[FeedbackDTO.from_entity(f) for f in feedbacks],
            total=len(feedbacks),
            unread_count=unread_count,
        )

    async def get_by_evaluator(
        self,
        evaluator_id: UUID,
        competitor_id: UUID | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> FeedbackListDTO:
        """List feedback given by an evaluator."""
        feedbacks = await self._feedback_repository.get_by_evaluator(
            evaluator_id=evaluator_id,
            competitor_id=competitor_id,
            skip=skip,
            limit=limit,
        )

        return FeedbackListDTO(
            feedbacks=[FeedbackDTO.from_entity(f) for f in feedbacks],
            total=len(feedbacks),
            unread_count=0,
        )

    async def mark_as_read(self, feedback_id: UUID) -> bool:
        """Mark feedback as read."""
        feedback = await self._feedback_repository.get_by_id(feedback_id)
        if not feedback:
            raise FeedbackNotFoundException(str(feedback_id))

        return await self._feedback_repository.mark_as_read(feedback_id)
