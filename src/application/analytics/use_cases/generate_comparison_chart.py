"""Generate comparison chart use case."""

from datetime import date
from uuid import UUID

from src.application.analytics.dtos.chart_dto import EvolutionComparisonDTO, TimeSeriesDTO
from src.domain.analytics.repositories.analytics_repository import AnalyticsRepository
from src.domain.analytics.value_objects.date_range import DateRange


class GenerateComparisonChartUseCase:
    """Use case for generating grade comparison chart between competitors."""

    def __init__(
        self,
        analytics_repository: AnalyticsRepository,
    ) -> None:
        self._analytics_repository = analytics_repository

    async def execute(
        self,
        competitor_ids: list[UUID],
        start_date: date | None = None,
        end_date: date | None = None,
        modality_id: UUID | None = None,
    ) -> EvolutionComparisonDTO:
        """Generate grade comparison chart data.

        Args:
            competitor_ids: List of competitor UUIDs to compare.
            start_date: Start date for the range.
            end_date: End date for the range.
            modality_id: Optional modality filter.

        Returns:
            EvolutionComparisonDTO with chart data for all competitors.
        """
        # Create date range
        if start_date and end_date:
            date_range = DateRange(start_date=start_date, end_date=end_date)
        else:
            date_range = DateRange.last_365_days()

        # Get comparison data
        series_list = await self._analytics_repository.get_grades_comparison(
            competitor_ids=competitor_ids,
            date_range=date_range,
            modality_id=modality_id,
        )

        return EvolutionComparisonDTO(
            series=[TimeSeriesDTO.from_domain(s) for s in series_list],
            competitor_ids=[str(c) for c in competitor_ids],
            modality_id=str(modality_id) if modality_id else None,
        )
