"""Register grade use case."""

from uuid import UUID

from src.application.assessment.dtos.grade_dto import GradeDTO, RegisterGradeDTO
from src.domain.assessment.entities.grade import Grade
from src.domain.assessment.entities.grade_audit_log import GradeAuditLog
from src.domain.assessment.exceptions import (
    CompetenceNotInExamException,
    CompetitorNotInModalityException,
    EvaluatorCannotGradeException,
    ExamNotActiveException,
    ExamNotFoundException,
    GradeAlreadyExistsException,
)
from src.domain.assessment.repositories.exam_repository import ExamRepository
from src.domain.assessment.repositories.grade_audit_repository import GradeAuditLogRepository
from src.domain.assessment.repositories.grade_repository import GradeRepository
from src.domain.assessment.value_objects.score import Score
from src.domain.modality.repositories.competence_repository import CompetenceRepository
from src.domain.modality.repositories.competitor_repository import CompetitorRepository
from src.domain.modality.repositories.enrollment_repository import EnrollmentRepository


class RegisterGradeUseCase:
    """Use case for registering a grade.

    This use case allows evaluators to register grades for competitors.

    Business Rules:
    - RN02: Evaluator must be assigned to the competitor's modality
    - RN03: Score must be between 0 and 100
    - RN08: Competence must be part of the exam
    """

    def __init__(
        self,
        exam_repository: ExamRepository,
        grade_repository: GradeRepository,
        audit_repository: GradeAuditLogRepository,
        enrollment_repository: EnrollmentRepository,
        competitor_repository: CompetitorRepository,
        competence_repository: CompetenceRepository | None = None,
    ) -> None:
        self._exam_repository = exam_repository
        self._grade_repository = grade_repository
        self._audit_repository = audit_repository
        self._enrollment_repository = enrollment_repository
        self._competitor_repository = competitor_repository
        self._competence_repository = competence_repository

    async def execute(
        self,
        evaluator_id: UUID,
        dto: RegisterGradeDTO,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> GradeDTO:
        """Register a grade.

        Args:
            evaluator_id: ID of the evaluator registering the grade.
            dto: Grade registration data.
            ip_address: Optional IP address for audit.
            user_agent: Optional user agent for audit.

        Returns:
            Created grade DTO.

        Raises:
            ExamNotFoundException: If exam not found.
            ExamNotActiveException: If exam is not active.
            CompetenceNotInExamException: If competence not in exam (RN08).
            EvaluatorCannotGradeException: If evaluator not assigned (RN02).
            GradeAlreadyExistsException: If grade already exists.
        """
        # 1. Get and validate exam exists and is active
        exam = await self._exam_repository.get_by_id(dto.exam_id)
        if not exam:
            raise ExamNotFoundException(str(dto.exam_id))

        if not exam.is_active:
            raise ExamNotActiveException(str(dto.exam_id))

        # 2. Validate competence is part of the exam (RN08)
        # If exam has no specific competences assigned, allow any competence from the modality
        if exam.competence_ids:
            # Exam has specific competences - validate against them
            if not exam.has_competence(dto.competence_id):
                raise CompetenceNotInExamException(
                    competence_id=str(dto.competence_id),
                    exam_id=str(dto.exam_id),
                )
        elif self._competence_repository:
            # Exam has no specific competences - validate against modality competences
            competence = await self._competence_repository.get_by_id(dto.competence_id)
            if not competence or competence.modality_id != exam.modality_id:
                raise CompetenceNotInExamException(
                    competence_id=str(dto.competence_id),
                    exam_id=str(dto.exam_id),
                )

        # 3. Validate competitor is enrolled in the modality
        enrollment = await self._enrollment_repository.get_by_competitor_and_modality(
            competitor_id=dto.competitor_id,
            modality_id=exam.modality_id,
        )
        if not enrollment:
            raise CompetitorNotInModalityException(
                competitor_id=str(dto.competitor_id),
                modality_id=str(exam.modality_id),
            )

        # 4. Validate evaluator can grade this competitor (RN02)
        # Evaluator must be assigned to the competitor's enrollment
        if enrollment.evaluator_id != evaluator_id:
            # Check if evaluator has another enrollment with this modality
            evaluator_enrollments = await self._enrollment_repository.get_by_evaluator(
                evaluator_id=evaluator_id,
            )
            modality_ids = {e.modality_id for e in evaluator_enrollments}
            if exam.modality_id not in modality_ids:
                raise EvaluatorCannotGradeException(
                    evaluator_id=str(evaluator_id),
                    competitor_id=str(dto.competitor_id),
                )

        # 5. Check if grade already exists
        exists = await self._grade_repository.exists_for_exam_competitor_competence(
            exam_id=dto.exam_id,
            competitor_id=dto.competitor_id,
            competence_id=dto.competence_id,
        )
        if exists:
            raise GradeAlreadyExistsException(
                exam_id=str(dto.exam_id),
                competitor_id=str(dto.competitor_id),
                competence_id=str(dto.competence_id),
            )

        # 6. Create score value object (validates range - RN03)
        score = Score(dto.score)

        # 7. Create and save grade
        grade = Grade(
            exam_id=dto.exam_id,
            competitor_id=dto.competitor_id,
            competence_id=dto.competence_id,
            score=score,
            notes=dto.notes,
            created_by=evaluator_id,
        )

        created_grade = await self._grade_repository.add(grade)

        # 8. Create audit log
        audit_log = GradeAuditLog.create_for_new_grade(
            grade_id=created_grade.id,
            score=score.value,
            notes=dto.notes,
            created_by=evaluator_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await self._audit_repository.add(audit_log)

        return GradeDTO.from_entity(created_grade)
