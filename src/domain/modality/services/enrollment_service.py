"""Enrollment domain service."""

from uuid import UUID

from src.domain.modality.entities.competitor import Competitor
from src.domain.modality.entities.enrollment import Enrollment, EnrollmentStatus
from src.domain.modality.entities.modality import Modality
from src.domain.modality.exceptions import (
    CompetitorAlreadyEnrolledException,
    CompetitorNotEnrolledException,
    EvaluatorNotAssignedException,
)
from src.domain.modality.repositories.enrollment_repository import EnrollmentRepository


class EnrollmentService:
    """Domain service for enrollment business rules.

    Handles enrollment logic including:
    - RN01: Competitor can only register trainings for enrolled modalities
    - RN02: Only assigned evaluators can evaluate competitors
    - RN07: Evaluator can only manage competitors under their responsibility
    """

    def __init__(self, enrollment_repository: EnrollmentRepository) -> None:
        self._enrollment_repository = enrollment_repository

    async def enroll_competitor(
        self,
        competitor: Competitor,
        modality: Modality,
        evaluator_id: UUID | None = None,
    ) -> Enrollment:
        """Enroll a competitor in a modality.

        Args:
            competitor: Competitor to enroll.
            modality: Modality to enroll in.
            evaluator_id: Optional evaluator to assign.

        Returns:
            Created enrollment.

        Raises:
            CompetitorAlreadyEnrolledException: If already enrolled.
        """
        # Check if already enrolled
        if await self._enrollment_repository.is_enrolled(competitor.id, modality.id):
            raise CompetitorAlreadyEnrolledException(competitor.id, modality.id)

        enrollment = Enrollment(
            competitor_id=competitor.id,
            modality_id=modality.id,
            evaluator_id=evaluator_id,
            status=EnrollmentStatus.ACTIVE,
        )

        return await self._enrollment_repository.add(enrollment)

    async def validate_competitor_can_train(
        self,
        competitor_id: UUID,
        modality_id: UUID,
    ) -> bool:
        """Validate if competitor can register training for modality (RN01).

        Args:
            competitor_id: Competitor ID.
            modality_id: Modality ID.

        Returns:
            True if competitor can train.

        Raises:
            CompetitorNotEnrolledException: If not enrolled.
        """
        is_enrolled = await self._enrollment_repository.is_enrolled(competitor_id, modality_id)

        if not is_enrolled:
            raise CompetitorNotEnrolledException(competitor_id, modality_id)

        return True

    async def validate_evaluator_can_evaluate(
        self,
        evaluator_id: UUID,
        modality_id: UUID,
    ) -> bool:
        """Validate if evaluator can evaluate competitors in modality (RN02).

        Args:
            evaluator_id: Evaluator user ID.
            modality_id: Modality ID.

        Returns:
            True if evaluator can evaluate.

        Raises:
            EvaluatorNotAssignedException: If not assigned to modality.
        """
        is_assigned = await self._enrollment_repository.is_evaluator_assigned(
            evaluator_id, modality_id
        )

        if not is_assigned:
            raise EvaluatorNotAssignedException(evaluator_id, modality_id)

        return True

    async def validate_evaluator_manages_competitor(
        self,
        evaluator_id: UUID,
        competitor_id: UUID,
        modality_id: UUID,
    ) -> bool:
        """Validate if evaluator manages the competitor in modality (RN07).

        Args:
            evaluator_id: Evaluator user ID.
            competitor_id: Competitor ID.
            modality_id: Modality ID.

        Returns:
            True if evaluator manages the competitor.

        Raises:
            EvaluatorNotAssignedException: If evaluator doesn't manage the competitor.
        """
        enrollment = await self._enrollment_repository.get_by_competitor_and_modality(
            competitor_id, modality_id
        )

        if not enrollment or enrollment.evaluator_id != evaluator_id:
            raise EvaluatorNotAssignedException(evaluator_id, modality_id)

        return True

    async def assign_evaluator_to_enrollment(
        self,
        enrollment: Enrollment,
        evaluator_id: UUID,
    ) -> Enrollment:
        """Assign an evaluator to an enrollment.

        Args:
            enrollment: Enrollment to update.
            evaluator_id: Evaluator to assign.

        Returns:
            Updated enrollment.
        """
        enrollment.assign_evaluator(evaluator_id)
        return await self._enrollment_repository.update(enrollment)

    async def get_evaluator_competitors(
        self,
        evaluator_id: UUID,
        modality_id: UUID | None = None,
    ) -> list[Enrollment]:
        """Get all enrollments assigned to an evaluator (RN07).

        Args:
            evaluator_id: Evaluator user ID.
            modality_id: Optional modality filter.

        Returns:
            List of enrollments.
        """
        enrollments = await self._enrollment_repository.get_by_evaluator(
            evaluator_id, status=EnrollmentStatus.ACTIVE
        )

        if modality_id:
            enrollments = [e for e in enrollments if e.modality_id == modality_id]

        return enrollments
