"""Training repository interface."""

from abc import ABC, abstractmethod
from datetime import date
from uuid import UUID

from src.domain.training.entities.training_session import TrainingSession
from src.shared.constants.enums import TrainingStatus, TrainingType


class TrainingRepository(ABC):
    """Repository interface for TrainingSession aggregate."""

    @abstractmethod
    async def create(self, training: TrainingSession) -> TrainingSession:
        """Create a new training session.

        Args:
            training: Training session to create.

        Returns:
            Created training session with ID.
        """
        pass

    @abstractmethod
    async def get_by_id(self, training_id: UUID) -> TrainingSession | None:
        """Get training session by ID.

        Args:
            training_id: Training session ID.

        Returns:
            Training session if found, None otherwise.
        """
        pass

    @abstractmethod
    async def update(self, training: TrainingSession) -> TrainingSession:
        """Update a training session.

        Args:
            training: Training session to update.

        Returns:
            Updated training session.
        """
        pass

    @abstractmethod
    async def delete(self, training_id: UUID) -> bool:
        """Delete a training session.

        Args:
            training_id: Training session ID.

        Returns:
            True if deleted, False if not found.
        """
        pass

    @abstractmethod
    async def get_by_competitor(
        self,
        competitor_id: UUID,
        skip: int = 0,
        limit: int = 100,
        status: TrainingStatus | None = None,
        modality_id: UUID | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[TrainingSession]:
        """Get training sessions by competitor.

        Args:
            competitor_id: Competitor ID.
            skip: Number of records to skip.
            limit: Maximum records to return.
            status: Filter by status.
            modality_id: Filter by modality.
            start_date: Filter from this date.
            end_date: Filter until this date.

        Returns:
            List of training sessions.
        """
        pass

    @abstractmethod
    async def get_by_modality(
        self,
        modality_id: UUID,
        skip: int = 0,
        limit: int = 100,
        status: TrainingStatus | None = None,
    ) -> list[TrainingSession]:
        """Get training sessions by modality.

        Args:
            modality_id: Modality ID.
            skip: Number of records to skip.
            limit: Maximum records to return.
            status: Filter by status.

        Returns:
            List of training sessions.
        """
        pass

    @abstractmethod
    async def get_by_evaluator(
        self,
        evaluator_id: UUID,
        skip: int = 0,
        limit: int = 100,
        status: TrainingStatus | None = None,
    ) -> list[TrainingSession]:
        """Get training sessions pending validation by an evaluator.

        Args:
            evaluator_id: Evaluator user ID.
            skip: Number of records to skip.
            limit: Maximum records to return.
            status: Filter by status.

        Returns:
            List of training sessions.
        """
        pass

    @abstractmethod
    async def get_daily_hours(
        self,
        competitor_id: UUID,
        training_date: date,
        exclude_training_id: UUID | None = None,
    ) -> float:
        """Get total training hours for a competitor on a specific date.

        Used to enforce RN04 (max 12h/day).

        Args:
            competitor_id: Competitor ID.
            training_date: Date to check.
            exclude_training_id: Training ID to exclude (for updates).

        Returns:
            Total hours for the date.
        """
        pass

    @abstractmethod
    async def get_total_hours(
        self,
        competitor_id: UUID,
        modality_id: UUID | None = None,
        training_type: TrainingType | None = None,
        approved_only: bool = True,
    ) -> float:
        """Get total training hours for a competitor.

        Args:
            competitor_id: Competitor ID.
            modality_id: Filter by modality.
            training_type: Filter by training type (SENAI/EXTERNAL).
            approved_only: Only count approved trainings.

        Returns:
            Total hours.
        """
        pass

    @abstractmethod
    async def get_pending_count(
        self,
        evaluator_id: UUID | None = None,
        modality_id: UUID | None = None,
    ) -> int:
        """Get count of pending trainings.

        Args:
            evaluator_id: Filter by evaluator.
            modality_id: Filter by modality.

        Returns:
            Count of pending trainings.
        """
        pass

    @abstractmethod
    async def count(
        self,
        competitor_id: UUID | None = None,
        modality_id: UUID | None = None,
        status: TrainingStatus | None = None,
    ) -> int:
        """Count training sessions with filters.

        Args:
            competitor_id: Filter by competitor.
            modality_id: Filter by modality.
            status: Filter by status.

        Returns:
            Count of training sessions.
        """
        pass

    @abstractmethod
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: TrainingStatus | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[TrainingSession]:
        """Get all training sessions.

        Args:
            skip: Number of records to skip.
            limit: Maximum records to return.
            status: Filter by status.
            start_date: Filter from this date.
            end_date: Filter until this date.

        Returns:
            List of training sessions.
        """
        pass

    @abstractmethod
    async def count_all(
        self,
        status: TrainingStatus | None = None,
    ) -> int:
        """Count all training sessions.

        Args:
            status: Filter by status.

        Returns:
            Count of training sessions.
        """
        pass

    @abstractmethod
    async def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[TrainingSession]:
        """Search training sessions.

        Args:
            query: Search query.
            skip: Number of records to skip.
            limit: Maximum records to return.

        Returns:
            List of matching training sessions.
        """
        pass
