"""Grade repository interface."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.assessment.entities.grade import Grade


class GradeRepository(ABC):
    """Abstract repository interface for Grade aggregate."""

    @abstractmethod
    async def get_by_id(self, grade_id: UUID) -> Grade | None:
        """Get grade by ID.

        Args:
            grade_id: Grade UUID.

        Returns:
            Grade entity or None if not found.
        """
        ...

    @abstractmethod
    async def add(self, grade: Grade) -> Grade:
        """Add a new grade.

        Args:
            grade: Grade entity to add.

        Returns:
            Added grade with generated ID.
        """
        ...

    @abstractmethod
    async def update(self, grade: Grade) -> Grade:
        """Update an existing grade.

        Args:
            grade: Grade entity with updated data.

        Returns:
            Updated grade entity.
        """
        ...

    @abstractmethod
    async def delete(self, grade_id: UUID) -> bool:
        """Delete a grade.

        Args:
            grade_id: Grade UUID to delete.

        Returns:
            True if deleted, False if not found.
        """
        ...

    @abstractmethod
    async def exists(self, grade_id: UUID) -> bool:
        """Check if grade exists.

        Args:
            grade_id: Grade UUID.

        Returns:
            True if exists.
        """
        ...

    @abstractmethod
    async def exists_for_exam_competitor_competence(
        self,
        exam_id: UUID,
        competitor_id: UUID,
        competence_id: UUID,
    ) -> bool:
        """Check if a grade exists for the given combination.

        Args:
            exam_id: Exam UUID.
            competitor_id: Competitor UUID.
            competence_id: Competence UUID.

        Returns:
            True if grade already exists.
        """
        ...

    @abstractmethod
    async def get_by_exam(
        self,
        exam_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Grade]:
        """Get all grades for an exam.

        Args:
            exam_id: Exam UUID.
            skip: Number of records to skip.
            limit: Maximum records to return.

        Returns:
            List of grades.
        """
        ...

    @abstractmethod
    async def get_by_competitor(
        self,
        competitor_id: UUID,
        exam_id: UUID | None = None,
        competence_id: UUID | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Grade]:
        """Get grades for a competitor.

        Args:
            competitor_id: Competitor UUID.
            exam_id: Optional exam filter.
            competence_id: Optional competence filter.
            skip: Number of records to skip.
            limit: Maximum records to return.

        Returns:
            List of grades.
        """
        ...

    @abstractmethod
    async def get_by_exam_and_competitor(
        self,
        exam_id: UUID,
        competitor_id: UUID,
    ) -> list[Grade]:
        """Get all grades for a competitor in an exam.

        Args:
            exam_id: Exam UUID.
            competitor_id: Competitor UUID.

        Returns:
            List of grades.
        """
        ...

    @abstractmethod
    async def get_by_exam_and_competence(
        self,
        exam_id: UUID,
        competence_id: UUID,
    ) -> list[Grade]:
        """Get all grades for a competence in an exam.

        Args:
            exam_id: Exam UUID.
            competence_id: Competence UUID.

        Returns:
            List of grades for statistics calculation.
        """
        ...

    @abstractmethod
    async def get_by_competitor_and_competence(
        self,
        competitor_id: UUID,
        competence_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Grade]:
        """Get grades for a competitor on a specific competence.

        Args:
            competitor_id: Competitor UUID.
            competence_id: Competence UUID.
            skip: Number of records to skip.
            limit: Maximum records to return.

        Returns:
            List of grades.
        """
        ...

    @abstractmethod
    async def get_scores_for_statistics(
        self,
        exam_id: UUID,
        competence_id: UUID | None = None,
    ) -> list[float]:
        """Get score values for statistics calculation.

        Args:
            exam_id: Exam UUID.
            competence_id: Optional competence filter.

        Returns:
            List of score values.
        """
        ...

    @abstractmethod
    async def count(
        self,
        exam_id: UUID | None = None,
        competitor_id: UUID | None = None,
        competence_id: UUID | None = None,
    ) -> int:
        """Count grades with optional filters.

        Args:
            exam_id: Optional exam filter.
            competitor_id: Optional competitor filter.
            competence_id: Optional competence filter.

        Returns:
            Number of grades.
        """
        ...

    @abstractmethod
    async def get_average_score(
        self,
        exam_id: UUID | None = None,
        competitor_id: UUID | None = None,
        competence_id: UUID | None = None,
    ) -> float | None:
        """Calculate average score with filters.

        Args:
            exam_id: Optional exam filter.
            competitor_id: Optional competitor filter.
            competence_id: Optional competence filter.

        Returns:
            Average score or None if no grades.
        """
        ...
