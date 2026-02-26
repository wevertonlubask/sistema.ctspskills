"""Competitor repository interface."""

from abc import abstractmethod
from uuid import UUID

from src.domain.modality.entities.competitor import Competitor
from src.shared.domain.repository import Repository


class CompetitorRepository(Repository[Competitor, UUID]):
    """Repository interface for Competitor aggregate."""

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> Competitor | None:
        """Get competitor by user ID.

        Args:
            user_id: User ID.

        Returns:
            Competitor if found, None otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False,
    ) -> list[Competitor]:
        """Get all competitors with pagination.

        Args:
            skip: Number of records to skip.
            limit: Maximum number of records to return.
            active_only: If True, return only active competitors.

        Returns:
            List of competitors.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_modality(
        self,
        modality_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Competitor]:
        """Get competitors enrolled in a modality.

        Args:
            modality_id: Modality ID.
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            List of competitors.
        """
        raise NotImplementedError

    @abstractmethod
    async def count(self, active_only: bool = False) -> int:
        """Count total number of competitors.

        Args:
            active_only: If True, count only active competitors.

        Returns:
            Total count.
        """
        raise NotImplementedError

    @abstractmethod
    async def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Competitor]:
        """Search competitors by name.

        Args:
            query: Search query.
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            List of matching competitors.
        """
        raise NotImplementedError
