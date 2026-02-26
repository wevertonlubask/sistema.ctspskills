"""Aggregation service for analytics calculations."""

from dataclasses import dataclass
from datetime import date
from statistics import mean, median, stdev
from uuid import UUID

from src.domain.analytics.entities.performance_metric import (
    CompetenceMap,
    CompetenceScore,
    Ranking,
    RankingEntry,
    TimeSeries,
    TimeSeriesPoint,
    TrainingHoursSummary,
)
from src.domain.analytics.value_objects.metric_type import AggregationPeriod, MetricType


@dataclass
class GradeData:
    """Raw grade data for aggregation."""

    score: float
    exam_date: date
    competence_id: UUID
    competence_name: str


@dataclass
class TrainingData:
    """Raw training data for aggregation."""

    hours: float
    training_date: date
    training_type: str
    status: str


class AggregationService:
    """Domain service for data aggregation and metric calculation.

    Provides methods to aggregate raw data into analytics metrics.
    """

    @staticmethod
    def calculate_statistics(values: list[float]) -> dict[str, float]:
        """Calculate basic statistics from a list of values.

        Args:
            values: List of numeric values.

        Returns:
            Dictionary with average, median, min, max, std_dev.
        """
        if not values:
            return {
                "average": 0.0,
                "median": 0.0,
                "min": 0.0,
                "max": 0.0,
                "std_dev": 0.0,
                "count": 0,
            }

        avg = round(mean(values), 2)
        med = round(median(values), 2)
        min_val = round(min(values), 2)
        max_val = round(max(values), 2)
        std = round(stdev(values), 2) if len(values) >= 2 else 0.0

        return {
            "average": avg,
            "median": med,
            "min": min_val,
            "max": max_val,
            "std_dev": std,
            "count": len(values),
        }

    @staticmethod
    def aggregate_by_period(
        data: list[tuple[date, float]],
        period: AggregationPeriod,
    ) -> list[TimeSeriesPoint]:
        """Aggregate data points by time period.

        Args:
            data: List of (date, value) tuples.
            period: Aggregation period.

        Returns:
            List of aggregated TimeSeriesPoints.
        """
        if not data:
            return []

        # Group by period
        groups: dict[str, list[float]] = {}
        group_dates: dict[str, date] = {}

        for d, value in data:
            key = AggregationService._get_period_key(d, period)
            if key not in groups:
                groups[key] = []
                group_dates[key] = d
            groups[key].append(value)

        # Calculate averages
        points = []
        for key in sorted(groups.keys()):
            avg = round(mean(groups[key]), 2)
            points.append(
                TimeSeriesPoint(
                    date=group_dates[key],
                    value=avg,
                    label=key,
                )
            )

        return points

    @staticmethod
    def _get_period_key(d: date, period: AggregationPeriod) -> str:
        """Get grouping key for a date based on period."""
        if period == AggregationPeriod.DAILY:
            return d.isoformat()
        elif period == AggregationPeriod.WEEKLY:
            # ISO week number
            return f"{d.year}-W{d.isocalendar()[1]:02d}"
        elif period == AggregationPeriod.MONTHLY:
            return f"{d.year}-{d.month:02d}"
        elif period == AggregationPeriod.QUARTERLY:
            quarter = (d.month - 1) // 3 + 1
            return f"{d.year}-Q{quarter}"
        elif period == AggregationPeriod.YEARLY:
            return str(d.year)
        return d.isoformat()

    @staticmethod
    def create_grade_time_series(
        grades: list[GradeData],
        competitor_name: str,
        period: AggregationPeriod,
    ) -> TimeSeries:
        """Create time series from grade data.

        Args:
            grades: List of grade data.
            competitor_name: Name for the series.
            period: Aggregation period.

        Returns:
            TimeSeries with grade averages.
        """
        data = [(g.exam_date, g.score) for g in grades]
        points = AggregationService.aggregate_by_period(data, period)

        return TimeSeries(
            name=competitor_name,
            points=points,
            metric_type=MetricType.GRADE_AVERAGE,
        )

    @staticmethod
    def create_training_time_series(
        trainings: list[TrainingData],
        training_type: str,
        period: AggregationPeriod,
    ) -> TimeSeries:
        """Create time series from training data.

        Args:
            trainings: List of training data.
            training_type: "senai" or "external".
            period: Aggregation period.

        Returns:
            TimeSeries with training hours.
        """
        # Filter by type and approved status
        filtered = [
            t for t in trainings if t.training_type == training_type and t.status == "approved"
        ]

        # Group by period and sum hours
        groups: dict[str, float] = {}
        group_dates: dict[str, date] = {}

        for t in filtered:
            key = AggregationService._get_period_key(t.training_date, period)
            if key not in groups:
                groups[key] = 0.0
                group_dates[key] = t.training_date
            groups[key] += t.hours

        points = [
            TimeSeriesPoint(
                date=group_dates[key],
                value=round(groups[key], 2),
                label=key,
            )
            for key in sorted(groups.keys())
        ]

        metric_type = (
            MetricType.TRAINING_HOURS_SENAI
            if training_type == "senai"
            else MetricType.TRAINING_HOURS_EXTERNAL
        )

        return TimeSeries(
            name=f"Training Hours ({training_type.title()})",
            points=points,
            metric_type=metric_type,
        )

    @staticmethod
    def create_competence_map(
        grades: list[GradeData],
        competitor_id: UUID,
        competitor_name: str,
    ) -> CompetenceMap:
        """Create competence map from grade data.

        Args:
            grades: List of grade data.
            competitor_id: Competitor UUID.
            competitor_name: Competitor name.

        Returns:
            CompetenceMap for radar chart.
        """
        # Group by competence and calculate averages
        competence_scores: dict[UUID, list[float]] = {}
        competence_names: dict[UUID, str] = {}

        for g in grades:
            if g.competence_id not in competence_scores:
                competence_scores[g.competence_id] = []
                competence_names[g.competence_id] = g.competence_name
            competence_scores[g.competence_id].append(g.score)

        competences = [
            CompetenceScore(
                competence_id=comp_id,
                competence_name=competence_names[comp_id],
                score=round(mean(scores), 2),
            )
            for comp_id, scores in competence_scores.items()
        ]

        all_scores = [c.score for c in competences]
        overall_avg = round(mean(all_scores), 2) if all_scores else 0.0

        return CompetenceMap(
            competitor_id=competitor_id,
            competitor_name=competitor_name,
            competences=competences,
            overall_average=overall_avg,
        )

    @staticmethod
    def create_ranking(
        competitor_scores: list[tuple[UUID, str, float]],
        modality_id: UUID,
        modality_name: str,
    ) -> Ranking:
        """Create ranking from competitor scores.

        Args:
            competitor_scores: List of (competitor_id, name, score) tuples.
            modality_id: Modality UUID.
            modality_name: Modality name.

        Returns:
            Ranking with sorted entries.
        """
        from datetime import datetime

        # Sort by score descending
        sorted_scores = sorted(competitor_scores, key=lambda x: x[2], reverse=True)

        entries = [
            RankingEntry(
                position=i + 1,
                competitor_id=comp_id,
                competitor_name=name,
                score=round(score, 2),
                modality_id=modality_id,
            )
            for i, (comp_id, name, score) in enumerate(sorted_scores)
        ]

        return Ranking(
            modality_id=modality_id,
            modality_name=modality_name,
            entries=entries,
            generated_at=datetime.utcnow(),
        )

    @staticmethod
    def create_training_summary(
        trainings: list[TrainingData],
        competitor_id: UUID,
    ) -> TrainingHoursSummary:
        """Create training hours summary.

        Args:
            trainings: List of training data.
            competitor_id: Competitor UUID.

        Returns:
            TrainingHoursSummary with all metrics.
        """
        total_hours = sum(t.hours for t in trainings)
        senai_hours = sum(t.hours for t in trainings if t.training_type == "senai")
        external_hours = sum(t.hours for t in trainings if t.training_type == "external")
        approved_hours = sum(t.hours for t in trainings if t.status == "approved")
        pending_hours = sum(t.hours for t in trainings if t.status == "pending")
        rejected_hours = sum(t.hours for t in trainings if t.status == "rejected")

        sessions_count = len(trainings)
        approved_count = len([t for t in trainings if t.status == "approved"])
        approval_rate = (
            round((approved_count / sessions_count) * 100, 2) if sessions_count > 0 else 0.0
        )

        return TrainingHoursSummary(
            competitor_id=competitor_id,
            total_hours=round(total_hours, 2),
            senai_hours=round(senai_hours, 2),
            external_hours=round(external_hours, 2),
            approved_hours=round(approved_hours, 2),
            pending_hours=round(pending_hours, 2),
            rejected_hours=round(rejected_hours, 2),
            sessions_count=sessions_count,
            approval_rate=approval_rate,
        )
