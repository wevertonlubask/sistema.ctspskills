"""Delete modality use case."""

from uuid import UUID

from src.domain.modality.exceptions import ModalityNotFoundException
from src.domain.modality.repositories.modality_repository import ModalityRepository


class DeleteModalityUseCase:
    """Use case for deleting a modality."""

    def __init__(self, modality_repository: ModalityRepository) -> None:
        self._modality_repository = modality_repository

    async def execute(self, modality_id: UUID) -> bool:
        """Delete a modality.

        Args:
            modality_id: Modality identifier.

        Returns:
            True if deleted.

        Raises:
            ModalityNotFoundException: If modality not found.
        """
        if not await self._modality_repository.exists(modality_id):
            raise ModalityNotFoundException(identifier=str(modality_id))

        return await self._modality_repository.delete(modality_id)
