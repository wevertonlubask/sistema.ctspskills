"""Enrollment repository interface."""

from abc import abstractmethod
from uuid import UUID

from src.domain.modality.entities.enrollment import Enrollment, EnrollmentStatus
from src.shared.domain.repository import Repository


class EnrollmentRepository(Repository[Enrollment, UUID]):
    """Repository interface for Enrollment entity."""

    @abstractmethod
    async def get_by_competitor_and_modality(
        self,
        competitor_id: UUID,
        modality_id: UUID,
    ) -> Enrollment | None:
        """Get enrollment by competitor and modality.

        Args:
            competitor_id: Competitor ID.
            modality_id: Modality ID.

        Returns:
            Enrollment if found, None otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_competitor(
        self,
        competitor_id: UUID,
        status: EnrollmentStatus | None = None,
    ) -> list[Enrollment]:
        """Get all enrollments for a competitor.

        Args:
            competitor_id: Competitor ID.
            status: Optional status filter.

        Returns:
            List of enrollments.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_modality(
        self,
        modality_id: UUID,
        status: EnrollmentStatus | None = None,
    ) -> list[Enrollment]:
        """Get all enrollments for a modality.

        Args:
            modality_id: Modality ID.
            status: Optional status filter.

        Returns:
            List of enrollments.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_evaluator(
        self,
        evaluator_id: UUID,
        status: EnrollmentStatus | None = None,
    ) -> list[Enrollment]:
        """Get all enrollments assigned to an evaluator.

        Args:
            evaluator_id: Evaluator user ID.
            status: Optional status filter.

        Returns:
            List of enrollments.
        """
        raise NotImplementedError

    @abstractmethod
    async def is_enrolled(
        self,
        competitor_id: UUID,
        modality_id: UUID,
    ) -> bool:
        """Check if competitor is enrolled in modality.

        Args:
            competitor_id: Competitor ID.
            modality_id: Modality ID.

        Returns:
            True if enrolled.
        """
        raise NotImplementedError

    @abstractmethod
    async def is_evaluator_assigned(
        self,
        evaluator_id: UUID,
        modality_id: UUID,
    ) -> bool:
        """Check if evaluator is assigned to any enrollment in modality (RN02).

        Args:
            evaluator_id: Evaluator user ID.
            modality_id: Modality ID.

        Returns:
            True if assigned.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_active_enrollment(
        self,
        competitor_id: UUID,
        modality_id: UUID,
    ) -> Enrollment | None:
        """Get active enrollment for competitor in modality.

        Args:
            competitor_id: Competitor ID.
            modality_id: Modality ID.

        Returns:
            Active enrollment if found, None otherwise.
        """
        raise NotImplementedError
