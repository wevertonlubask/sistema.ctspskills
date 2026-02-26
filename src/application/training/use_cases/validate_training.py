"""Validate training use case."""

from uuid import UUID

from src.application.training.dtos.training_dto import TrainingDTO, ValidateTrainingDTO
from src.domain.modality.repositories.enrollment_repository import EnrollmentRepository
from src.domain.training.exceptions import TrainingNotFoundException
from src.domain.training.repositories.training_repository import TrainingRepository
from src.domain.training.services.training_validation_service import TrainingValidationService
from src.shared.constants.enums import UserRole
from src.shared.exceptions import ValidationException


class ValidateTrainingUseCase:
    """Use case for validating a training session.

    This use case allows evaluators to approve or reject training sessions.

    Business Rules:
    - RN07: Only assigned evaluators can validate their competitors' training
    - RN11: Training must be validated to count in statistics
    """

    def __init__(
        self,
        training_repository: TrainingRepository,
        enrollment_repository: EnrollmentRepository,
    ) -> None:
        self._training_repository = training_repository
        self._enrollment_repository = enrollment_repository
        self._validation_service = TrainingValidationService(
            training_repository=training_repository,
            enrollment_repository=enrollment_repository,
        )

    async def execute(
        self,
        training_id: UUID,
        evaluator_id: UUID,
        evaluator_role: UserRole,
        dto: ValidateTrainingDTO,
    ) -> TrainingDTO:
        """Validate a training session.

        Args:
            training_id: ID of the training to validate.
            evaluator_id: ID of the evaluator performing validation.
            evaluator_role: Role of the evaluator.
            dto: Validation data (approved/rejected with reason).

        Returns:
            Updated training session DTO.

        Raises:
            TrainingNotFoundException: If training not found.
            EvaluatorNotAssignedException: If evaluator not assigned (for non-admins).
        """
        # Get training
        training = await self._training_repository.get_by_id(training_id)
        if not training:
            raise TrainingNotFoundException(str(training_id))

        # Super admins can validate any training, evaluators only their assigned ones
        if evaluator_role != UserRole.SUPER_ADMIN:
            await self._validation_service.validate_evaluator_can_validate(
                evaluator_id=evaluator_id,
                competitor_id=training.competitor_id,
                modality_id=training.modality_id,
            )

        # Approve or reject
        if dto.approved:
            training.approve(evaluator_id)
        else:
            if not dto.rejection_reason:
                raise ValidationException(
                    message="Rejection reason is required when rejecting training",
                    errors=[
                        {"field": "rejection_reason", "message": "Rejection reason is required"}
                    ],
                )
            training.reject(evaluator_id, dto.rejection_reason)

        # Save and return
        updated = await self._training_repository.update(training)
        return TrainingDTO.from_entity(updated)
