"""Training type configuration repository interface."""

from abc import abstractmethod
from uuid import UUID

from src.domain.training.entities.training_type_config import TrainingTypeConfig
from src.shared.domain.repository import Repository


class TrainingTypeConfigRepository(Repository[TrainingTypeConfig, UUID]):
    """Repository interface for TrainingTypeConfig aggregate."""

    @abstractmethod
    async def get_by_code(self, code: str) -> TrainingTypeConfig | None:
        """Get training type by code.

        Args:
            code: Training type code.

        Returns:
            TrainingTypeConfig if found, None otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False,
    ) -> list[TrainingTypeConfig]:
        """Get all training types with pagination.

        Args:
            skip: Number of records to skip.
            limit: Maximum number of records to return.
            active_only: If True, return only active types.

        Returns:
            List of training types ordered by display_order.
        """
        raise NotImplementedError

    @abstractmethod
    async def count(self, active_only: bool = False) -> int:
        """Count total number of training types.

        Args:
            active_only: If True, count only active types.

        Returns:
            Total count.
        """
        raise NotImplementedError

    @abstractmethod
    async def code_exists(self, code: str, exclude_id: UUID | None = None) -> bool:
        """Check if training type code already exists.

        Args:
            code: Code to check.
            exclude_id: Optional ID to exclude from check (for updates).

        Returns:
            True if code exists.
        """
        raise NotImplementedError
