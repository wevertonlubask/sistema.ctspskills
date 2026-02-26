"""Unit tests for Analytics entities and value objects."""

from datetime import date, datetime
from uuid import uuid4

import pytest

from src.domain.analytics.entities.performance_metric import (
    CompetenceMap,
    CompetenceScore,
    PerformanceMetric,
    Ranking,
    RankingEntry,
    TimeSeries,
    TimeSeriesPoint,
    TrainingHoursSummary,
)
from src.domain.analytics.value_objects.date_range import DateRange
from src.domain.analytics.value_objects.metric_type import (
    AggregationPeriod,
    ChartType,
    MetricType,
)
from src.shared.exceptions import InvalidValueException


class TestDateRange:
    """Tests for DateRange value object."""

    def test_create_valid_date_range(self):
        """Test creating valid date range."""
        start = date(2024, 1, 1)
        end = date(2024, 1, 31)
        dr = DateRange(start_date=start, end_date=end)

        assert dr.start_date == start
        assert dr.end_date == end

    def test_date_range_end_before_start_raises_exception(self):
        """Test that end date before start date raises exception."""
        with pytest.raises(InvalidValueException):
            DateRange(
                start_date=date(2024, 1, 31),
                end_date=date(2024, 1, 1),
            )

    def test_date_range_days(self):
        """Test calculating days in range (inclusive)."""
        dr = DateRange(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )
        assert dr.days == 31  # Jan 1-31 inclusive = 31 days

    def test_date_range_contains(self):
        """Test checking if date is in range."""
        dr = DateRange(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )

        assert dr.contains(date(2024, 1, 15)) is True
        assert dr.contains(date(2024, 1, 1)) is True
        assert dr.contains(date(2024, 1, 31)) is True
        assert dr.contains(date(2024, 2, 1)) is False

    def test_date_range_last_7_days(self):
        """Test creating last 7 days range."""
        dr = DateRange.last_7_days()
        today = date.today()

        assert dr.end_date == today
        assert dr.days == 7  # Inclusive: today and 6 days before = 7 days

    def test_date_range_last_30_days(self):
        """Test creating last 30 days range."""
        dr = DateRange.last_30_days()
        today = date.today()

        assert dr.end_date == today
        assert dr.days == 30  # Inclusive: today and 29 days before = 30 days

    def test_date_range_current_month(self):
        """Test creating current month range."""
        dr = DateRange.current_month()
        today = date.today()

        assert dr.start_date.day == 1
        assert dr.start_date.month == today.month
        assert dr.end_date == today

    def test_date_range_current_year(self):
        """Test creating current year range."""
        dr = DateRange.current_year()
        today = date.today()

        assert dr.start_date == date(today.year, 1, 1)
        assert dr.end_date == today


class TestMetricType:
    """Tests for MetricType enum."""

    def test_metric_types_exist(self):
        """Test all metric types exist."""
        assert MetricType.GRADE_AVERAGE
        assert MetricType.TRAINING_HOURS_TOTAL
        assert MetricType.COMPETENCE_SCORE
        assert MetricType.RANKING_POSITION

    def test_chart_types_exist(self):
        """Test all chart types exist."""
        assert ChartType.LINE
        assert ChartType.BAR
        assert ChartType.RADAR
        assert ChartType.PIE

    def test_aggregation_periods_exist(self):
        """Test all aggregation periods exist."""
        assert AggregationPeriod.DAILY
        assert AggregationPeriod.WEEKLY
        assert AggregationPeriod.MONTHLY
        assert AggregationPeriod.QUARTERLY
        assert AggregationPeriod.YEARLY


class TestTimeSeriesPoint:
    """Tests for TimeSeriesPoint."""

    def test_create_point(self):
        """Test creating time series point."""
        point = TimeSeriesPoint(
            date=date(2024, 1, 15),
            value=85.5,
            label="Week 2",
        )

        assert point.date == date(2024, 1, 15)
        assert point.value == 85.5
        assert point.label == "Week 2"

    def test_create_point_without_label(self):
        """Test creating point without label."""
        point = TimeSeriesPoint(
            date=date(2024, 1, 15),
            value=85.5,
        )

        assert point.label is None


class TestTimeSeries:
    """Tests for TimeSeries."""

    @pytest.fixture
    def sample_series(self):
        """Create sample time series."""
        return TimeSeries(
            name="Grade Evolution",
            points=[
                TimeSeriesPoint(date=date(2024, 1, 1), value=80.0),
                TimeSeriesPoint(date=date(2024, 1, 8), value=82.0),
                TimeSeriesPoint(date=date(2024, 1, 15), value=85.0),
                TimeSeriesPoint(date=date(2024, 1, 22), value=88.0),
                TimeSeriesPoint(date=date(2024, 1, 29), value=90.0),
            ],
            metric_type=MetricType.GRADE_AVERAGE,
        )

    def test_time_series_values(self, sample_series):
        """Test getting values from series."""
        values = sample_series.values
        assert values == [80.0, 82.0, 85.0, 88.0, 90.0]

    def test_time_series_dates(self, sample_series):
        """Test getting dates from series."""
        dates = sample_series.dates
        assert len(dates) == 5
        assert dates[0] == date(2024, 1, 1)

    def test_time_series_average(self, sample_series):
        """Test calculating average."""
        expected = (80 + 82 + 85 + 88 + 90) / 5
        assert sample_series.average == round(expected, 2)

    def test_time_series_trend(self, sample_series):
        """Test calculating trend."""
        # Trend = last value - first value
        expected = 90.0 - 80.0
        assert sample_series.trend == expected

    def test_empty_series_average(self):
        """Test average of empty series."""
        series = TimeSeries(
            name="Empty",
            points=[],
            metric_type=MetricType.GRADE_AVERAGE,
        )
        assert series.average == 0.0

    def test_single_point_trend(self):
        """Test trend with single point."""
        series = TimeSeries(
            name="Single",
            points=[TimeSeriesPoint(date=date(2024, 1, 1), value=80.0)],
            metric_type=MetricType.GRADE_AVERAGE,
        )
        assert series.trend == 0.0


class TestCompetenceScore:
    """Tests for CompetenceScore."""

    def test_create_score(self):
        """Test creating competence score."""
        score = CompetenceScore(
            competence_id=uuid4(),
            competence_name="Web Development",
            score=85.0,
            max_score=100.0,
            weight=1.0,
        )

        assert score.competence_name == "Web Development"
        assert score.score == 85.0
        assert score.normalized_score == 85.0

    def test_normalized_score_different_max(self):
        """Test normalized score with different max."""
        score = CompetenceScore(
            competence_id=uuid4(),
            competence_name="Test",
            score=170.0,
            max_score=200.0,
            weight=1.0,
        )

        assert score.normalized_score == 85.0  # 170/200 * 100

    def test_normalized_score_zero_max(self):
        """Test normalized score with zero max."""
        score = CompetenceScore(
            competence_id=uuid4(),
            competence_name="Test",
            score=50.0,
            max_score=0.0,
            weight=1.0,
        )

        assert score.normalized_score == 0.0


class TestCompetenceMap:
    """Tests for CompetenceMap (radar chart data)."""

    @pytest.fixture
    def sample_map(self):
        """Create sample competence map."""
        return CompetenceMap(
            competitor_id=uuid4(),
            competitor_name="John Doe",
            competences=[
                CompetenceScore(
                    competence_id=uuid4(),
                    competence_name="Web Development",
                    score=85.0,
                    max_score=100.0,
                ),
                CompetenceScore(
                    competence_id=uuid4(),
                    competence_name="Database",
                    score=80.0,
                    max_score=100.0,
                ),
                CompetenceScore(
                    competence_id=uuid4(),
                    competence_name="Security",
                    score=90.0,
                    max_score=100.0,
                ),
            ],
            overall_average=85.0,
        )

    def test_competence_map_labels(self, sample_map):
        """Test getting labels for chart."""
        labels = sample_map.labels
        assert labels == ["Web Development", "Database", "Security"]

    def test_competence_map_scores(self, sample_map):
        """Test getting scores for chart."""
        scores = sample_map.scores
        assert scores == [85.0, 80.0, 90.0]


class TestRankingEntry:
    """Tests for RankingEntry."""

    def test_create_entry(self):
        """Test creating ranking entry."""
        entry = RankingEntry(
            position=1,
            competitor_id=uuid4(),
            competitor_name="John Doe",
            score=92.5,
            previous_position=3,
        )

        assert entry.position == 1
        assert entry.score == 92.5
        assert entry.previous_position == 3

    def test_position_change_improved(self):
        """Test position change when improved."""
        entry = RankingEntry(
            position=1,
            competitor_id=uuid4(),
            competitor_name="John Doe",
            score=92.5,
            previous_position=3,
        )

        # Was 3rd, now 1st = improved by 2 positions
        assert entry.position_change == 2

    def test_position_change_declined(self):
        """Test position change when declined."""
        entry = RankingEntry(
            position=5,
            competitor_id=uuid4(),
            competitor_name="John Doe",
            score=75.0,
            previous_position=2,
        )

        # Was 2nd, now 5th = declined by 3 positions
        assert entry.position_change == -3

    def test_position_change_no_previous(self):
        """Test position change with no previous position."""
        entry = RankingEntry(
            position=1,
            competitor_id=uuid4(),
            competitor_name="John Doe",
            score=92.5,
        )

        assert entry.position_change is None


class TestRanking:
    """Tests for Ranking."""

    @pytest.fixture
    def sample_ranking(self):
        """Create sample ranking."""
        modality_id = uuid4()
        return Ranking(
            modality_id=modality_id,
            modality_name="Web Development",
            entries=[
                RankingEntry(
                    position=1, competitor_id=uuid4(), competitor_name="Alice", score=95.0
                ),
                RankingEntry(position=2, competitor_id=uuid4(), competitor_name="Bob", score=90.0),
                RankingEntry(
                    position=3, competitor_id=uuid4(), competitor_name="Charlie", score=85.0
                ),
                RankingEntry(
                    position=4, competitor_id=uuid4(), competitor_name="Diana", score=80.0
                ),
                RankingEntry(position=5, competitor_id=uuid4(), competitor_name="Eve", score=75.0),
            ],
            generated_at=datetime.now(),
        )

    def test_ranking_top_3(self, sample_ranking):
        """Test getting top 3."""
        top_3 = sample_ranking.top_3

        assert len(top_3) == 3
        assert top_3[0].competitor_name == "Alice"
        assert top_3[1].competitor_name == "Bob"
        assert top_3[2].competitor_name == "Charlie"

    def test_ranking_get_position(self, sample_ranking):
        """Test getting position by competitor ID."""
        charlie_id = sample_ranking.entries[2].competitor_id
        position = sample_ranking.get_position(charlie_id)

        assert position == 3

    def test_ranking_get_position_not_found(self, sample_ranking):
        """Test getting position for unknown competitor."""
        position = sample_ranking.get_position(uuid4())
        assert position is None


class TestTrainingHoursSummary:
    """Tests for TrainingHoursSummary."""

    @pytest.fixture
    def sample_summary(self):
        """Create sample training hours summary."""
        return TrainingHoursSummary(
            competitor_id=uuid4(),
            total_hours=100.0,
            senai_hours=70.0,
            external_hours=30.0,
            approved_hours=80.0,
            pending_hours=15.0,
            rejected_hours=5.0,
            sessions_count=20,
            approval_rate=80.0,
        )

    def test_senai_percentage(self, sample_summary):
        """Test calculating SENAI percentage."""
        assert sample_summary.senai_percentage == 70.0  # 70/100 * 100

    def test_external_percentage(self, sample_summary):
        """Test calculating external percentage."""
        assert sample_summary.external_percentage == 30.0  # 30/100 * 100

    def test_zero_total_percentages(self):
        """Test percentages with zero total hours."""
        summary = TrainingHoursSummary(
            competitor_id=uuid4(),
            total_hours=0.0,
            senai_hours=0.0,
            external_hours=0.0,
            approved_hours=0.0,
            pending_hours=0.0,
            rejected_hours=0.0,
            sessions_count=0,
            approval_rate=0.0,
        )

        assert summary.senai_percentage == 0.0
        assert summary.external_percentage == 0.0


class TestPerformanceMetric:
    """Tests for PerformanceMetric."""

    def test_create_metric(self):
        """Test creating performance metric."""
        metric = PerformanceMetric(
            metric_type=MetricType.GRADE_AVERAGE,
            value=85.5,
            entity_id=uuid4(),
            entity_type="competitor",
            metric_date=date(2024, 1, 15),
        )

        assert metric.metric_type == MetricType.GRADE_AVERAGE
        assert metric.value == 85.5
        assert metric.entity_type == "competitor"

    def test_negative_value_clamped_to_zero(self):
        """Test that negative values are clamped to zero."""
        metric = PerformanceMetric(
            metric_type=MetricType.GRADE_AVERAGE,
            value=-10.0,
            entity_id=uuid4(),
            entity_type="competitor",
            metric_date=date(2024, 1, 15),
        )

        assert metric.value == 0.0

    def test_metric_with_metadata(self):
        """Test creating metric with metadata."""
        metric = PerformanceMetric(
            metric_type=MetricType.COMPETENCE_SCORE,
            value=90.0,
            entity_id=uuid4(),
            entity_type="competence",
            metric_date=date(2024, 1, 15),
            metadata={"competence_name": "Web Development"},
        )

        assert metric.metadata["competence_name"] == "Web Development"
