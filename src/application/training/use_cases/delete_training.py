"""Delete training use case."""

from uuid import UUID

from src.domain.training.exceptions import (
    TrainingAlreadyValidatedException,
    TrainingNotFoundException,
)
from src.domain.training.repositories.training_repository import TrainingRepository
from src.shared.constants.enums import UserRole


class DeleteTrainingUseCase:
    """Use case for deleting a training session.

    Only pending trainings can be deleted by the competitor.
    Admins can delete any training.
    """

    def __init__(self, training_repository: TrainingRepository) -> None:
        self._training_repository = training_repository

    async def execute(
        self,
        training_id: UUID,
        user_id: UUID,
        user_role: UserRole,
        is_own_training: bool = False,
    ) -> bool:
        """Delete a training session.

        Args:
            training_id: Training session ID.
            user_id: ID of the user requesting deletion.
            user_role: Role of the user.
            is_own_training: Whether user is deleting their own training.

        Returns:
            True if deleted.

        Raises:
            TrainingNotFoundException: If training not found.
            TrainingAlreadyValidatedException: If training was already validated.
        """
        training = await self._training_repository.get_by_id(training_id)
        if not training:
            raise TrainingNotFoundException(str(training_id))

        # Super admins and evaluators can delete any training
        if user_role in (UserRole.SUPER_ADMIN, UserRole.EVALUATOR):
            return await self._training_repository.delete(training_id)

        # Competitors can only delete their own pending trainings
        if is_own_training:
            if not training.is_pending:
                raise TrainingAlreadyValidatedException()
            return await self._training_repository.delete(training_id)

        raise PermissionError("You don't have permission to delete this training")
