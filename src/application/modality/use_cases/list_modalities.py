"""List modalities use case."""

from src.application.modality.dtos.modality_dto import ModalityDTO, ModalityListDTO
from src.domain.modality.repositories.modality_repository import ModalityRepository


class ListModalitiesUseCase:
    """Use case for listing modalities."""

    def __init__(self, modality_repository: ModalityRepository) -> None:
        self._modality_repository = modality_repository

    async def execute(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False,
        search: str | None = None,
    ) -> ModalityListDTO:
        """List modalities with pagination and filtering.

        Args:
            skip: Number of records to skip.
            limit: Maximum records to return.
            active_only: Only return active modalities.
            search: Optional search query.

        Returns:
            Modality list DTO.
        """
        if search:
            modalities = await self._modality_repository.search(
                query=search, skip=skip, limit=limit
            )
            total = len(modalities)  # For search, count is the result length
        else:
            modalities = await self._modality_repository.get_all(
                skip=skip, limit=limit, active_only=active_only
            )
            total = await self._modality_repository.count(active_only=active_only)

        return ModalityListDTO(
            modalities=[ModalityDTO.from_entity(m) for m in modalities],
            total=total,
            skip=skip,
            limit=limit,
        )
