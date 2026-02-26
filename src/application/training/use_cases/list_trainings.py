"""List trainings use case."""

from datetime import date
from uuid import UUID

from src.application.training.dtos.training_dto import TrainingDTO, TrainingListDTO
from src.domain.training.repositories.training_repository import TrainingRepository
from src.shared.constants.enums import TrainingStatus


class ListTrainingsUseCase:
    """Use case for listing training sessions."""

    def __init__(self, training_repository: TrainingRepository) -> None:
        self._training_repository = training_repository

    async def execute(
        self,
        competitor_id: UUID | None = None,
        modality_id: UUID | None = None,
        evaluator_id: UUID | None = None,
        status: TrainingStatus | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> TrainingListDTO:
        """List training sessions with filters.

        Args:
            competitor_id: Filter by competitor.
            modality_id: Filter by modality.
            evaluator_id: Filter by assigned evaluator.
            status: Filter by validation status.
            start_date: Filter from this date.
            end_date: Filter until this date.
            skip: Pagination offset.
            limit: Pagination limit.

        Returns:
            Training list DTO with pagination.
        """
        if evaluator_id:
            # Get trainings for evaluator's assigned competitors
            trainings = await self._training_repository.get_by_evaluator(
                evaluator_id=evaluator_id,
                skip=skip,
                limit=limit,
                status=status,
            )
            # Count is approximate for evaluator filter
            total = len(trainings) + skip
        elif competitor_id:
            trainings = await self._training_repository.get_by_competitor(
                competitor_id=competitor_id,
                skip=skip,
                limit=limit,
                status=status,
                modality_id=modality_id,
                start_date=start_date,
                end_date=end_date,
            )
            total = await self._training_repository.count(
                competitor_id=competitor_id,
                modality_id=modality_id,
                status=status,
            )
        elif modality_id:
            trainings = await self._training_repository.get_by_modality(
                modality_id=modality_id,
                skip=skip,
                limit=limit,
                status=status,
            )
            total = await self._training_repository.count(
                modality_id=modality_id,
                status=status,
            )
        else:
            # Get all trainings (for super_admin)
            trainings = await self._training_repository.get_all(
                skip=skip,
                limit=limit,
                status=status,
                start_date=start_date,
                end_date=end_date,
            )
            total = await self._training_repository.count_all(status=status)

        return TrainingListDTO(
            trainings=[TrainingDTO.from_entity(t) for t in trainings],
            total=total,
            skip=skip,
            limit=limit,
        )
