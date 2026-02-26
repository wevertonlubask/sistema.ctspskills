"""Register training use case."""

from uuid import UUID

from src.application.training.dtos.training_dto import RegisterTrainingDTO, TrainingDTO
from src.domain.modality.repositories.competitor_repository import CompetitorRepository
from src.domain.modality.repositories.enrollment_repository import EnrollmentRepository
from src.domain.training.entities.training_session import TrainingSession
from src.domain.training.repositories.training_repository import TrainingRepository
from src.domain.training.services.training_validation_service import TrainingValidationService
from src.domain.training.value_objects.training_hours import TrainingHours


class RegisterTrainingUseCase:
    """Use case for registering a training session.

    This use case allows competitors to register their training hours.

    Business Rules:
    - RN01: Competitor must be enrolled in the modality
    - RN04: Maximum 12 hours per day
    """

    def __init__(
        self,
        training_repository: TrainingRepository,
        enrollment_repository: EnrollmentRepository,
        competitor_repository: CompetitorRepository,
    ) -> None:
        self._training_repository = training_repository
        self._enrollment_repository = enrollment_repository
        self._competitor_repository = competitor_repository
        self._validation_service = TrainingValidationService(
            training_repository=training_repository,
            enrollment_repository=enrollment_repository,
        )

    async def execute(
        self,
        competitor_id: UUID,
        dto: RegisterTrainingDTO,
    ) -> TrainingDTO:
        """Register a training session.

        Args:
            competitor_id: ID of the competitor registering the training.
            dto: Training registration data.

        Returns:
            Created training session DTO.

        Raises:
            CompetitorNotEnrolledException: If competitor is not enrolled.
            MaxDailyHoursExceededException: If daily limit exceeded.
            InvalidTrainingDateException: If date is invalid.
        """
        # Create training hours value object (validates max 12h)
        hours = TrainingHours(dto.hours)

        # Validate competitor can register training (RN01, RN04)
        enrollment_id = await self._validation_service.validate_can_register_training(
            competitor_id=competitor_id,
            modality_id=dto.modality_id,
            training_date=dto.training_date,
            hours=hours,
        )

        # Create training session
        training = TrainingSession(
            competitor_id=competitor_id,
            modality_id=dto.modality_id,
            enrollment_id=enrollment_id,
            training_date=dto.training_date,
            hours=hours,
            training_type=dto.training_type,
            location=dto.location,
            description=dto.description,
        )

        # Save and return
        created = await self._training_repository.create(training)
        return TrainingDTO.from_entity(created)
