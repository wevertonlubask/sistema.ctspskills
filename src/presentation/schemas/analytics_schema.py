"""Analytics schemas."""

from datetime import date
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field

from src.domain.analytics.value_objects.metric_type import AggregationPeriod


class ExportFormat(str, Enum):
    """Export format enum."""

    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"


# Time Series Schemas
class TimeSeriesPointResponse(BaseModel):
    """Time series point response."""

    date: str
    value: float
    label: str | None = None


class TimeSeriesResponse(BaseModel):
    """Time series response (for charts)."""

    name: str
    metric_type: str
    points: list[TimeSeriesPointResponse]
    average: float
    trend: float


# Competence Map Schemas (Radar Chart)
class CompetenceScoreResponse(BaseModel):
    """Competence score response."""

    competence_id: str
    competence_name: str
    score: float
    normalized_score: float
    max_score: float
    weight: float


class CompetenceMapResponse(BaseModel):
    """Competence map response (radar chart data)."""

    competitor_id: str
    competitor_name: str
    competences: list[CompetenceScoreResponse]
    overall_average: float
    labels: list[str] = Field(description="Competence names for chart labels")
    scores: list[float] = Field(description="Normalized scores for chart data")


class CompetenceComparisonResponse(BaseModel):
    """Competence comparison response (multiple radar charts)."""

    maps: list[CompetenceMapResponse]
    competitor_ids: list[str]
    modality_id: str


# Ranking Schemas
class RankingEntryResponse(BaseModel):
    """Ranking entry response."""

    position: int
    competitor_id: str
    competitor_name: str
    score: float
    position_change: int | None = Field(
        None,
        description="Position change from previous period (positive = improved)",
    )


class RankingResponse(BaseModel):
    """Ranking response."""

    modality_id: str
    modality_name: str
    entries: list[RankingEntryResponse]
    generated_at: str
    total_competitors: int


# Training Hours Schemas
class TrainingHoursSummaryResponse(BaseModel):
    """Training hours summary response."""

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


class TrainingHoursChartResponse(BaseModel):
    """Training hours chart response (SENAI vs External)."""

    competitor_id: str
    senai_series: TimeSeriesResponse
    external_series: TimeSeriesResponse
    summary: TrainingHoursSummaryResponse


# Dashboard Summary Schemas
class CompetitorSummaryResponse(BaseModel):
    """Competitor dashboard summary response."""

    competitor_id: str
    modality_id: str | None
    grades_average: float
    grades_total: int
    grades_max: float
    grades_min: float
    training_total_hours: float
    training_total_sessions: int
    exams_participated: int


class ModalitySummaryResponse(BaseModel):
    """Modality dashboard summary response."""

    modality_id: str
    modality_name: str
    active_competitors: int
    active_exams: int
    grades_average: float
    grades_total: int
    training_total_hours: float


# Comparison Schemas
class EvolutionComparisonResponse(BaseModel):
    """Evolution comparison response (multiple competitors)."""

    series: list[TimeSeriesResponse]
    competitor_ids: list[str]
    modality_id: str | None = None


# Export Schemas
class ExportRequest(BaseModel):
    """Export request schema."""

    format: ExportFormat = Field(
        default=ExportFormat.PDF,
        description="Export format",
    )


class ExportCompetitorReportRequest(ExportRequest):
    """Export competitor report request."""

    modality_id: UUID | None = Field(None, description="Optional modality filter")
    start_date: date | None = Field(None, description="Optional start date")
    end_date: date | None = Field(None, description="Optional end date")


class ExportModalityReportRequest(ExportRequest):
    """Export modality report request."""

    include_ranking: bool = Field(True, description="Include ranking in report")


class ExportRankingRequest(ExportRequest):
    """Export ranking request."""

    format: ExportFormat = Field(
        default=ExportFormat.EXCEL,
        description="Export format",
    )
    limit: int = Field(100, ge=1, le=500, description="Maximum entries")


# Query Parameter Schemas
class DateRangeParams(BaseModel):
    """Date range query parameters."""

    start_date: date = Field(..., description="Start date")
    end_date: date = Field(..., description="End date")


class ChartQueryParams(BaseModel):
    """Common chart query parameters."""

    start_date: date = Field(..., description="Start date")
    end_date: date = Field(..., description="End date")
    period: AggregationPeriod = Field(
        default=AggregationPeriod.MONTHLY,
        description="Aggregation period",
    )
    modality_id: UUID | None = Field(None, description="Optional modality filter")
    competence_id: UUID | None = Field(None, description="Optional competence filter")
