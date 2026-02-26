"""Training validation domain service."""

from datetime import date
from uuid import UUID

from src.domain.modality.repositories.enrollment_repository import EnrollmentRepository
from src.domain.training.exceptions import (
    CompetitorNotEnrolledException,
    EvaluatorNotAssignedException,
    InvalidTrainingDateException,
    MaxDailyHoursExceededException,
)
from src.domain.training.repositories.training_repository import TrainingRepository
from src.domain.training.value_objects.training_hours import TrainingHours
from src.shared.constants.enums import TrainingStatus, TrainingType


class TrainingValidationService:
    """Domain service for training validation rules.

    This service encapsulates business rules related to training registration
    and validation that span multiple aggregates.

    Business Rules:
    - RN01: Competitors can only register training for modalities they're enrolled in
    - RN04: Maximum 12 hours of training per day
    - RN07: Only assigned evaluators can validate training for their competitors
    - RN11: Training must be validated to count in statistics
    """

    def __init__(
        self,
        training_repository: TrainingRepository,
        enrollment_repository: EnrollmentRepository,
    ) -> None:
        """Initialize the service.

        Args:
            training_repository: Repository for training sessions.
            enrollment_repository: Repository for enrollments.
        """
        self._training_repository = training_repository
        self._enrollment_repository = enrollment_repository

    async def validate_can_register_training(
        self,
        competitor_id: UUID,
        modality_id: UUID,
        training_date: date,
        hours: TrainingHours,
        exclude_training_id: UUID | None = None,
    ) -> UUID:
        """Validate if a competitor can register training.

        Args:
            competitor_id: Competitor ID.
            modality_id: Modality ID.
            training_date: Date of training.
            hours: Training hours.
            exclude_training_id: Training ID to exclude (for updates).

        Returns:
            Enrollment ID if validation passes.

        Raises:
            CompetitorNotEnrolledException: If competitor is not enrolled (RN01).
            MaxDailyHoursExceededException: If daily hours would exceed limit (RN04).
            InvalidTrainingDateException: If training date is in the future.
        """
        # RN01: Check if competitor is enrolled in the modality
        enrollment = await self._enrollment_repository.get_active_enrollment(
            competitor_id=competitor_id,
            modality_id=modality_id,
        )
        if not enrollment:
            raise CompetitorNotEnrolledException(
                competitor_id=str(competitor_id),
                modality_id=str(modality_id),
            )

        # Validate training date is not in the future
        if training_date > date.today():
            raise InvalidTrainingDateException("Training date cannot be in the future")

        # RN04: Check daily hours limit
        current_daily_hours = await self._training_repository.get_daily_hours(
            competitor_id=competitor_id,
            training_date=training_date,
            exclude_training_id=exclude_training_id,
        )
        total_hours = current_daily_hours + hours.value
        if total_hours > TrainingHours.MAX_HOURS_PER_DAY:
            raise MaxDailyHoursExceededException(
                date=str(training_date),
                current_hours=current_daily_hours,
                max_hours=TrainingHours.MAX_HOURS_PER_DAY,
            )

        return enrollment.id

    async def validate_evaluator_can_validate(
        self,
        evaluator_id: UUID,
        competitor_id: UUID,
        modality_id: UUID,
    ) -> bool:
        """Validate if an evaluator can validate a competitor's training.

        RN07: Only assigned evaluators can validate training.

        Args:
            evaluator_id: Evaluator user ID.
            competitor_id: Competitor ID.
            modality_id: Modality ID.

        Returns:
            True if evaluator can validate.

        Raises:
            EvaluatorNotAssignedException: If evaluator is not assigned.
        """
        enrollment = await self._enrollment_repository.get_active_enrollment(
            competitor_id=competitor_id,
            modality_id=modality_id,
        )
        if not enrollment:
            raise CompetitorNotEnrolledException(
                competitor_id=str(competitor_id),
                modality_id=str(modality_id),
            )

        if enrollment.evaluator_id != evaluator_id:
            raise EvaluatorNotAssignedException()

        return True

    async def get_daily_hours_remaining(
        self,
        competitor_id: UUID,
        training_date: date,
    ) -> float:
        """Get remaining hours a competitor can register for a given date.

        Args:
            competitor_id: Competitor ID.
            training_date: Date to check.

        Returns:
            Remaining hours available.
        """
        current_hours = await self._training_repository.get_daily_hours(
            competitor_id=competitor_id,
            training_date=training_date,
        )
        remaining = TrainingHours.MAX_HOURS_PER_DAY - current_hours
        return max(0, remaining)

    async def get_training_statistics(
        self,
        competitor_id: UUID,
        modality_id: UUID | None = None,
    ) -> dict:
        """Get training statistics for a competitor.

        Args:
            competitor_id: Competitor ID.
            modality_id: Optional modality filter.

        Returns:
            Dictionary with training statistics.
        """
        # Get approved hours by type
        senai_hours = await self._training_repository.get_total_hours(
            competitor_id=competitor_id,
            modality_id=modality_id,
            training_type=TrainingType.SENAI,
            approved_only=True,
        )
        external_hours = await self._training_repository.get_total_hours(
            competitor_id=competitor_id,
            modality_id=modality_id,
            training_type=TrainingType.EXTERNAL,
            approved_only=True,
        )

        # Get counts by status
        total_count = await self._training_repository.count(
            competitor_id=competitor_id,
            modality_id=modality_id,
        )
        pending_count = await self._training_repository.count(
            competitor_id=competitor_id,
            modality_id=modality_id,
            status=TrainingStatus.PENDING,
        )
        approved_count = await self._training_repository.count(
            competitor_id=competitor_id,
            modality_id=modality_id,
            status=TrainingStatus.APPROVED,
        )
        rejected_count = await self._training_repository.count(
            competitor_id=competitor_id,
            modality_id=modality_id,
            status=TrainingStatus.REJECTED,
        )

        return {
            "senai_hours": senai_hours,
            "external_hours": external_hours,
            "total_approved_hours": senai_hours + external_hours,
            "total_sessions": total_count,
            "pending_sessions": pending_count,
            "approved_sessions": approved_count,
            "rejected_sessions": rejected_count,
        }
