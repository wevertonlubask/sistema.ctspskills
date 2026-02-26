"""List competitors use case."""

from uuid import UUID

from src.application.modality.dtos.competitor_dto import CompetitorDTO, CompetitorListDTO
from src.domain.modality.repositories.competitor_repository import CompetitorRepository


class ListCompetitorsUseCase:
    """Use case for listing competitors."""

    def __init__(self, competitor_repository: CompetitorRepository) -> None:
        self._competitor_repository = competitor_repository

    async def execute(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False,
        modality_id: UUID | None = None,
        search: str | None = None,
    ) -> CompetitorListDTO:
        """List competitors with pagination and filtering.

        Args:
            skip: Number of records to skip.
            limit: Maximum records to return.
            active_only: Only return active competitors.
            modality_id: Filter by modality enrollment.
            search: Optional search query.

        Returns:
            Competitor list DTO.
        """
        if search:
            competitors = await self._competitor_repository.search(
                query=search, skip=skip, limit=limit
            )
            total = len(competitors)
        elif modality_id:
            competitors = await self._competitor_repository.get_by_modality(
                modality_id=modality_id, skip=skip, limit=limit
            )
            total = len(competitors)
        else:
            competitors = await self._competitor_repository.get_all(
                skip=skip, limit=limit, active_only=active_only
            )
            total = await self._competitor_repository.count(active_only=active_only)

        return CompetitorListDTO(
            competitors=[CompetitorDTO.from_entity(c) for c in competitors],
            total=total,
            skip=skip,
            limit=limit,
        )
