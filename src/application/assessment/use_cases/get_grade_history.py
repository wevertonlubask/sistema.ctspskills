"""Get grade history use case."""

from uuid import UUID

from src.application.assessment.dtos.grade_dto import (
    GradeAuditDTO,
    GradeDTO,
    GradeHistoryDTO,
)
from src.domain.assessment.exceptions import GradeNotFoundException
from src.domain.assessment.repositories.grade_audit_repository import GradeAuditLogRepository
from src.domain.assessment.repositories.grade_repository import GradeRepository


class GetGradeHistoryUseCase:
    """Use case for getting grade history.

    This use case retrieves the audit history for a grade.
    """

    def __init__(
        self,
        grade_repository: GradeRepository,
        audit_repository: GradeAuditLogRepository,
    ) -> None:
        self._grade_repository = grade_repository
        self._audit_repository = audit_repository

    async def execute(
        self,
        grade_id: UUID,
    ) -> GradeHistoryDTO:
        """Get history for a grade.

        Args:
            grade_id: ID of the grade.

        Returns:
            GradeHistoryDTO with grade and audit history.

        Raises:
            GradeNotFoundException: If grade not found.
        """
        # Get grade
        grade = await self._grade_repository.get_by_id(grade_id)
        if not grade:
            raise GradeNotFoundException(str(grade_id))

        # Get audit history
        history = await self._audit_repository.get_grade_history(grade_id)

        return GradeHistoryDTO(
            grade=GradeDTO.from_entity(grade),
            history=[GradeAuditDTO.from_entity(h) for h in history],
        )
