"""Exam repository interface."""

from abc import ABC, abstractmethod
from datetime import date
from uuid import UUID

from src.domain.assessment.entities.exam import Exam


class ExamRepository(ABC):
    """Abstract repository interface for Exam aggregate."""

    @abstractmethod
    async def get_by_id(self, exam_id: UUID) -> Exam | None:
        """Get exam by ID.

        Args:
            exam_id: Exam UUID.

        Returns:
            Exam entity or None if not found.
        """
        ...

    @abstractmethod
    async def add(self, exam: Exam) -> Exam:
        """Add a new exam.

        Args:
            exam: Exam entity to add.

        Returns:
            Added exam with generated ID.
        """
        ...

    @abstractmethod
    async def update(self, exam: Exam) -> Exam:
        """Update an existing exam.

        Args:
            exam: Exam entity with updated data.

        Returns:
            Updated exam entity.
        """
        ...

    @abstractmethod
    async def delete(self, exam_id: UUID) -> bool:
        """Delete an exam.

        Args:
            exam_id: Exam UUID to delete.

        Returns:
            True if deleted, False if not found.
        """
        ...

    @abstractmethod
    async def exists(self, exam_id: UUID) -> bool:
        """Check if exam exists.

        Args:
            exam_id: Exam UUID.

        Returns:
            True if exists.
        """
        ...

    @abstractmethod
    async def get_all(
        self,
        active_only: bool = True,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Exam]:
        """Get all exams.

        Args:
            active_only: Whether to return only active exams.
            skip: Number of records to skip.
            limit: Maximum records to return.

        Returns:
            List of exams.
        """
        ...

    @abstractmethod
    async def get_by_modality(
        self,
        modality_id: UUID,
        active_only: bool = True,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Exam]:
        """Get exams by modality.

        Args:
            modality_id: Modality UUID.
            active_only: Whether to return only active exams.
            skip: Number of records to skip.
            limit: Maximum records to return.

        Returns:
            List of exams.
        """
        ...

    @abstractmethod
    async def get_by_date_range(
        self,
        modality_id: UUID | None,
        start_date: date,
        end_date: date,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Exam]:
        """Get exams within a date range.

        Args:
            modality_id: Optional modality filter.
            start_date: Start of date range.
            end_date: End of date range.
            skip: Number of records to skip.
            limit: Maximum records to return.

        Returns:
            List of exams.
        """
        ...

    @abstractmethod
    async def get_by_creator(
        self,
        creator_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Exam]:
        """Get exams created by a specific user.

        Args:
            creator_id: Creator user UUID.
            skip: Number of records to skip.
            limit: Maximum records to return.

        Returns:
            List of exams.
        """
        ...

    @abstractmethod
    async def count(
        self,
        modality_id: UUID | None = None,
        active_only: bool = True,
    ) -> int:
        """Count exams with optional filters.

        Args:
            modality_id: Optional modality filter.
            active_only: Whether to count only active exams.

        Returns:
            Number of exams.
        """
        ...
