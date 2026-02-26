"""Competence repository interface."""

from abc import abstractmethod
from uuid import UUID

from src.domain.modality.entities.competence import Competence
from src.shared.domain.repository import Repository


class CompetenceRepository(Repository[Competence, UUID]):
    """Repository interface for Competence entity."""

    @abstractmethod
    async def get_by_modality(
        self,
        modality_id: UUID,
        active_only: bool = False,
    ) -> list[Competence]:
        """Get all competences for a modality.

        Args:
            modality_id: Modality ID.
            active_only: If True, return only active competences.

        Returns:
            List of competences.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_name_and_modality(
        self,
        name: str,
        modality_id: UUID,
    ) -> Competence | None:
        """Get competence by name within a modality.

        Args:
            name: Competence name.
            modality_id: Modality ID.

        Returns:
            Competence if found, None otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    async def count_by_modality(
        self,
        modality_id: UUID,
        active_only: bool = False,
    ) -> int:
        """Count competences in a modality.

        Args:
            modality_id: Modality ID.
            active_only: If True, count only active competences.

        Returns:
            Total count.
        """
        raise NotImplementedError
