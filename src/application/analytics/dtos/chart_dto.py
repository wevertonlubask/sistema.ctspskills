"""Chart and analytics DTOs."""

from dataclasses import dataclass

from src.domain.analytics.entities.performance_metric import (
    CompetenceMap,
    CompetenceScore,
    Ranking,
    RankingEntry,
    TimeSeries,
    TimeSeriesPoint,
    TrainingHoursSummary,
)


@dataclass
class TimeSeriesPointDTO:
    """DTO for a single time series point."""

    date: str
    value: float
    label: str | None = None

    @classmethod
    def from_domain(cls, point: TimeSeriesPoint) -> "TimeSeriesPointDTO":
        return cls(
            date=point.date.isoformat(),
            value=point.value,
            label=point.label,
        )


@dataclass
class TimeSeriesDTO:
    """DTO for time series data (charts)."""

    name: str
    metric_type: str
    points: list[TimeSeriesPointDTO]
    average: float
    trend: float

    @classmethod
    def from_domain(cls, series: TimeSeries) -> "TimeSeriesDTO":
        return cls(
            name=series.name,
            metric_type=series.metric_type.value,
            points=[TimeSeriesPointDTO.from_domain(p) for p in series.points],
            average=series.average,
            trend=series.trend,
        )


@dataclass
class CompetenceScoreDTO:
    """DTO for competence score."""

    competence_id: str
    competence_name: str
    score: float
    normalized_score: float
    max_score: float
    weight: float

    @classmethod
    def from_domain(cls, score: CompetenceScore) -> "CompetenceScoreDTO":
        return cls(
            competence_id=str(score.competence_id),
            competence_name=score.competence_name,
            score=score.score,
            normalized_score=score.normalized_score,
            max_score=score.max_score,
            weight=score.weight,
        )


@dataclass
class CompetenceMapDTO:
    """DTO for competence map (radar chart)."""

    competitor_id: str
    competitor_name: str
    competences: list[CompetenceScoreDTO]
    overall_average: float
    labels: list[str]
    scores: list[float]

    @classmethod
    def from_domain(cls, comp_map: CompetenceMap) -> "CompetenceMapDTO":
        return cls(
            competitor_id=str(comp_map.competitor_id),
            competitor_name=comp_map.competitor_name,
            competences=[CompetenceScoreDTO.from_domain(c) for c in comp_map.competences],
            overall_average=comp_map.overall_average,
            labels=comp_map.labels,
            scores=comp_map.scores,
        )


@dataclass
class RankingEntryDTO:
    """DTO for ranking entry."""

    position: int
    competitor_id: str
    competitor_name: str
    score: float
    position_change: int | None = None

    @classmethod
    def from_domain(cls, entry: RankingEntry) -> "RankingEntryDTO":
        return cls(
            position=entry.position,
            competitor_id=str(entry.competitor_id),
            competitor_name=entry.competitor_name,
            score=entry.score,
            position_change=entry.position_change,
        )


@dataclass
class RankingDTO:
    """DTO for ranking data."""

    modality_id: str
    modality_name: str
    entries: list[RankingEntryDTO]
    generated_at: str
    total_competitors: int

    @classmethod
    def from_domain(cls, ranking: Ranking) -> "RankingDTO":
        return cls(
            modality_id=str(ranking.modality_id),
            modality_name=ranking.modality_name,
            entries=[RankingEntryDTO.from_domain(e) for e in ranking.entries],
            generated_at=ranking.generated_at.isoformat(),
            total_competitors=len(ranking.entries),
        )


@dataclass
class TrainingHoursSummaryDTO:
    """DTO for training hours summary."""

    competitor_id: str
    total_hours: float
    senai_hours: float
    external_hours: float
    approved_hours: float
    pending_hours: float
    rejected_hours: float
    sessions_count: int
    approval_rate: float
    senai_percentage: float
    external_percentage: float

    @classmethod
    def from_domain(cls, summary: TrainingHoursSummary) -> "TrainingHoursSummaryDTO":
        return cls(
            competitor_id=str(summary.competitor_id),
            total_hours=summary.total_hours,
            senai_hours=summary.senai_hours,
            external_hours=summary.external_hours,
            approved_hours=summary.approved_hours,
            pending_hours=summary.pending_hours,
            rejected_hours=summary.rejected_hours,
            sessions_count=summary.sessions_count,
            approval_rate=summary.approval_rate,
            senai_percentage=summary.senai_percentage,
            external_percentage=summary.external_percentage,
        )


@dataclass
class TrainingHoursChartDTO:
    """DTO for training hours chart (SENAI vs External)."""

    competitor_id: str
    senai_series: TimeSeriesDTO
    external_series: TimeSeriesDTO
    summary: TrainingHoursSummaryDTO


@dataclass
class CompetitorSummaryDTO:
    """DTO for competitor dashboard summary."""

    competitor_id: str
    modality_id: str | None
    grades_average: float
    grades_total: int
    grades_max: float
    grades_min: float
    training_total_hours: float
    training_total_sessions: int
    exams_participated: int


@dataclass
class ModalitySummaryDTO:
    """DTO for modality dashboard summary."""

    modality_id: str
    modality_name: str
    active_competitors: int
    active_exams: int
    grades_average: float
    grades_total: int
    training_total_hours: float


@dataclass
class EvolutionComparisonDTO:
    """DTO for comparing multiple competitors."""

    series: list[TimeSeriesDTO]
    competitor_ids: list[str]
    modality_id: str | None = None


@dataclass
class CompetenceComparisonDTO:
    """DTO for comparing competence maps."""

    maps: list[CompetenceMapDTO]
    competitor_ids: list[str]
    modality_id: str
