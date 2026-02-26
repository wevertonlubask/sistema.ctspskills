"""Get competitor summary use case."""

from uuid import UUID

from src.application.analytics.dtos.chart_dto import CompetitorSummaryDTO
from src.domain.analytics.repositories.analytics_repository import AnalyticsRepository
from src.domain.modality.exceptions import CompetitorNotFoundException, ModalityNotFoundException
from src.domain.modality.repositories.competitor_repository import CompetitorRepository
from src.domain.modality.repositories.modality_repository import ModalityRepository


class GetCompetitorSummaryUseCase:
    """Use case for getting competitor dashboard summary."""

    def __init__(
        self,
        analytics_repository: AnalyticsRepository,
        competitor_repository: CompetitorRepository,
        modality_repository: ModalityRepository,
    ) -> None:
        self._analytics_repository = analytics_repository
        self._competitor_repository = competitor_repository
        self._modality_repository = modality_repository

    async def execute(
        self,
        competitor_id: UUID,
        modality_id: UUID | None = None,
    ) -> CompetitorSummaryDTO:
        """Get comprehensive summary for a competitor.

        Args:
            competitor_id: Competitor UUID.
            modality_id: Optional modality filter.

        Returns:
            CompetitorSummaryDTO with all summary metrics.

        Raises:
            CompetitorNotFoundException: If competitor not found.
            ModalityNotFoundException: If modality_id provided but not found.
        """
        # Validate competitor exists
        competitor = await self._competitor_repository.get_by_id(competitor_id)
        if not competitor:
            raise CompetitorNotFoundException(str(competitor_id))

        # Validate modality if provided
        if modality_id:
            modality = await self._modality_repository.get_by_id(modality_id)
            if not modality:
                raise ModalityNotFoundException(str(modality_id))

        # Get summary data from repository
        summary_data = await self._analytics_repository.get_competitor_summary(
            competitor_id=competitor_id,
            modality_id=modality_id,
        )

        return CompetitorSummaryDTO(
            competitor_id=str(competitor_id),
            modality_id=str(modality_id) if modality_id else None,
            grades_average=summary_data.get("grades_average", 0.0),
            grades_total=summary_data.get("grades_total", 0),
            grades_max=summary_data.get("grades_max", 0.0),
            grades_min=summary_data.get("grades_min", 0.0),
            training_total_hours=summary_data.get("training_total_hours", 0.0),
            training_total_sessions=summary_data.get("training_total_sessions", 0),
            exams_participated=summary_data.get("exams_participated", 0),
        )
