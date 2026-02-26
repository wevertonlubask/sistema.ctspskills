"""SQLAlchemy Analytics repository implementation (CQRS read-side)."""

from datetime import date, datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.analytics.entities.performance_metric import (
    CompetenceMap,
    CompetenceScore,
    Ranking,
    RankingEntry,
    TimeSeries,
    TimeSeriesPoint,
    TrainingHoursSummary,
)
from src.domain.analytics.repositories.analytics_repository import AnalyticsRepository
from src.domain.analytics.services.aggregation_service import AggregationService
from src.domain.analytics.value_objects.date_range import DateRange
from src.domain.analytics.value_objects.metric_type import AggregationPeriod, MetricType
from src.infrastructure.database.models.assessment_model import ExamModel, GradeModel
from src.infrastructure.database.models.modality_model import (
    CompetenceModel,
    CompetitorModel,
    EnrollmentModel,
    ModalityModel,
)
from src.infrastructure.database.models.training_model import TrainingSessionModel


class SQLAlchemyAnalyticsRepository(AnalyticsRepository):
    """SQLAlchemy implementation of AnalyticsRepository.

    Optimized for complex read queries and aggregations.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ==========================================================================
    # Grade Evolution Queries
    # ==========================================================================

    async def get_grade_evolution(
        self,
        competitor_id: UUID,
        date_range: DateRange,
        period: AggregationPeriod = AggregationPeriod.MONTHLY,
        modality_id: UUID | None = None,
        competence_id: UUID | None = None,
    ) -> TimeSeries:
        """Get grade evolution over time for a competitor."""
        # Query grades with exam dates
        stmt = (
            select(
                GradeModel.score,
                ExamModel.exam_date,
            )
            .join(ExamModel, GradeModel.exam_id == ExamModel.id)
            .where(
                GradeModel.competitor_id == competitor_id,
                ExamModel.exam_date >= date_range.start_date,
                ExamModel.exam_date <= date_range.end_date,
            )
        )

        if modality_id:
            stmt = stmt.where(ExamModel.modality_id == modality_id)
        if competence_id:
            stmt = stmt.where(GradeModel.competence_id == competence_id)

        stmt = stmt.order_by(ExamModel.exam_date)

        result = await self._session.execute(stmt)
        rows = result.all()

        # Convert to time series
        data = [(row.exam_date, row.score) for row in rows]
        points = AggregationService.aggregate_by_period(data, period)

        # Get competitor name
        competitor = await self._session.get(CompetitorModel, competitor_id)
        name = competitor.full_name if competitor else "Unknown"

        return TimeSeries(
            name=name,
            points=points,
            metric_type=MetricType.GRADE_AVERAGE,
        )

    async def get_grades_comparison(
        self,
        competitor_ids: list[UUID],
        date_range: DateRange,
        modality_id: UUID | None = None,
    ) -> list[TimeSeries]:
        """Get grade evolution for multiple competitors."""
        series_list = []

        for comp_id in competitor_ids:
            series = await self.get_grade_evolution(
                competitor_id=comp_id,
                date_range=date_range,
                modality_id=modality_id,
            )
            series_list.append(series)

        return series_list

    # ==========================================================================
    # Training Hours Queries
    # ==========================================================================

    async def get_training_hours_evolution(
        self,
        competitor_id: UUID,
        date_range: DateRange,
        period: AggregationPeriod = AggregationPeriod.MONTHLY,
        modality_id: UUID | None = None,
    ) -> tuple[TimeSeries, TimeSeries]:
        """Get training hours evolution (SENAI vs External)."""
        stmt = select(
            TrainingSessionModel.hours,
            TrainingSessionModel.training_date,
            TrainingSessionModel.training_type,
            TrainingSessionModel.status,
        ).where(
            TrainingSessionModel.competitor_id == competitor_id,
            TrainingSessionModel.training_date >= date_range.start_date,
            TrainingSessionModel.training_date <= date_range.end_date,
            TrainingSessionModel.status == "approved",
        )

        if modality_id:
            stmt = stmt.where(TrainingSessionModel.modality_id == modality_id)

        stmt = stmt.order_by(TrainingSessionModel.training_date)

        result = await self._session.execute(stmt)
        rows = result.all()

        # Separate SENAI and external
        senai_data = [
            (row.training_date, row.hours) for row in rows if row.training_type == "senai"
        ]
        external_data = [
            (row.training_date, row.hours) for row in rows if row.training_type == "external"
        ]

        # Aggregate by period (sum hours instead of average)
        senai_groups: dict[str, float] = {}
        senai_dates: dict[str, date] = {}
        for d, hours in senai_data:
            key = AggregationService._get_period_key(d, period)
            senai_groups[key] = senai_groups.get(key, 0) + hours
            senai_dates[key] = d

        external_groups: dict[str, float] = {}
        external_dates: dict[str, date] = {}
        for d, hours in external_data:
            key = AggregationService._get_period_key(d, period)
            external_groups[key] = external_groups.get(key, 0) + hours
            external_dates[key] = d

        senai_points = [
            TimeSeriesPoint(date=senai_dates[k], value=round(v, 2), label=k)
            for k, v in sorted(senai_groups.items())
        ]
        external_points = [
            TimeSeriesPoint(date=external_dates[k], value=round(v, 2), label=k)
            for k, v in sorted(external_groups.items())
        ]

        senai_series = TimeSeries(
            name="SENAI",
            points=senai_points,
            metric_type=MetricType.TRAINING_HOURS_SENAI,
        )
        external_series = TimeSeries(
            name="External",
            points=external_points,
            metric_type=MetricType.TRAINING_HOURS_EXTERNAL,
        )

        return senai_series, external_series

    async def get_training_hours_summary(
        self,
        competitor_id: UUID,
        date_range: DateRange | None = None,
        modality_id: UUID | None = None,
    ) -> TrainingHoursSummary:
        """Get comprehensive training hours summary."""
        stmt = select(
            TrainingSessionModel.hours,
            TrainingSessionModel.training_type,
            TrainingSessionModel.status,
        ).where(TrainingSessionModel.competitor_id == competitor_id)

        if date_range:
            stmt = stmt.where(
                TrainingSessionModel.training_date >= date_range.start_date,
                TrainingSessionModel.training_date <= date_range.end_date,
            )
        if modality_id:
            stmt = stmt.where(TrainingSessionModel.modality_id == modality_id)

        result = await self._session.execute(stmt)
        rows = result.all()

        total_hours = sum(r.hours for r in rows)
        senai_hours = sum(r.hours for r in rows if r.training_type == "senai")
        external_hours = sum(r.hours for r in rows if r.training_type == "external")
        approved_hours = sum(r.hours for r in rows if r.status == "approved")
        pending_hours = sum(r.hours for r in rows if r.status == "pending")
        rejected_hours = sum(r.hours for r in rows if r.status == "rejected")
        sessions_count = len(rows)
        approved_count = len([r for r in rows if r.status == "approved"])
        approval_rate = (approved_count / sessions_count * 100) if sessions_count > 0 else 0

        return TrainingHoursSummary(
            competitor_id=competitor_id,
            total_hours=round(total_hours, 2),
            senai_hours=round(senai_hours, 2),
            external_hours=round(external_hours, 2),
            approved_hours=round(approved_hours, 2),
            pending_hours=round(pending_hours, 2),
            rejected_hours=round(rejected_hours, 2),
            sessions_count=sessions_count,
            approval_rate=round(approval_rate, 2),
        )

    # ==========================================================================
    # Competence Map Queries
    # ==========================================================================

    async def get_competence_map(
        self,
        competitor_id: UUID,
        modality_id: UUID,
        exam_id: UUID | None = None,
    ) -> CompetenceMap:
        """Get competence scores for radar chart."""
        # Get grades with competence info
        stmt = (
            select(
                GradeModel.score,
                CompetenceModel.id.label("competence_id"),
                CompetenceModel.name.label("competence_name"),
                CompetenceModel.max_score,
                CompetenceModel.weight,
            )
            .join(CompetenceModel, GradeModel.competence_id == CompetenceModel.id)
            .join(ExamModel, GradeModel.exam_id == ExamModel.id)
            .where(
                GradeModel.competitor_id == competitor_id,
                ExamModel.modality_id == modality_id,
            )
        )

        if exam_id:
            stmt = stmt.where(GradeModel.exam_id == exam_id)

        result = await self._session.execute(stmt)
        rows = result.all()

        # Group by competence
        competence_scores: dict[UUID, list[float]] = {}
        competence_info: dict[UUID, dict] = {}

        for row in rows:
            comp_id = row.competence_id
            if comp_id not in competence_scores:
                competence_scores[comp_id] = []
                competence_info[comp_id] = {
                    "name": row.competence_name,
                    "max_score": row.max_score,
                    "weight": row.weight,
                }
            competence_scores[comp_id].append(row.score)

        # Calculate averages
        competences = []
        for comp_id, scores in competence_scores.items():
            info = competence_info[comp_id]
            avg_score = sum(scores) / len(scores)
            competences.append(
                CompetenceScore(
                    competence_id=comp_id,
                    competence_name=info["name"],
                    score=round(avg_score, 2),
                    max_score=info["max_score"],
                    weight=info["weight"],
                )
            )

        # Get competitor name
        competitor = await self._session.get(CompetitorModel, competitor_id)
        name = competitor.full_name if competitor else "Unknown"

        all_scores = [c.normalized_score for c in competences]
        overall_avg = sum(all_scores) / len(all_scores) if all_scores else 0.0

        return CompetenceMap(
            competitor_id=competitor_id,
            competitor_name=name,
            competences=competences,
            overall_average=round(overall_avg, 2),
        )

    async def get_competence_comparison(
        self,
        competitor_ids: list[UUID],
        modality_id: UUID,
    ) -> list[CompetenceMap]:
        """Get competence maps for multiple competitors."""
        maps = []
        for comp_id in competitor_ids:
            comp_map = await self.get_competence_map(
                competitor_id=comp_id,
                modality_id=modality_id,
            )
            maps.append(comp_map)
        return maps

    # ==========================================================================
    # Ranking Queries
    # ==========================================================================

    async def get_ranking(
        self,
        modality_id: UUID,
        date_range: DateRange | None = None,
        limit: int = 50,
    ) -> Ranking:
        """Get competitor ranking for a modality."""
        # Query average grades per competitor
        stmt = (
            select(
                GradeModel.competitor_id,
                CompetitorModel.full_name,
                func.avg(GradeModel.score).label("avg_score"),
            )
            .join(CompetitorModel, GradeModel.competitor_id == CompetitorModel.id)
            .join(ExamModel, GradeModel.exam_id == ExamModel.id)
            .where(ExamModel.modality_id == modality_id)
        )

        if date_range:
            stmt = stmt.where(
                ExamModel.exam_date >= date_range.start_date,
                ExamModel.exam_date <= date_range.end_date,
            )

        stmt = stmt.group_by(GradeModel.competitor_id, CompetitorModel.full_name)
        stmt = stmt.order_by(func.avg(GradeModel.score).desc())
        stmt = stmt.limit(limit)

        result = await self._session.execute(stmt)
        rows = result.all()

        # Get modality name
        modality = await self._session.get(ModalityModel, modality_id)
        modality_name = modality.name if modality else "Unknown"

        entries = [
            RankingEntry(
                position=i + 1,
                competitor_id=row.competitor_id,
                competitor_name=row.full_name,
                score=round(float(row.avg_score), 2),
                modality_id=modality_id,
            )
            for i, row in enumerate(rows)
        ]

        return Ranking(
            modality_id=modality_id,
            modality_name=modality_name,
            entries=entries,
            generated_at=datetime.utcnow(),
        )

    async def get_competitor_ranking_history(
        self,
        competitor_id: UUID,
        modality_id: UUID,
        date_range: DateRange,
        period: AggregationPeriod = AggregationPeriod.MONTHLY,
    ) -> TimeSeries:
        """Get ranking position evolution for a competitor."""
        # This would require historical ranking snapshots
        # For now, return empty series (could be implemented with materialized views)
        return TimeSeries(
            name="Ranking Position",
            points=[],
            metric_type=MetricType.RANKING_POSITION,
        )

    # ==========================================================================
    # Summary/Dashboard Queries
    # ==========================================================================

    async def get_competitor_summary(
        self,
        competitor_id: UUID,
        modality_id: UUID | None = None,
    ) -> dict:
        """Get comprehensive summary for a competitor dashboard."""
        # Grade stats
        grade_stmt = select(
            func.avg(GradeModel.score).label("avg_score"),
            func.count(GradeModel.id).label("total_grades"),
            func.max(GradeModel.score).label("max_score"),
            func.min(GradeModel.score).label("min_score"),
        ).where(GradeModel.competitor_id == competitor_id)

        if modality_id:
            grade_stmt = grade_stmt.join(ExamModel, GradeModel.exam_id == ExamModel.id).where(
                ExamModel.modality_id == modality_id
            )

        grade_result = await self._session.execute(grade_stmt)
        grade_row = grade_result.one_or_none()

        # Training stats
        training_stmt = select(
            func.sum(TrainingSessionModel.hours).label("total_hours"),
            func.count(TrainingSessionModel.id).label("total_sessions"),
        ).where(
            TrainingSessionModel.competitor_id == competitor_id,
            TrainingSessionModel.status == "approved",
        )

        if modality_id:
            training_stmt = training_stmt.where(TrainingSessionModel.modality_id == modality_id)

        training_result = await self._session.execute(training_stmt)
        training_row = training_result.one_or_none()

        # Exam count
        exam_stmt = select(func.count(func.distinct(GradeModel.exam_id))).where(
            GradeModel.competitor_id == competitor_id
        )
        exam_result = await self._session.execute(exam_stmt)
        exam_count = exam_result.scalar() or 0

        return {
            "competitor_id": str(competitor_id),
            "modality_id": str(modality_id) if modality_id else None,
            "grades": {
                "average": round(float(grade_row.avg_score or 0), 2) if grade_row else 0.0,  # type: ignore[union-attr]
                "total": (grade_row.total_grades or 0) if grade_row else 0,  # type: ignore[union-attr]
                "max": round(float(grade_row.max_score or 0), 2) if grade_row else 0.0,  # type: ignore[union-attr]
                "min": round(float(grade_row.min_score or 0), 2) if grade_row else 0.0,  # type: ignore[union-attr]
            },
            "training": {
                "total_hours": round(float(training_row.total_hours or 0), 2) if training_row else 0.0,  # type: ignore[union-attr]
                "total_sessions": (training_row.total_sessions or 0) if training_row else 0,  # type: ignore[union-attr]
            },
            "exams_participated": exam_count,
        }

    async def get_modality_summary(
        self,
        modality_id: UUID,
    ) -> dict:
        """Get comprehensive summary for a modality dashboard."""
        # Competitor count
        enrollment_stmt = select(func.count(func.distinct(EnrollmentModel.competitor_id))).where(
            EnrollmentModel.modality_id == modality_id,
            EnrollmentModel.status == "active",
        )
        enrollment_result = await self._session.execute(enrollment_stmt)
        competitor_count = enrollment_result.scalar() or 0

        # Exam count
        exam_stmt = select(func.count(ExamModel.id)).where(
            ExamModel.modality_id == modality_id,
            ExamModel.is_active == True,  # noqa: E712
        )
        exam_result = await self._session.execute(exam_stmt)
        exam_count = exam_result.scalar() or 0

        # Grade stats
        grade_stmt = (
            select(
                func.avg(GradeModel.score).label("avg_score"),
                func.count(GradeModel.id).label("total_grades"),
            )
            .join(ExamModel, GradeModel.exam_id == ExamModel.id)
            .where(ExamModel.modality_id == modality_id)
        )
        grade_result = await self._session.execute(grade_stmt)
        grade_row = grade_result.one_or_none()

        # Training stats
        training_stmt = select(
            func.sum(TrainingSessionModel.hours).label("total_hours"),
        ).where(
            TrainingSessionModel.modality_id == modality_id,
            TrainingSessionModel.status == "approved",
        )
        training_result = await self._session.execute(training_stmt)
        training_row = training_result.one_or_none()

        # Get modality name
        modality = await self._session.get(ModalityModel, modality_id)
        modality_name = modality.name if modality else "Unknown"

        return {
            "modality_id": str(modality_id),
            "modality_name": modality_name,
            "competitors": {
                "active_count": competitor_count,
            },
            "exams": {
                "active_count": exam_count,
            },
            "grades": {
                "average": round(float(grade_row.avg_score or 0), 2) if grade_row else 0.0,  # type: ignore[union-attr]
                "total": (grade_row.total_grades or 0) if grade_row else 0,  # type: ignore[union-attr]
            },
            "training": {
                "total_hours": round(float(training_row.total_hours or 0), 2) if training_row else 0.0,  # type: ignore[union-attr]
            },
        }
