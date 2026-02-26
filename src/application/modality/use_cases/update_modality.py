"""Update modality use case."""

from uuid import UUID

from src.application.modality.dtos.modality_dto import ModalityDTO, UpdateModalityDTO
from src.domain.modality.exceptions import ModalityNotFoundException
from src.domain.modality.repositories.modality_repository import ModalityRepository
from src.domain.modality.value_objects.modality_code import ModalityCode


class UpdateModalityUseCase:
    """Use case for updating a modality."""

    def __init__(self, modality_repository: ModalityRepository) -> None:
        self._modality_repository = modality_repository

    async def execute(
        self,
        modality_id: UUID,
        dto: UpdateModalityDTO,
    ) -> ModalityDTO:
        """Update a modality.

        Args:
            modality_id: Modality identifier.
            dto: Update data.

        Returns:
            Updated modality DTO.

        Raises:
            ModalityNotFoundException: If modality not found.
        """
        modality = await self._modality_repository.get_by_id(modality_id)

        if not modality:
            raise ModalityNotFoundException(identifier=str(modality_id))

        # Update fields
        new_code = ModalityCode(dto.code) if dto.code else None
        modality.update(
            code=new_code,
            name=dto.name,
            description=dto.description,
            min_training_hours=dto.min_training_hours,
        )

        # Handle activation/deactivation
        if dto.is_active is not None:
            if dto.is_active:
                modality.activate()
            else:
                modality.deactivate()

        # Persist
        updated = await self._modality_repository.update(modality)

        return ModalityDTO.from_entity(updated)
