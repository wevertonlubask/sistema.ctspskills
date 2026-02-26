"""Add competence to modality use case."""

from uuid import UUID

from src.application.modality.dtos.competence_dto import CompetenceDTO, CreateCompetenceDTO
from src.domain.modality.entities.competence import Competence
from src.domain.modality.exceptions import ModalityNotFoundException
from src.domain.modality.repositories.competence_repository import CompetenceRepository
from src.domain.modality.repositories.modality_repository import ModalityRepository
from src.shared.exceptions import ConflictException


class AddCompetenceUseCase:
    """Use case for adding a competence to a modality."""

    def __init__(
        self,
        modality_repository: ModalityRepository,
        competence_repository: CompetenceRepository,
    ) -> None:
        self._modality_repository = modality_repository
        self._competence_repository = competence_repository

    async def execute(
        self,
        modality_id: UUID,
        dto: CreateCompetenceDTO,
    ) -> CompetenceDTO:
        """Add a competence to a modality.

        Args:
            modality_id: Modality identifier.
            dto: Competence creation data.

        Returns:
            Created competence DTO.

        Raises:
            ModalityNotFoundException: If modality not found.
            ConflictException: If competence name already exists in modality.
        """
        # Verify modality exists
        if not await self._modality_repository.exists(modality_id):
            raise ModalityNotFoundException(identifier=str(modality_id))

        # Check if competence name already exists in modality
        existing = await self._competence_repository.get_by_name_and_modality(
            name=dto.name,
            modality_id=modality_id,
        )
        if existing:
            raise ConflictException(
                message=f"Competence '{dto.name}' already exists in this modality",
                resource_type="Competence",
            )

        # Create competence entity
        competence = Competence(
            modality_id=modality_id,
            name=dto.name,
            description=dto.description,
            weight=dto.weight,
            max_score=dto.max_score,
        )

        # Persist
        created = await self._competence_repository.add(competence)

        return CompetenceDTO.from_entity(created)
