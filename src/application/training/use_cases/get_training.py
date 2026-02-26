"""Get training use case."""

from uuid import UUID

from src.application.training.dtos.training_dto import TrainingDTO
from src.domain.training.exceptions import TrainingNotFoundException
from src.domain.training.repositories.training_repository import TrainingRepository


class GetTrainingUseCase:
    """Use case for getting a single training session."""

    def __init__(self, training_repository: TrainingRepository) -> None:
        self._training_repository = training_repository

    async def execute(self, training_id: UUID) -> TrainingDTO:
        """Get a training session by ID.

        Args:
            training_id: Training session ID.

        Returns:
            Training session DTO.

        Raises:
            TrainingNotFoundException: If training not found.
        """
        training = await self._training_repository.get_by_id(training_id)
        if not training:
            raise TrainingNotFoundException(str(training_id))

        return TrainingDTO.from_entity(training)
