"""Evidence repository interface."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.training.entities.evidence import Evidence


class EvidenceRepository(ABC):
    """Repository interface for Evidence entity."""

    @abstractmethod
    async def create(self, evidence: Evidence) -> Evidence:
        """Create a new evidence record.

        Args:
            evidence: Evidence to create.

        Returns:
            Created evidence with ID.
        """
        pass

    @abstractmethod
    async def get_by_id(self, evidence_id: UUID) -> Evidence | None:
        """Get evidence by ID.

        Args:
            evidence_id: Evidence ID.

        Returns:
            Evidence if found, None otherwise.
        """
        pass

    @abstractmethod
    async def get_by_training_session(
        self,
        training_session_id: UUID,
    ) -> list[Evidence]:
        """Get all evidences for a training session.

        Args:
            training_session_id: Training session ID.

        Returns:
            List of evidences.
        """
        pass

    @abstractmethod
    async def update(self, evidence: Evidence) -> Evidence:
        """Update evidence.

        Args:
            evidence: Evidence to update.

        Returns:
            Updated evidence.
        """
        pass

    @abstractmethod
    async def delete(self, evidence_id: UUID) -> bool:
        """Delete evidence.

        Args:
            evidence_id: Evidence ID.

        Returns:
            True if deleted, False if not found.
        """
        pass

    @abstractmethod
    async def delete_by_training_session(self, training_session_id: UUID) -> int:
        """Delete all evidences for a training session.

        Args:
            training_session_id: Training session ID.

        Returns:
            Number of evidences deleted.
        """
        pass

    @abstractmethod
    async def count_by_training_session(self, training_session_id: UUID) -> int:
        """Count evidences for a training session.

        Args:
            training_session_id: Training session ID.

        Returns:
            Count of evidences.
        """
        pass
