"""Get modality use case."""

from uuid import UUID

from src.application.modality.dtos.modality_dto import ModalityDTO
from src.domain.modality.exceptions import ModalityNotFoundException
from src.domain.modality.repositories.modality_repository import ModalityRepository


class GetModalityUseCase:
    """Use case for getting a single modality."""

    def __init__(self, modality_repository: ModalityRepository) -> None:
        self._modality_repository = modality_repository

    async def execute(self, modality_id: UUID) -> ModalityDTO:
        """Get modality by ID.

        Args:
            modality_id: Modality identifier.

        Returns:
            Modality DTO.

        Raises:
            ModalityNotFoundException: If modality not found.
        """
        modality = await self._modality_repository.get_by_id(modality_id)

        if not modality:
            raise ModalityNotFoundException(identifier=str(modality_id))

        return ModalityDTO.from_entity(modality)

    async def execute_by_code(self, code: str) -> ModalityDTO:
        """Get modality by code.

        Args:
            code: Modality code.

        Returns:
            Modality DTO.

        Raises:
            ModalityNotFoundException: If modality not found.
        """
        modality = await self._modality_repository.get_by_code(code)

        if not modality:
            raise ModalityNotFoundException(identifier=code, field="code")

        return ModalityDTO.from_entity(modality)
