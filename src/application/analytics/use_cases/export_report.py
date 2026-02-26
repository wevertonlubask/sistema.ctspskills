"""Export report use case."""

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Any
from uuid import UUID

from src.domain.analytics.repositories.analytics_repository import AnalyticsRepository
from src.domain.analytics.value_objects.date_range import DateRange
from src.domain.modality.exceptions import CompetitorNotFoundException, ModalityNotFoundException
from src.domain.modality.repositories.competitor_repository import CompetitorRepository
from src.domain.modality.repositories.modality_repository import ModalityRepository


class ExportFormat(str, Enum):
    """Supported export formats."""

    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"


class ReportType(str, Enum):
    """Available report types."""

    COMPETITOR_SUMMARY = "competitor_summary"
    MODALITY_SUMMARY = "modality_summary"
    RANKING = "ranking"
    GRADES_EVOLUTION = "grades_evolution"
    TRAINING_HOURS = "training_hours"
    COMPETENCE_MAP = "competence_map"


@dataclass
class ExportResult:
    """Result of an export operation."""

    content: bytes
    filename: str
    content_type: str
    format: ExportFormat


class ExportReportUseCase:
    """Use case for exporting analytics reports."""

    CONTENT_TYPES = {
        ExportFormat.PDF: "application/pdf",
        ExportFormat.EXCEL: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ExportFormat.CSV: "text/csv",
    }

    FILE_EXTENSIONS = {
        ExportFormat.PDF: ".pdf",
        ExportFormat.EXCEL: ".xlsx",
        ExportFormat.CSV: ".csv",
    }

    def __init__(
        self,
        analytics_repository: AnalyticsRepository,
        competitor_repository: CompetitorRepository,
        modality_repository: ModalityRepository,
    ) -> None:
        self._analytics_repository = analytics_repository
        self._competitor_repository = competitor_repository
        self._modality_repository = modality_repository

    async def export_competitor_report(
        self,
        competitor_id: UUID,
        modality_id: UUID | None = None,
        format: ExportFormat = ExportFormat.PDF,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> ExportResult:
        """Export comprehensive competitor report.

        Args:
            competitor_id: Competitor UUID.
            modality_id: Optional modality filter.
            format: Export format (PDF, Excel, CSV).
            start_date: Optional start date.
            end_date: Optional end date.

        Returns:
            ExportResult with file content.

        Raises:
            CompetitorNotFoundException: If competitor not found.
        """
        # Validate competitor exists
        competitor = await self._competitor_repository.get_by_id(competitor_id)
        if not competitor:
            raise CompetitorNotFoundException(str(competitor_id))

        # Validate modality if provided
        if modality_id:
            modality = await self._modality_repository.get_by_id(modality_id)
            if not modality:
                raise ModalityNotFoundException(str(modality_id))

        # Get summary data
        summary_data = await self._analytics_repository.get_competitor_summary(
            competitor_id=competitor_id,
            modality_id=modality_id,
        )

        # Get additional data if date range provided
        date_range = None
        if start_date and end_date:
            date_range = DateRange(start_date=start_date, end_date=end_date)

        # Generate report content
        content = await self._generate_competitor_report(
            competitor=competitor,
            summary_data=summary_data,
            date_range=date_range,
            format=format,
        )

        filename = f"competitor_report_{competitor_id}{self.FILE_EXTENSIONS[format]}"

        return ExportResult(
            content=content,
            filename=filename,
            content_type=self.CONTENT_TYPES[format],
            format=format,
        )

    async def export_modality_report(
        self,
        modality_id: UUID,
        format: ExportFormat = ExportFormat.PDF,
        include_ranking: bool = True,
    ) -> ExportResult:
        """Export comprehensive modality report.

        Args:
            modality_id: Modality UUID.
            format: Export format.
            include_ranking: Whether to include full ranking.

        Returns:
            ExportResult with file content.

        Raises:
            ModalityNotFoundException: If modality not found.
        """
        # Validate modality exists
        modality = await self._modality_repository.get_by_id(modality_id)
        if not modality:
            raise ModalityNotFoundException(str(modality_id))

        # Get summary data
        summary_data = await self._analytics_repository.get_modality_summary(
            modality_id=modality_id,
        )

        # Get ranking if requested
        ranking = None
        if include_ranking:
            ranking = await self._analytics_repository.get_ranking(
                modality_id=modality_id,
                limit=100,
            )

        # Generate report content
        content = await self._generate_modality_report(
            modality=modality,
            summary_data=summary_data,
            ranking=ranking,
            format=format,
        )

        filename = f"modality_report_{modality_id}{self.FILE_EXTENSIONS[format]}"

        return ExportResult(
            content=content,
            filename=filename,
            content_type=self.CONTENT_TYPES[format],
            format=format,
        )

    async def export_ranking(
        self,
        modality_id: UUID,
        format: ExportFormat = ExportFormat.EXCEL,
        limit: int = 100,
    ) -> ExportResult:
        """Export ranking data.

        Args:
            modality_id: Modality UUID.
            format: Export format.
            limit: Maximum entries.

        Returns:
            ExportResult with file content.
        """
        # Validate modality exists
        modality = await self._modality_repository.get_by_id(modality_id)
        if not modality:
            raise ModalityNotFoundException(str(modality_id))

        # Get ranking
        ranking = await self._analytics_repository.get_ranking(
            modality_id=modality_id,
            limit=limit,
        )

        # Generate content based on format
        if format == ExportFormat.CSV:
            content = self._ranking_to_csv(ranking)
        elif format == ExportFormat.EXCEL:
            content = await self._ranking_to_excel(ranking)
        else:
            content = await self._ranking_to_pdf(ranking)

        filename = f"ranking_{modality_id}{self.FILE_EXTENSIONS[format]}"

        return ExportResult(
            content=content,
            filename=filename,
            content_type=self.CONTENT_TYPES[format],
            format=format,
        )

    # =========================================================================
    # Private generation methods
    # =========================================================================

    async def _generate_competitor_report(
        self,
        competitor: Any,
        summary_data: dict,
        date_range: DateRange | None,
        format: ExportFormat,
    ) -> bytes:
        """Generate competitor report content."""
        if format == ExportFormat.CSV:
            return self._competitor_summary_to_csv(competitor, summary_data)
        elif format == ExportFormat.EXCEL:
            return await self._competitor_summary_to_excel(competitor, summary_data)
        else:
            return await self._competitor_summary_to_pdf(competitor, summary_data)

    async def _generate_modality_report(
        self,
        modality: Any,
        summary_data: dict,
        ranking: Any,
        format: ExportFormat,
    ) -> bytes:
        """Generate modality report content."""
        if format == ExportFormat.CSV:
            return self._modality_summary_to_csv(modality, summary_data, ranking)
        elif format == ExportFormat.EXCEL:
            return await self._modality_summary_to_excel(modality, summary_data, ranking)
        else:
            return await self._modality_summary_to_pdf(modality, summary_data, ranking)

    def _competitor_summary_to_csv(self, competitor: Any, summary_data: dict) -> bytes:
        """Convert competitor summary to CSV."""
        lines = [
            "Metric,Value",
            f"Competitor ID,{competitor.id}",
            f"Name,{competitor.full_name}",
            f"Grades Average,{summary_data.get('grades_average', 0.0)}",
            f"Grades Total,{summary_data.get('grades_total', 0)}",
            f"Grades Max,{summary_data.get('grades_max', 0.0)}",
            f"Grades Min,{summary_data.get('grades_min', 0.0)}",
            f"Training Hours,{summary_data.get('training_total_hours', 0.0)}",
            f"Training Sessions,{summary_data.get('training_total_sessions', 0)}",
            f"Exams Participated,{summary_data.get('exams_participated', 0)}",
        ]
        return "\n".join(lines).encode("utf-8")

    def _modality_summary_to_csv(self, modality: Any, summary_data: dict, ranking: Any) -> bytes:
        """Convert modality summary to CSV."""
        lines = [
            "Metric,Value",
            f"Modality ID,{modality.id}",
            f"Name,{modality.name}",
            f"Active Competitors,{summary_data.get('active_competitors', 0)}",
            f"Active Exams,{summary_data.get('active_exams', 0)}",
            f"Grades Average,{summary_data.get('grades_average', 0.0)}",
            f"Grades Total,{summary_data.get('grades_total', 0)}",
            f"Training Hours,{summary_data.get('training_total_hours', 0.0)}",
            "",
        ]

        if ranking:
            lines.append("Ranking")
            lines.append("Position,Competitor,Score")
            for entry in ranking.entries:
                lines.append(f"{entry.position},{entry.competitor_name},{entry.score}")

        return "\n".join(lines).encode("utf-8")

    def _ranking_to_csv(self, ranking: Any) -> bytes:
        """Convert ranking to CSV."""
        lines = [
            f"Ranking - {ranking.modality_name}",
            f"Generated at: {ranking.generated_at.isoformat()}",
            "",
            "Position,Competitor ID,Competitor Name,Score,Position Change",
        ]

        for entry in ranking.entries:
            change = entry.position_change if entry.position_change is not None else "N/A"
            lines.append(
                f"{entry.position},{entry.competitor_id},{entry.competitor_name},"
                f"{entry.score},{change}"
            )

        return "\n".join(lines).encode("utf-8")

    async def _competitor_summary_to_excel(self, competitor: Any, summary_data: dict) -> bytes:
        """Convert competitor summary to Excel."""
        # Note: This would use openpyxl or xlsxwriter in a real implementation
        # For now, return CSV as placeholder
        return self._competitor_summary_to_csv(competitor, summary_data)

    async def _modality_summary_to_excel(
        self, modality: Any, summary_data: dict, ranking: Any
    ) -> bytes:
        """Convert modality summary to Excel."""
        return self._modality_summary_to_csv(modality, summary_data, ranking)

    async def _ranking_to_excel(self, ranking: Any) -> bytes:
        """Convert ranking to Excel."""
        return self._ranking_to_csv(ranking)

    async def _competitor_summary_to_pdf(self, competitor: Any, summary_data: dict) -> bytes:
        """Convert competitor summary to PDF."""
        # Note: This would use reportlab or weasyprint in a real implementation
        # For now, return a placeholder
        return b"PDF content placeholder"

    async def _modality_summary_to_pdf(
        self, modality: Any, summary_data: dict, ranking: Any
    ) -> bytes:
        """Convert modality summary to PDF."""
        return b"PDF content placeholder"

    async def _ranking_to_pdf(self, ranking: Any) -> bytes:
        """Convert ranking to PDF."""
        return b"PDF content placeholder"
