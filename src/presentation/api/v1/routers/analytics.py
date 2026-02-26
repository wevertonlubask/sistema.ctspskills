"""Analytics router."""

from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.analytics.use_cases import (
    ExportReportUseCase,
    GenerateComparisonChartUseCase,
    GenerateCompetenceMapUseCase,
    GenerateEvolutionChartUseCase,
    GenerateRankingUseCase,
    GenerateTrainingHoursChartUseCase,
    GetCompetitorSummaryUseCase,
    GetModalitySummaryUseCase,
)
from src.application.analytics.use_cases.export_report import ExportFormat
from src.domain.analytics.value_objects.metric_type import AggregationPeriod
from src.domain.identity.entities.user import User
from src.infrastructure.database.repositories import (
    SQLAlchemyAnalyticsRepository,
    SQLAlchemyCompetitorRepository,
    SQLAlchemyModalityRepository,
)
from src.presentation.api.v1.dependencies.auth import (
    get_current_active_user,
    require_evaluator,
)
from src.presentation.api.v1.dependencies.database import get_db
from src.presentation.schemas.analytics_schema import (
    CompetenceComparisonResponse,
    CompetenceMapResponse,
    CompetenceScoreResponse,
    CompetitorSummaryResponse,
    EvolutionComparisonResponse,
    ExportCompetitorReportRequest,
    ExportModalityReportRequest,
    ExportRankingRequest,
    ModalitySummaryResponse,
    RankingEntryResponse,
    RankingResponse,
    TimeSeriesPointResponse,
    TimeSeriesResponse,
    TrainingHoursChartResponse,
    TrainingHoursSummaryResponse,
)

router = APIRouter()


# =============================================================================
# Grade Evolution Charts
# =============================================================================


@router.get(
    "/evolution/{competitor_id}",
    response_model=TimeSeriesResponse,
    summary="Get grade evolution",
    description="Get grade evolution over time for a competitor.",
)
async def get_grade_evolution(
    competitor_id: UUID,
    start_date: date,
    end_date: date,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    period: AggregationPeriod = Query(default=AggregationPeriod.MONTHLY),
    modality_id: UUID | None = Query(default=None),
    competence_id: UUID | None = Query(default=None),
) -> TimeSeriesResponse:
    """Get grade evolution chart data."""
    use_case = GenerateEvolutionChartUseCase(
        analytics_repository=SQLAlchemyAnalyticsRepository(db),
        competitor_repository=SQLAlchemyCompetitorRepository(db),
    )

    result = await use_case.execute(
        competitor_id=competitor_id,
        start_date=start_date,
        end_date=end_date,
        period=period,
        modality_id=modality_id,
        competence_id=competence_id,
    )

    return TimeSeriesResponse(
        name=result.name,
        metric_type=result.metric_type,
        points=[
            TimeSeriesPointResponse(date=p.date, value=p.value, label=p.label)
            for p in result.points
        ],
        average=result.average,
        trend=result.trend,
    )


@router.post(
    "/evolution/compare",
    response_model=EvolutionComparisonResponse,
    summary="Compare grade evolution",
    description="Compare grade evolution for multiple competitors.",
)
async def compare_evolution(
    competitor_ids: list[UUID],
    start_date: date,
    end_date: date,
    current_user: Annotated[User, Depends(require_evaluator)],
    db: Annotated[AsyncSession, Depends(get_db)],
    modality_id: UUID | None = Query(default=None),
) -> EvolutionComparisonResponse:
    """Compare grade evolution for multiple competitors."""
    use_case = GenerateComparisonChartUseCase(
        analytics_repository=SQLAlchemyAnalyticsRepository(db),
    )

    result = await use_case.execute(
        competitor_ids=competitor_ids,
        start_date=start_date,
        end_date=end_date,
        modality_id=modality_id,
    )

    return EvolutionComparisonResponse(
        series=[
            TimeSeriesResponse(
                name=s.name,
                metric_type=s.metric_type,
                points=[
                    TimeSeriesPointResponse(date=p.date, value=p.value, label=p.label)
                    for p in s.points
                ],
                average=s.average,
                trend=s.trend,
            )
            for s in result.series
        ],
        competitor_ids=result.competitor_ids,
        modality_id=result.modality_id,
    )


# =============================================================================
# Training Hours Charts
# =============================================================================


@router.get(
    "/training-hours/{competitor_id}",
    response_model=TrainingHoursChartResponse,
    summary="Get training hours chart",
    description="Get training hours chart (SENAI vs External) for a competitor.",
)
async def get_training_hours_chart(
    competitor_id: UUID,
    start_date: date,
    end_date: date,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    period: AggregationPeriod = Query(default=AggregationPeriod.MONTHLY),
    modality_id: UUID | None = Query(default=None),
) -> TrainingHoursChartResponse:
    """Get training hours chart data."""
    use_case = GenerateTrainingHoursChartUseCase(
        analytics_repository=SQLAlchemyAnalyticsRepository(db),
        competitor_repository=SQLAlchemyCompetitorRepository(db),
    )

    result = await use_case.execute(
        competitor_id=competitor_id,
        start_date=start_date,
        end_date=end_date,
        period=period,
        modality_id=modality_id,
    )

    return TrainingHoursChartResponse(
        competitor_id=result.competitor_id,
        senai_series=TimeSeriesResponse(
            name=result.senai_series.name,
            metric_type=result.senai_series.metric_type,
            points=[
                TimeSeriesPointResponse(date=p.date, value=p.value, label=p.label)
                for p in result.senai_series.points
            ],
            average=result.senai_series.average,
            trend=result.senai_series.trend,
        ),
        external_series=TimeSeriesResponse(
            name=result.external_series.name,
            metric_type=result.external_series.metric_type,
            points=[
                TimeSeriesPointResponse(date=p.date, value=p.value, label=p.label)
                for p in result.external_series.points
            ],
            average=result.external_series.average,
            trend=result.external_series.trend,
        ),
        summary=TrainingHoursSummaryResponse(
            competitor_id=result.summary.competitor_id,
            total_hours=result.summary.total_hours,
            senai_hours=result.summary.senai_hours,
            external_hours=result.summary.external_hours,
            approved_hours=result.summary.approved_hours,
            pending_hours=result.summary.pending_hours,
            rejected_hours=result.summary.rejected_hours,
            sessions_count=result.summary.sessions_count,
            approval_rate=result.summary.approval_rate,
            senai_percentage=result.summary.senai_percentage,
            external_percentage=result.summary.external_percentage,
        ),
    )


# =============================================================================
# Competence Maps (Radar Charts)
# =============================================================================


@router.get(
    "/competence-map/{competitor_id}/{modality_id}",
    response_model=CompetenceMapResponse,
    summary="Get competence map",
    description="Get competence map (radar chart) for a competitor in a modality.",
)
async def get_competence_map(
    competitor_id: UUID,
    modality_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    exam_id: UUID | None = Query(default=None),
) -> CompetenceMapResponse:
    """Get competence map for radar chart."""
    use_case = GenerateCompetenceMapUseCase(
        analytics_repository=SQLAlchemyAnalyticsRepository(db),
        competitor_repository=SQLAlchemyCompetitorRepository(db),
        modality_repository=SQLAlchemyModalityRepository(db),
    )

    result = await use_case.execute(
        competitor_id=competitor_id,
        modality_id=modality_id,
        exam_id=exam_id,
    )

    return CompetenceMapResponse(
        competitor_id=result.competitor_id,
        competitor_name=result.competitor_name,
        competences=[
            CompetenceScoreResponse(
                competence_id=c.competence_id,
                competence_name=c.competence_name,
                score=c.score,
                normalized_score=c.normalized_score,
                max_score=c.max_score,
                weight=c.weight,
            )
            for c in result.competences
        ],
        overall_average=result.overall_average,
        labels=result.labels,
        scores=result.scores,
    )


@router.post(
    "/competence-map/compare/{modality_id}",
    response_model=CompetenceComparisonResponse,
    summary="Compare competence maps",
    description="Compare competence maps for multiple competitors.",
)
async def compare_competence_maps(
    modality_id: UUID,
    competitor_ids: list[UUID],
    current_user: Annotated[User, Depends(require_evaluator)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CompetenceComparisonResponse:
    """Compare competence maps for multiple competitors."""
    use_case = GenerateCompetenceMapUseCase(
        analytics_repository=SQLAlchemyAnalyticsRepository(db),
        competitor_repository=SQLAlchemyCompetitorRepository(db),
        modality_repository=SQLAlchemyModalityRepository(db),
    )

    result = await use_case.compare(
        competitor_ids=competitor_ids,
        modality_id=modality_id,
    )

    return CompetenceComparisonResponse(
        maps=[
            CompetenceMapResponse(
                competitor_id=m.competitor_id,
                competitor_name=m.competitor_name,
                competences=[
                    CompetenceScoreResponse(
                        competence_id=c.competence_id,
                        competence_name=c.competence_name,
                        score=c.score,
                        normalized_score=c.normalized_score,
                        max_score=c.max_score,
                        weight=c.weight,
                    )
                    for c in m.competences
                ],
                overall_average=m.overall_average,
                labels=m.labels,
                scores=m.scores,
            )
            for m in result.maps
        ],
        competitor_ids=result.competitor_ids,
        modality_id=result.modality_id,
    )


# =============================================================================
# Rankings
# =============================================================================


@router.get(
    "/ranking/{modality_id}",
    response_model=RankingResponse,
    summary="Get ranking",
    description="Get competitor ranking for a modality.",
)
async def get_ranking(
    modality_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
) -> RankingResponse:
    """Get ranking for a modality."""
    use_case = GenerateRankingUseCase(
        analytics_repository=SQLAlchemyAnalyticsRepository(db),
        modality_repository=SQLAlchemyModalityRepository(db),
        competitor_repository=SQLAlchemyCompetitorRepository(db),
    )

    result = await use_case.execute(
        modality_id=modality_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )

    return RankingResponse(
        modality_id=result.modality_id,
        modality_name=result.modality_name,
        entries=[
            RankingEntryResponse(
                position=e.position,
                competitor_id=e.competitor_id,
                competitor_name=e.competitor_name,
                score=e.score,
                position_change=e.position_change,
            )
            for e in result.entries
        ],
        generated_at=result.generated_at,
        total_competitors=result.total_competitors,
    )


@router.get(
    "/ranking/{modality_id}/position-history/{competitor_id}",
    response_model=TimeSeriesResponse,
    summary="Get position history",
    description="Get ranking position history for a competitor in a modality.",
)
async def get_position_history(
    modality_id: UUID,
    competitor_id: UUID,
    start_date: date,
    end_date: date,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    period: AggregationPeriod = Query(default=AggregationPeriod.MONTHLY),
) -> TimeSeriesResponse:
    """Get position history for a competitor."""
    use_case = GenerateRankingUseCase(
        analytics_repository=SQLAlchemyAnalyticsRepository(db),
        modality_repository=SQLAlchemyModalityRepository(db),
        competitor_repository=SQLAlchemyCompetitorRepository(db),
    )

    result = await use_case.get_position_history(
        competitor_id=competitor_id,
        modality_id=modality_id,
        start_date=start_date,
        end_date=end_date,
        period=period,
    )

    return TimeSeriesResponse(
        name=result.name,
        metric_type=result.metric_type,
        points=[
            TimeSeriesPointResponse(date=p.date, value=p.value, label=p.label)
            for p in result.points
        ],
        average=result.average,
        trend=result.trend,
    )


# =============================================================================
# Dashboard Summaries
# =============================================================================


@router.get(
    "/summary/competitor/{competitor_id}",
    response_model=CompetitorSummaryResponse,
    summary="Get competitor summary",
    description="Get comprehensive summary for a competitor dashboard.",
)
async def get_competitor_summary(
    competitor_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    modality_id: UUID | None = Query(default=None),
) -> CompetitorSummaryResponse:
    """Get competitor dashboard summary."""
    use_case = GetCompetitorSummaryUseCase(
        analytics_repository=SQLAlchemyAnalyticsRepository(db),
        competitor_repository=SQLAlchemyCompetitorRepository(db),
        modality_repository=SQLAlchemyModalityRepository(db),
    )

    result = await use_case.execute(
        competitor_id=competitor_id,
        modality_id=modality_id,
    )

    return CompetitorSummaryResponse(
        competitor_id=result.competitor_id,
        modality_id=result.modality_id,
        grades_average=result.grades_average,
        grades_total=result.grades_total,
        grades_max=result.grades_max,
        grades_min=result.grades_min,
        training_total_hours=result.training_total_hours,
        training_total_sessions=result.training_total_sessions,
        exams_participated=result.exams_participated,
    )


@router.get(
    "/summary/modality/{modality_id}",
    response_model=ModalitySummaryResponse,
    summary="Get modality summary",
    description="Get comprehensive summary for a modality dashboard.",
)
async def get_modality_summary(
    modality_id: UUID,
    current_user: Annotated[User, Depends(require_evaluator)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ModalitySummaryResponse:
    """Get modality dashboard summary."""
    use_case = GetModalitySummaryUseCase(
        analytics_repository=SQLAlchemyAnalyticsRepository(db),
        modality_repository=SQLAlchemyModalityRepository(db),
    )

    result = await use_case.execute(modality_id=modality_id)

    return ModalitySummaryResponse(
        modality_id=result.modality_id,
        modality_name=result.modality_name,
        active_competitors=result.active_competitors,
        active_exams=result.active_exams,
        grades_average=result.grades_average,
        grades_total=result.grades_total,
        training_total_hours=result.training_total_hours,
    )


# =============================================================================
# Export Reports
# =============================================================================


@router.post(
    "/export/competitor/{competitor_id}",
    summary="Export competitor report",
    description="Export comprehensive competitor report.",
)
async def export_competitor_report(
    competitor_id: UUID,
    request: ExportCompetitorReportRequest,
    current_user: Annotated[User, Depends(require_evaluator)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Response:
    """Export competitor report."""
    use_case = ExportReportUseCase(
        analytics_repository=SQLAlchemyAnalyticsRepository(db),
        competitor_repository=SQLAlchemyCompetitorRepository(db),
        modality_repository=SQLAlchemyModalityRepository(db),
    )

    # Convert schema format to use case format
    format_map = {
        "pdf": ExportFormat.PDF,
        "excel": ExportFormat.EXCEL,
        "csv": ExportFormat.CSV,
    }
    export_format = format_map.get(request.format.value, ExportFormat.PDF)

    result = await use_case.export_competitor_report(
        competitor_id=competitor_id,
        modality_id=request.modality_id,
        format=export_format,
        start_date=request.start_date,
        end_date=request.end_date,
    )

    return Response(
        content=result.content,
        media_type=result.content_type,
        headers={"Content-Disposition": f'attachment; filename="{result.filename}"'},
    )


@router.post(
    "/export/modality/{modality_id}",
    summary="Export modality report",
    description="Export comprehensive modality report.",
)
async def export_modality_report(
    modality_id: UUID,
    request: ExportModalityReportRequest,
    current_user: Annotated[User, Depends(require_evaluator)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Response:
    """Export modality report."""
    use_case = ExportReportUseCase(
        analytics_repository=SQLAlchemyAnalyticsRepository(db),
        competitor_repository=SQLAlchemyCompetitorRepository(db),
        modality_repository=SQLAlchemyModalityRepository(db),
    )

    format_map = {
        "pdf": ExportFormat.PDF,
        "excel": ExportFormat.EXCEL,
        "csv": ExportFormat.CSV,
    }
    export_format = format_map.get(request.format.value, ExportFormat.PDF)

    result = await use_case.export_modality_report(
        modality_id=modality_id,
        format=export_format,
        include_ranking=request.include_ranking,
    )

    return Response(
        content=result.content,
        media_type=result.content_type,
        headers={"Content-Disposition": f'attachment; filename="{result.filename}"'},
    )


@router.post(
    "/export/ranking/{modality_id}",
    summary="Export ranking",
    description="Export ranking data.",
)
async def export_ranking(
    modality_id: UUID,
    request: ExportRankingRequest,
    current_user: Annotated[User, Depends(require_evaluator)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Response:
    """Export ranking."""
    use_case = ExportReportUseCase(
        analytics_repository=SQLAlchemyAnalyticsRepository(db),
        competitor_repository=SQLAlchemyCompetitorRepository(db),
        modality_repository=SQLAlchemyModalityRepository(db),
    )

    format_map = {
        "pdf": ExportFormat.PDF,
        "excel": ExportFormat.EXCEL,
        "csv": ExportFormat.CSV,
    }
    export_format = format_map.get(request.format.value, ExportFormat.EXCEL)

    result = await use_case.export_ranking(
        modality_id=modality_id,
        format=export_format,
        limit=request.limit,
    )

    return Response(
        content=result.content,
        media_type=result.content_type,
        headers={"Content-Disposition": f'attachment; filename="{result.filename}"'},
    )
