"""Create exam use case."""

from uuid import UUID

from src.application.assessment.dtos.exam_dto import CreateExamDTO, ExamDTO
from src.domain.assessment.entities.exam import Exam
from src.domain.assessment.repositories.exam_repository import ExamRepository
from src.domain.modality.exceptions import ModalityNotFoundException
from src.domain.modality.repositories.competence_repository import CompetenceRepository
from src.domain.modality.repositories.modality_repository import ModalityRepository


class CreateExamUseCase:
    """Use case for creating an exam.

    This use case allows evaluators to create assessment exams.
    """

    def __init__(
        self,
        exam_repository: ExamRepository,
        modality_repository: ModalityRepository,
        competence_repository: CompetenceRepository,
    ) -> None:
        self._exam_repository = exam_repository
        self._modality_repository = modality_repository
        self._competence_repository = competence_repository

    async def execute(
        self,
        user_id: UUID,
        dto: CreateExamDTO,
    ) -> ExamDTO:
        """Create an exam.

        Args:
            user_id: ID of the user creating the exam.
            dto: Exam creation data.

        Returns:
            Created exam DTO.

        Raises:
            ModalityNotFoundException: If modality not found.
        """
        # Validate modality exists
        modality = await self._modality_repository.get_by_id(dto.modality_id)
        if not modality:
            raise ModalityNotFoundException(str(dto.modality_id))

        # Validate competences belong to the modality (if provided)
        valid_competence_ids = []
        if dto.competence_ids:
            for comp_id in dto.competence_ids:
                competence = await self._competence_repository.get_by_id(comp_id)
                if competence and competence.modality_id == dto.modality_id:
                    valid_competence_ids.append(comp_id)

        # Create exam
        exam = Exam(
            name=dto.name,
            modality_id=dto.modality_id,
            assessment_type=dto.assessment_type,
            exam_date=dto.exam_date,
            created_by=user_id,
            description=dto.description,
            competence_ids=valid_competence_ids,
        )

        # Save and return
        created = await self._exam_repository.add(exam)
        return ExamDTO.from_entity(created)
