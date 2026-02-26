"""Update exam use case."""

from uuid import UUID

from src.application.assessment.dtos.exam_dto import ExamDTO, UpdateExamDTO
from src.domain.assessment.exceptions import ExamNotFoundException
from src.domain.assessment.repositories.exam_repository import ExamRepository
from src.domain.modality.repositories.competence_repository import CompetenceRepository


class UpdateExamUseCase:
    """Use case for updating an exam.

    This use case allows evaluators to update assessment exams.
    """

    def __init__(
        self,
        exam_repository: ExamRepository,
        competence_repository: CompetenceRepository,
    ) -> None:
        self._exam_repository = exam_repository
        self._competence_repository = competence_repository

    async def execute(
        self,
        exam_id: UUID,
        dto: UpdateExamDTO,
    ) -> ExamDTO:
        """Update an exam.

        Args:
            exam_id: ID of the exam to update.
            dto: Exam update data.

        Returns:
            Updated exam DTO.

        Raises:
            ExamNotFoundException: If exam not found.
        """
        # Get exam
        exam = await self._exam_repository.get_by_id(exam_id)
        if not exam:
            raise ExamNotFoundException(str(exam_id))

        # Update basic fields
        exam.update(
            name=dto.name,
            description=dto.description,
            exam_date=dto.exam_date,
            assessment_type=dto.assessment_type,
        )

        # Update active status if provided
        if dto.is_active is not None:
            if dto.is_active:
                exam.activate()
            else:
                exam.deactivate()

        # Update competences if provided
        if dto.competence_ids is not None:
            # Clear current competences
            for comp_id in list(exam.competence_ids):
                exam.remove_competence(comp_id)

            # Add valid competences
            for comp_id in dto.competence_ids:
                competence = await self._competence_repository.get_by_id(comp_id)
                if competence and competence.modality_id == exam.modality_id:
                    exam.add_competence(comp_id)

        # Save and return
        updated = await self._exam_repository.update(exam)
        return ExamDTO.from_entity(updated)
