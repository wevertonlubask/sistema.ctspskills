"""Create modality use case."""

from src.application.modality.dtos.modality_dto import CreateModalityDTO, ModalityDTO
from src.domain.modality.entities.modality import Modality
from src.domain.modality.exceptions import ModalityCodeAlreadyExistsException
from src.domain.modality.repositories.modality_repository import ModalityRepository
from src.domain.modality.value_objects.modality_code import ModalityCode


class CreateModalityUseCase:
    """Use case for creating a new modality."""

    def __init__(self, modality_repository: ModalityRepository) -> None:
        self._modality_repository = modality_repository

    async def execute(self, dto: CreateModalityDTO) -> ModalityDTO:
        """Create a new modality.

        Args:
            dto: Modality creation data.

        Returns:
            Created modality DTO.

        Raises:
            ModalityCodeAlreadyExistsException: If code already exists.
            InvalidValueException: If code format is invalid.
        """
        # Validate and create code value object
        code = ModalityCode(dto.code)

        # Check if code already exists
        if await self._modality_repository.code_exists(code.value):
            raise ModalityCodeAlreadyExistsException(code=code.value)

        # Create modality entity
        modality = Modality(
            code=code,
            name=dto.name,
            description=dto.description,
            min_training_hours=dto.min_training_hours,
        )

        # Persist
        created = await self._modality_repository.add(modality)

        return ModalityDTO.from_entity(created)
