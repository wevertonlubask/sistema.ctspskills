"""Generate ranking use case."""

from datetime import date
from uuid import UUID

from src.application.analytics.dtos.chart_dto import RankingDTO, TimeSeriesDTO
from src.domain.analytics.repositories.analytics_repository import AnalyticsRepository
from src.domain.analytics.value_objects.date_range import DateRange
from src.domain.analytics.value_objects.metric_type import AggregationPeriod
from src.domain.modality.exceptions import CompetitorNotFoundException, ModalityNotFoundException
from src.domain.modality.repositories.competitor_repository import CompetitorRepository
from src.domain.modality.repositories.modality_repository import ModalityRepository


class GenerateRankingUseCase:
    """Use case for generating competitor rankings."""

    def __init__(
        self,
        analytics_repository: AnalyticsRepository,
        modality_repository: ModalityRepository,
        competitor_repository: CompetitorRepository,
    ) -> None:
        self._analytics_repository = analytics_repository
        self._modality_repository = modality_repository
        self._competitor_repository = competitor_repository

    async def execute(
        self,
        modality_id: UUID,
        start_date: date | None = None,
        end_date: date | None = None,
        limit: int = 50,
    ) -> RankingDTO:
        """Generate ranking for a modality.

        Args:
            modality_id: Modality UUID.
            start_date: Optional start date filter.
            end_date: Optional end date filter.
            limit: Maximum entries to return.

        Returns:
            RankingDTO with sorted competitor entries.

        Raises:
            ModalityNotFoundException: If modality not found.
        """
        # Validate modality exists
        modality = await self._modality_repository.get_by_id(modality_id)
        if not modality:
            raise ModalityNotFoundException(str(modality_id))

        # Build date range if provided
        date_range = None
        if start_date and end_date:
            date_range = DateRange(start_date=start_date, end_date=end_date)

        # Get ranking
        ranking = await self._analytics_repository.get_ranking(
            modality_id=modality_id,
            date_range=date_range,
            limit=limit,
        )

        return RankingDTO.from_domain(ranking)

    async def get_position_history(
        self,
        competitor_id: UUID,
        modality_id: UUID,
        start_date: date,
        end_date: date,
        period: AggregationPeriod = AggregationPeriod.MONTHLY,
    ) -> TimeSeriesDTO:
        """Get ranking position history for a competitor.

        Args:
            competitor_id: Competitor UUID.
            modality_id: Modality UUID.
            start_date: Start date.
            end_date: End date.
            period: Aggregation period.

        Returns:
            TimeSeriesDTO with position history.

        Raises:
            CompetitorNotFoundException: If competitor not found.
            ModalityNotFoundException: If modality not found.
        """
        # Validate competitor exists
        competitor = await self._competitor_repository.get_by_id(competitor_id)
        if not competitor:
            raise CompetitorNotFoundException(str(competitor_id))

        # Validate modality exists
        modality = await self._modality_repository.get_by_id(modality_id)
        if not modality:
            raise ModalityNotFoundException(str(modality_id))

        date_range = DateRange(start_date=start_date, end_date=end_date)

        # Get position history
        series = await self._analytics_repository.get_competitor_ranking_history(
            competitor_id=competitor_id,
            modality_id=modality_id,
            date_range=date_range,
            period=period,
        )

        return TimeSeriesDTO.from_domain(series)
