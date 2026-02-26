"""Get exam use case."""

from uuid import UUID

from src.application.assessment.dtos.exam_dto import ExamDTO
from src.domain.assessment.exceptions import ExamNotFoundException
from src.domain.assessment.repositories.exam_repository import ExamRepository


class GetExamUseCase:
    """Use case for getting an exam by ID.

    This use case retrieves a single exam's details.
    """

    def __init__(
        self,
        exam_repository: ExamRepository,
    ) -> None:
        self._exam_repository = exam_repository

    async def execute(
        self,
        exam_id: UUID,
    ) -> ExamDTO:
        """Get an exam by ID.

        Args:
            exam_id: ID of the exam to retrieve.

        Returns:
            ExamDTO with exam details.

        Raises:
            ExamNotFoundException: If exam not found.
        """
        exam = await self._exam_repository.get_by_id(exam_id)
        if not exam:
            raise ExamNotFoundException(str(exam_id))

        return ExamDTO.from_entity(exam)
