"""Get competitor grades use case."""

from uuid import UUID

from src.application.assessment.dtos.grade_dto import GradeDTO, GradeListDTO
from src.domain.assessment.repositories.grade_repository import GradeRepository
from src.domain.modality.exceptions import CompetitorNotFoundException
from src.domain.modality.repositories.competitor_repository import CompetitorRepository


class GetCompetitorGradesUseCase:
    """Use case for getting a competitor's grades.

    This use case retrieves grades for a specific competitor.
    """

    def __init__(
        self,
        grade_repository: GradeRepository,
        competitor_repository: CompetitorRepository,
    ) -> None:
        self._grade_repository = grade_repository
        self._competitor_repository = competitor_repository

    async def execute(
        self,
        competitor_id: UUID,
        exam_id: UUID | None = None,
        competence_id: UUID | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> GradeListDTO:
        """Get grades for a competitor.

        Args:
            competitor_id: ID of the competitor.
            exam_id: Optional exam filter.
            competence_id: Optional competence filter.
            skip: Number of records to skip.
            limit: Maximum records to return.

        Returns:
            GradeListDTO with paginated results.

        Raises:
            CompetitorNotFoundException: If competitor not found.
        """
        # Validate competitor exists
        competitor = await self._competitor_repository.get_by_id(competitor_id)
        if not competitor:
            raise CompetitorNotFoundException(str(competitor_id))

        # Get grades
        grades = await self._grade_repository.get_by_competitor(
            competitor_id=competitor_id,
            exam_id=exam_id,
            competence_id=competence_id,
            skip=skip,
            limit=limit,
        )

        # Get total count
        total = await self._grade_repository.count(
            competitor_id=competitor_id,
            exam_id=exam_id,
            competence_id=competence_id,
        )

        return GradeListDTO(
            grades=[GradeDTO.from_entity(g) for g in grades],
            total=total,
            skip=skip,
            limit=limit,
        )
