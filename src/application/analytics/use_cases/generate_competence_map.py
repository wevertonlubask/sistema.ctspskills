"""Generate competence map use case."""

from uuid import UUID

from src.application.analytics.dtos.chart_dto import CompetenceComparisonDTO, CompetenceMapDTO
from src.domain.analytics.repositories.analytics_repository import AnalyticsRepository
from src.domain.modality.exceptions import CompetitorNotFoundException, ModalityNotFoundException
from src.domain.modality.repositories.competitor_repository import CompetitorRepository
from src.domain.modality.repositories.modality_repository import ModalityRepository


class GenerateCompetenceMapUseCase:
    """Use case for generating competence map (radar chart)."""

    def __init__(
        self,
        analytics_repository: AnalyticsRepository,
        competitor_repository: CompetitorRepository,
        modality_repository: ModalityRepository,
    ) -> None:
        self._analytics_repository = analytics_repository
        self._competitor_repository = competitor_repository
        self._modality_repository = modality_repository

    async def execute(
        self,
        competitor_id: UUID,
        modality_id: UUID,
        exam_id: UUID | None = None,
    ) -> CompetenceMapDTO:
        """Generate competence map data for radar chart.

        Args:
            competitor_id: Competitor UUID.
            modality_id: Modality UUID.
            exam_id: Optional specific exam filter.

        Returns:
            CompetenceMapDTO with competence scores.

        Raises:
            CompetitorNotFoundException: If competitor not found.
            ModalityNotFoundException: If modality not found.
        """
        # Validate competitor exists
        competitor = await self._competitor_repository.get_by_id(competitor_id)
        if not competitor:
            raise CompetitorNotFoundException(str(competitor_id))

        # Validate modality exists
        modality = await self._modality_repository.get_by_id(modality_id)
        if not modality:
            raise ModalityNotFoundException(str(modality_id))

        # Get competence map
        comp_map = await self._analytics_repository.get_competence_map(
            competitor_id=competitor_id,
            modality_id=modality_id,
            exam_id=exam_id,
        )

        return CompetenceMapDTO.from_domain(comp_map)

    async def compare(
        self,
        competitor_ids: list[UUID],
        modality_id: UUID,
    ) -> CompetenceComparisonDTO:
        """Generate competence maps for multiple competitors.

        Args:
            competitor_ids: List of competitor UUIDs.
            modality_id: Modality UUID.

        Returns:
            CompetenceComparisonDTO with maps for all competitors.
        """
        # Validate modality exists
        modality = await self._modality_repository.get_by_id(modality_id)
        if not modality:
            raise ModalityNotFoundException(str(modality_id))

        # Get comparison data
        maps = await self._analytics_repository.get_competence_comparison(
            competitor_ids=competitor_ids,
            modality_id=modality_id,
        )

        return CompetenceComparisonDTO(
            maps=[CompetenceMapDTO.from_domain(m) for m in maps],
            competitor_ids=[str(c) for c in competitor_ids],
            modality_id=str(modality_id),
        )
