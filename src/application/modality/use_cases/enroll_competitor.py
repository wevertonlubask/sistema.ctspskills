"""Enroll competitor use case."""

from uuid import UUID

from src.application.modality.dtos.enrollment_dto import EnrollCompetitorDTO, EnrollmentDTO
from src.domain.modality.exceptions import (
    CompetitorNotFoundException,
    ModalityNotFoundException,
)
from src.domain.modality.repositories.competitor_repository import CompetitorRepository
from src.domain.modality.repositories.enrollment_repository import EnrollmentRepository
from src.domain.modality.repositories.modality_repository import ModalityRepository
from src.domain.modality.services.enrollment_service import EnrollmentService


class EnrollCompetitorUseCase:
    """Use case for enrolling a competitor in a modality."""

    def __init__(
        self,
        modality_repository: ModalityRepository,
        competitor_repository: CompetitorRepository,
        enrollment_repository: EnrollmentRepository,
    ) -> None:
        self._modality_repository = modality_repository
        self._competitor_repository = competitor_repository
        self._enrollment_service = EnrollmentService(enrollment_repository)

    async def execute(
        self,
        modality_id: UUID,
        dto: EnrollCompetitorDTO,
    ) -> EnrollmentDTO:
        """Enroll a competitor in a modality.

        Args:
            modality_id: Modality identifier.
            dto: Enrollment data.

        Returns:
            Created enrollment DTO.

        Raises:
            ModalityNotFoundException: If modality not found.
            CompetitorNotFoundException: If competitor not found.
            CompetitorAlreadyEnrolledException: If already enrolled.
        """
        # Get modality
        modality = await self._modality_repository.get_by_id(modality_id)
        if not modality:
            raise ModalityNotFoundException(identifier=str(modality_id))

        # Get competitor
        competitor = await self._competitor_repository.get_by_id(dto.competitor_id)
        if not competitor:
            raise CompetitorNotFoundException(identifier=str(dto.competitor_id))

        # Enroll using domain service
        enrollment = await self._enrollment_service.enroll_competitor(
            competitor=competitor,
            modality=modality,
            evaluator_id=dto.evaluator_id,
        )

        return EnrollmentDTO.from_entity(enrollment)
