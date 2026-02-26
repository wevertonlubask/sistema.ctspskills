"""Get training statistics use case."""

from uuid import UUID

from src.application.training.dtos.training_dto import TrainingStatisticsDTO
from src.domain.training.repositories.training_repository import TrainingRepository
from src.shared.constants.enums import TrainingStatus, TrainingType


class GetTrainingStatisticsUseCase:
    """Use case for getting training statistics.

    Returns totalized training hours and session counts for a competitor.
    """

    def __init__(self, training_repository: TrainingRepository) -> None:
        self._training_repository = training_repository

    async def execute(
        self,
        competitor_id: UUID,
        modality_id: UUID | None = None,
    ) -> TrainingStatisticsDTO:
        """Get training statistics for a competitor.

        Args:
            competitor_id: Competitor ID.
            modality_id: Optional modality filter.

        Returns:
            Training statistics DTO.
        """
        # Get approved hours by type (RN11: only approved count)
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
        total_sessions = await self._training_repository.count(
            competitor_id=competitor_id,
            modality_id=modality_id,
        )
        pending_sessions = await self._training_repository.count(
            competitor_id=competitor_id,
            modality_id=modality_id,
            status=TrainingStatus.PENDING,
        )
        approved_sessions = await self._training_repository.count(
            competitor_id=competitor_id,
            modality_id=modality_id,
            status=TrainingStatus.APPROVED,
        )
        rejected_sessions = await self._training_repository.count(
            competitor_id=competitor_id,
            modality_id=modality_id,
            status=TrainingStatus.REJECTED,
        )

        return TrainingStatisticsDTO(
            competitor_id=competitor_id,
            modality_id=modality_id,
            senai_hours=senai_hours,
            external_hours=external_hours,
            total_approved_hours=senai_hours + external_hours,
            total_sessions=total_sessions,
            pending_sessions=pending_sessions,
            approved_sessions=approved_sessions,
            rejected_sessions=rejected_sessions,
        )
