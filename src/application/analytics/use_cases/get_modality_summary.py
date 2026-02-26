"""Get modality summary use case."""

from uuid import UUID

from src.application.analytics.dtos.chart_dto import ModalitySummaryDTO
from src.domain.analytics.repositories.analytics_repository import AnalyticsRepository
from src.domain.modality.exceptions import ModalityNotFoundException
from src.domain.modality.repositories.modality_repository import ModalityRepository


class GetModalitySummaryUseCase:
    """Use case for getting modality dashboard summary."""

    def __init__(
        self,
        analytics_repository: AnalyticsRepository,
        modality_repository: ModalityRepository,
    ) -> None:
        self._analytics_repository = analytics_repository
        self._modality_repository = modality_repository

    async def execute(
        self,
        modality_id: UUID,
    ) -> ModalitySummaryDTO:
        """Get comprehensive summary for a modality.

        Args:
            modality_id: Modality UUID.

        Returns:
            ModalitySummaryDTO with all summary metrics.

        Raises:
            ModalityNotFoundException: If modality not found.
        """
        # Validate modality exists
        modality = await self._modality_repository.get_by_id(modality_id)
        if not modality:
            raise ModalityNotFoundException(str(modality_id))

        # Get summary data from repository
        summary_data = await self._analytics_repository.get_modality_summary(
            modality_id=modality_id,
        )

        return ModalitySummaryDTO(
            modality_id=str(modality_id),
            modality_name=summary_data.get("modality_name", modality.name),
            active_competitors=summary_data.get("active_competitors", 0),
            active_exams=summary_data.get("active_exams", 0),
            grades_average=summary_data.get("grades_average", 0.0),
            grades_total=summary_data.get("grades_total", 0),
            training_total_hours=summary_data.get("training_total_hours", 0.0),
        )
