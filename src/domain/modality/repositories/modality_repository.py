"""Modality repository interface."""

from abc import abstractmethod
from uuid import UUID

from src.domain.modality.entities.modality import Modality
from src.shared.domain.repository import Repository


class ModalityRepository(Repository[Modality, UUID]):
    """Repository interface for Modality aggregate."""

    @abstractmethod
    async def get_by_code(self, code: str) -> Modality | None:
        """Get modality by code.

        Args:
            code: Modality code.

        Returns:
            Modality if found, None otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False,
    ) -> list[Modality]:
        """Get all modalities with pagination.

        Args:
            skip: Number of records to skip.
            limit: Maximum number of records to return.
            active_only: If True, return only active modalities.

        Returns:
            List of modalities.
        """
        raise NotImplementedError

    @abstractmethod
    async def count(self, active_only: bool = False) -> int:
        """Count total number of modalities.

        Args:
            active_only: If True, count only active modalities.

        Returns:
            Total count.
        """
        raise NotImplementedError

    @abstractmethod
    async def code_exists(self, code: str, exclude_id: UUID | None = None) -> bool:
        """Check if modality code already exists.

        Args:
            code: Code to check.
            exclude_id: Optional ID to exclude from check (for updates).

        Returns:
            True if code exists.
        """
        raise NotImplementedError

    @abstractmethod
    async def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Modality]:
        """Search modalities by name or code.

        Args:
            query: Search query.
            skip: Number of records to skip.
            limit: Maximum number of records to return.

        Returns:
            List of matching modalities.
        """
        raise NotImplementedError
