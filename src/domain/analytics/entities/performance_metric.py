"""Performance metric entity for analytics."""

from dataclasses import dataclass, field
from datetime import date, datetime
from uuid import UUID

from src.domain.analytics.value_objects.metric_type import AggregationPeriod, MetricType


@dataclass(frozen=True)
class PerformanceMetric:
    """Immutable performance metric for analytics.

    Represents a calculated metric value for a specific entity
    at a specific point in time.
    """

    metric_type: MetricType
    value: float
    entity_id: UUID  # competitor_id, modality_id, exam_id, etc.
    entity_type: str  # "competitor", "modality", "exam", etc.
    metric_date: date
    period: AggregationPeriod = AggregationPeriod.DAILY
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate metric."""
        if self.value < 0 and self.metric_type not in [
            MetricType.COMPETENCE_EVOLUTION,
        ]:
            object.__setattr__(self, "value", 0.0)


@dataclass(frozen=True)
class TimeSeriesPoint:
    """A single point in a time series."""

    date: date
    value: float
    label: str | None = None


@dataclass(frozen=True)
class TimeSeries:
    """Time series data for charts."""

    name: str
    points: list[TimeSeriesPoint]
    metric_type: MetricType

    @property
    def values(self) -> list[float]:
        """Get just the values."""
        return [p.value for p in self.points]

    @property
    def dates(self) -> list[date]:
        """Get just the dates."""
        return [p.date for p in self.points]

    @property
    def average(self) -> float:
        """Calculate average of all points."""
        if not self.points:
            return 0.0
        return round(sum(self.values) / len(self.values), 2)

    @property
    def trend(self) -> float:
        """Calculate trend (difference between first and last)."""
        if len(self.points) < 2:
            return 0.0
        return round(self.points[-1].value - self.points[0].value, 2)


@dataclass(frozen=True)
class CompetenceScore:
    """Score for a single competence (for radar charts)."""

    competence_id: UUID
    competence_name: str
    score: float
    max_score: float = 100.0
    weight: float = 1.0

    @property
    def normalized_score(self) -> float:
        """Get score as percentage (0-100)."""
        if self.max_score == 0:
            return 0.0
        return round((self.score / self.max_score) * 100, 2)


@dataclass(frozen=True)
class CompetenceMap:
    """Competence map data for radar charts."""

    competitor_id: UUID
    competitor_name: str
    competences: list[CompetenceScore]
    overall_average: float

    @property
    def labels(self) -> list[str]:
        """Get competence names for chart labels."""
        return [c.competence_name for c in self.competences]

    @property
    def scores(self) -> list[float]:
        """Get normalized scores for chart data."""
        return [c.normalized_score for c in self.competences]


@dataclass(frozen=True)
class RankingEntry:
    """A single entry in a ranking."""

    position: int
    competitor_id: UUID
    competitor_name: str
    score: float
    previous_position: int | None = None
    modality_id: UUID | None = None

    @property
    def position_change(self) -> int | None:
        """Calculate position change from previous."""
        if self.previous_position is None:
            return None
        return self.previous_position - self.position  # Positive = improved


@dataclass(frozen=True)
class Ranking:
    """Complete ranking for a modality."""

    modality_id: UUID
    modality_name: str
    entries: list[RankingEntry]
    generated_at: datetime
    metric_type: MetricType = MetricType.GRADE_AVERAGE

    @property
    def top_3(self) -> list[RankingEntry]:
        """Get top 3 entries."""
        return self.entries[:3]

    def get_position(self, competitor_id: UUID) -> int | None:
        """Get position of a specific competitor."""
        for entry in self.entries:
            if entry.competitor_id == competitor_id:
                return entry.position
        return None


@dataclass(frozen=True)
class TrainingHoursSummary:
    """Summary of training hours."""

    competitor_id: UUID
    total_hours: float
    senai_hours: float
    external_hours: float
    approved_hours: float
    pending_hours: float
    rejected_hours: float
    sessions_count: int
    approval_rate: float

    @property
    def senai_percentage(self) -> float:
        """Get SENAI hours as percentage of total."""
        if self.total_hours == 0:
            return 0.0
        return round((self.senai_hours / self.total_hours) * 100, 2)

    @property
    def external_percentage(self) -> float:
        """Get external hours as percentage of total."""
        if self.total_hours == 0:
            return 0.0
        return round((self.external_hours / self.total_hours) * 100, 2)
