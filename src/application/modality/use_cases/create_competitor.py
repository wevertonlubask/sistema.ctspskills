"""Create competitor use case."""


from src.application.modality.dtos.competitor_dto import CompetitorDTO, CreateCompetitorDTO
from src.domain.identity.exceptions import UserNotFoundException
from src.domain.identity.repositories.user_repository import UserRepository
from src.domain.modality.entities.competitor import Competitor
from src.domain.modality.repositories.competitor_repository import CompetitorRepository
from src.shared.exceptions import ConflictException


class CreateCompetitorUseCase:
    """Use case for creating a competitor profile."""

    def __init__(
        self,
        competitor_repository: CompetitorRepository,
        user_repository: UserRepository,
    ) -> None:
        self._competitor_repository = competitor_repository
        self._user_repository = user_repository

    async def execute(self, dto: CreateCompetitorDTO) -> CompetitorDTO:
        """Create a competitor profile for a user.

        Args:
            dto: Competitor creation data.

        Returns:
            Created competitor DTO.

        Raises:
            UserNotFoundException: If user not found.
            ConflictException: If competitor profile already exists.
        """
        # Verify user exists
        user = await self._user_repository.get_by_id(dto.user_id)
        if not user:
            raise UserNotFoundException(identifier=str(dto.user_id))

        # Check if competitor profile already exists
        existing = await self._competitor_repository.get_by_user_id(dto.user_id)
        if existing:
            raise ConflictException(
                message="Competitor profile already exists for this user",
                resource_type="Competitor",
            )

        # Create competitor entity
        competitor = Competitor(
            user_id=dto.user_id,
            full_name=dto.full_name,
            birth_date=dto.birth_date,
            document_number=dto.document_number,
            phone=dto.phone,
            emergency_contact=dto.emergency_contact,
            emergency_phone=dto.emergency_phone,
            notes=dto.notes,
        )

        # Persist
        created = await self._competitor_repository.add(competitor)

        return CompetitorDTO.from_entity(created)
