"""List exams use case."""

from datetime import date
from uuid import UUID

from src.application.assessment.dtos.exam_dto import ExamDTO, ExamListDTO
from src.domain.assessment.repositories.exam_repository import ExamRepository


class ListExamsUseCase:
    """Use case for listing exams.

    This use case allows users to list and filter exams.
    """

    def __init__(
        self,
        exam_repository: ExamRepository,
    ) -> None:
        self._exam_repository = exam_repository

    async def execute(
        self,
        modality_id: UUID | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        active_only: bool = True,
        skip: int = 0,
        limit: int = 100,
    ) -> ExamListDTO:
        """List exams with optional filters.

        Args:
            modality_id: Optional modality filter.
            start_date: Optional start date filter.
            end_date: Optional end date filter.
            active_only: Whether to return only active exams.
            skip: Number of records to skip.
            limit: Maximum records to return.

        Returns:
            ExamListDTO with paginated results.
        """
        # Use date range query if dates provided
        if start_date and end_date:
            exams = await self._exam_repository.get_by_date_range(
                modality_id=modality_id,
                start_date=start_date,
                end_date=end_date,
                skip=skip,
                limit=limit,
            )
        elif modality_id:
            exams = await self._exam_repository.get_by_modality(
                modality_id=modality_id,
                active_only=active_only,
                skip=skip,
                limit=limit,
            )
        else:
            # Get all exams without modality filter
            exams = await self._exam_repository.get_all(
                active_only=active_only,
                skip=skip,
                limit=limit,
            )

        # Get total count
        total = await self._exam_repository.count(
            modality_id=modality_id,
            active_only=active_only,
        )

        return ExamListDTO(
            exams=[ExamDTO.from_entity(e) for e in exams],
            total=total,
            skip=skip,
            limit=limit,
        )

    async def by_creator(
        self,
        creator_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> ExamListDTO:
        """List exams by creator.

        Args:
            creator_id: ID of the user who created the exams.
            skip: Number of records to skip.
            limit: Maximum records to return.

        Returns:
            ExamListDTO with paginated results.
        """
        exams = await self._exam_repository.get_by_creator(
            creator_id=creator_id,
            skip=skip,
            limit=limit,
        )

        return ExamListDTO(
            exams=[ExamDTO.from_entity(e) for e in exams],
            total=len(exams),  # Approximation - ideally we'd have a count method
            skip=skip,
            limit=limit,
        )
