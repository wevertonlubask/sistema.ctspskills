"""Analytics repository interface (CQRS read-side)."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.analytics.entities.performance_metric import (
    CompetenceMap,
    Ranking,
    TimeSeries,
    TrainingHoursSummary,
)
from src.domain.analytics.value_objects.date_range import DateRange
from src.domain.analytics.value_objects.metric_type import AggregationPeriod


class AnalyticsRepository(ABC):
    """Abstract repository for analytics queries (read-only).

    This repository follows CQRS pattern - it's optimized for
    complex read queries and aggregations, separate from the
    write-side repositories.
    """

    # ==========================================================================
    # Grade Evolution Queries
    # ==========================================================================

    @abstractmethod
    async def get_grade_evolution(
        self,
        competitor_id: UUID,
        date_range: DateRange,
        period: AggregationPeriod = AggregationPeriod.MONTHLY,
        modality_id: UUID | None = None,
        competence_id: UUID | None = None,
    ) -> TimeSeries:
        """Get grade evolution over time for a competitor.

        Args:
            competitor_id: Competitor UUID.
            date_range: Date range to query.
            period: Aggregation period.
            modality_id: Optional modality filter.
            competence_id: Optional competence filter.

        Returns:
            TimeSeries with grade averages over time.
        """
        ...

    @abstractmethod
    async def get_grades_comparison(
        self,
        competitor_ids: list[UUID],
        date_range: DateRange,
        modality_id: UUID | None = None,
    ) -> list[TimeSeries]:
        """Get grade evolution for multiple competitors (comparison).

        Args:
            competitor_ids: List of competitor UUIDs to compare.
            date_range: Date range to query.
            modality_id: Optional modality filter.

        Returns:
            List of TimeSeries, one per competitor.
        """
        ...

    # ==========================================================================
    # Training Hours Queries
    # ==========================================================================

    @abstractmethod
    async def get_training_hours_evolution(
        self,
        competitor_id: UUID,
        date_range: DateRange,
        period: AggregationPeriod = AggregationPeriod.MONTHLY,
        modality_id: UUID | None = None,
    ) -> tuple[TimeSeries, TimeSeries]:
        """Get training hours evolution (SENAI vs External).

        Args:
            competitor_id: Competitor UUID.
            date_range: Date range to query.
            period: Aggregation period.
            modality_id: Optional modality filter.

        Returns:
            Tuple of (senai_series, external_series).
        """
        ...

    @abstractmethod
    async def get_training_hours_summary(
        self,
        competitor_id: UUID,
        date_range: DateRange | None = None,
        modality_id: UUID | None = None,
    ) -> TrainingHoursSummary:
        """Get comprehensive training hours summary.

        Args:
            competitor_id: Competitor UUID.
            date_range: Optional date range filter.
            modality_id: Optional modality filter.

        Returns:
            TrainingHoursSummary with all metrics.
        """
        ...

    # ==========================================================================
    # Competence Map Queries
    # ==========================================================================

    @abstractmethod
    async def get_competence_map(
        self,
        competitor_id: UUID,
        modality_id: UUID,
        exam_id: UUID | None = None,
    ) -> CompetenceMap:
        """Get competence scores for radar chart.

        Args:
            competitor_id: Competitor UUID.
            modality_id: Modality UUID.
            exam_id: Optional specific exam filter.

        Returns:
            CompetenceMap with scores per competence.
        """
        ...

    @abstractmethod
    async def get_competence_comparison(
        self,
        competitor_ids: list[UUID],
        modality_id: UUID,
    ) -> list[CompetenceMap]:
        """Get competence maps for multiple competitors.

        Args:
            competitor_ids: List of competitor UUIDs.
            modality_id: Modality UUID.

        Returns:
            List of CompetenceMap, one per competitor.
        """
        ...

    # ==========================================================================
    # Ranking Queries
    # ==========================================================================

    @abstractmethod
    async def get_ranking(
        self,
        modality_id: UUID,
        date_range: DateRange | None = None,
        limit: int = 50,
    ) -> Ranking:
        """Get competitor ranking for a modality.

        Args:
            modality_id: Modality UUID.
            date_range: Optional date range for grades.
            limit: Maximum entries to return.

        Returns:
            Ranking with sorted entries.
        """
        ...

    @abstractmethod
    async def get_competitor_ranking_history(
        self,
        competitor_id: UUID,
        modality_id: UUID,
        date_range: DateRange,
        period: AggregationPeriod = AggregationPeriod.MONTHLY,
    ) -> TimeSeries:
        """Get ranking position evolution for a competitor.

        Args:
            competitor_id: Competitor UUID.
            modality_id: Modality UUID.
            date_range: Date range to query.
            period: Aggregation period.

        Returns:
            TimeSeries with ranking positions over time.
        """
        ...

    # ==========================================================================
    # Summary/Dashboard Queries
    # ==========================================================================

    @abstractmethod
    async def get_competitor_summary(
        self,
        competitor_id: UUID,
        modality_id: UUID | None = None,
    ) -> dict:
        """Get comprehensive summary for a competitor dashboard.

        Args:
            competitor_id: Competitor UUID.
            modality_id: Optional modality filter.

        Returns:
            Dictionary with all summary metrics.
        """
        ...

    @abstractmethod
    async def get_modality_summary(
        self,
        modality_id: UUID,
    ) -> dict:
        """Get comprehensive summary for a modality dashboard.

        Args:
            modality_id: Modality UUID.

        Returns:
            Dictionary with all summary metrics.
        """
        ...
