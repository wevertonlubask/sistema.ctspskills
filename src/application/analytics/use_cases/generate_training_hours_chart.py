"""Generate training hours chart use case."""

from datetime import date
from uuid import UUID

from src.application.analytics.dtos.chart_dto import (
    TimeSeriesDTO,
    TrainingHoursChartDTO,
    TrainingHoursSummaryDTO,
)
from src.domain.analytics.repositories.analytics_repository import AnalyticsRepository
from src.domain.analytics.value_objects.date_range import DateRange
from src.domain.analytics.value_objects.metric_type import AggregationPeriod
from src.domain.modality.exceptions import CompetitorNotFoundException
from src.domain.modality.repositories.competitor_repository import CompetitorRepository


class GenerateTrainingHoursChartUseCase:
    """Use case for generating training hours chart (SENAI vs External)."""

    def __init__(
        self,
        analytics_repository: AnalyticsRepository,
        competitor_repository: CompetitorRepository,
    ) -> None:
        self._analytics_repository = analytics_repository
        self._competitor_repository = competitor_repository

    async def execute(
        self,
        competitor_id: UUID,
        start_date: date | None = None,
        end_date: date | None = None,
        period: str = "monthly",
        modality_id: UUID | None = None,
    ) -> TrainingHoursChartDTO:
        """Generate training hours chart data.

        Args:
            competitor_id: Competitor UUID.
            start_date: Start date for the range.
            end_date: End date for the range.
            period: Aggregation period (daily, weekly, monthly, yearly).
            modality_id: Optional modality filter.

        Returns:
            TrainingHoursChartDTO with SENAI and External series.

        Raises:
            CompetitorNotFoundException: If competitor not found.
        """
        # Validate competitor exists
        competitor = await self._competitor_repository.get_by_id(competitor_id)
        if not competitor:
            raise CompetitorNotFoundException(str(competitor_id))

        # Create date range
        if start_date and end_date:
            date_range = DateRange(start_date=start_date, end_date=end_date)
        else:
            date_range = DateRange.last_365_days()

        # Convert period string to enum
        agg_period = AggregationPeriod(period)

        # Get evolution data
        (
            senai_series,
            external_series,
        ) = await self._analytics_repository.get_training_hours_evolution(
            competitor_id=competitor_id,
            date_range=date_range,
            period=agg_period,
            modality_id=modality_id,
        )

        # Get summary
        summary = await self._analytics_repository.get_training_hours_summary(
            competitor_id=competitor_id,
            date_range=date_range,
            modality_id=modality_id,
        )

        return TrainingHoursChartDTO(
            competitor_id=str(competitor_id),
            senai_series=TimeSeriesDTO.from_domain(senai_series),
            external_series=TimeSeriesDTO.from_domain(external_series),
            summary=TrainingHoursSummaryDTO.from_domain(summary),
        )
