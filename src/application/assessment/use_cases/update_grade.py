"""Update grade use case."""

from uuid import UUID

from src.application.assessment.dtos.grade_dto import GradeDTO, UpdateGradeDTO
from src.domain.assessment.entities.grade_audit_log import GradeAuditLog
from src.domain.assessment.exceptions import (
    EvaluatorCannotGradeException,
    ExamNotActiveException,
    ExamNotFoundException,
    GradeNotFoundException,
)
from src.domain.assessment.repositories.exam_repository import ExamRepository
from src.domain.assessment.repositories.grade_audit_repository import GradeAuditLogRepository
from src.domain.assessment.repositories.grade_repository import GradeRepository
from src.domain.assessment.value_objects.score import Score
from src.domain.modality.repositories.enrollment_repository import EnrollmentRepository


class UpdateGradeUseCase:
    """Use case for updating a grade.

    This use case allows evaluators to update existing grades.

    Business Rules:
    - RN02: Evaluator must be assigned to the competitor's modality
    - RN03: Score must be between 0 and 100
    """

    def __init__(
        self,
        exam_repository: ExamRepository,
        grade_repository: GradeRepository,
        audit_repository: GradeAuditLogRepository,
        enrollment_repository: EnrollmentRepository,
    ) -> None:
        self._exam_repository = exam_repository
        self._grade_repository = grade_repository
        self._audit_repository = audit_repository
        self._enrollment_repository = enrollment_repository

    async def execute(
        self,
        grade_id: UUID,
        evaluator_id: UUID,
        dto: UpdateGradeDTO,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> GradeDTO:
        """Update a grade.

        Args:
            grade_id: ID of the grade to update.
            evaluator_id: ID of the evaluator updating the grade.
            dto: Grade update data.
            ip_address: Optional IP address for audit.
            user_agent: Optional user agent for audit.

        Returns:
            Updated grade DTO.

        Raises:
            GradeNotFoundException: If grade not found.
            ExamNotFoundException: If exam not found.
            ExamNotActiveException: If exam is not active.
            EvaluatorCannotGradeException: If evaluator not assigned (RN02).
        """
        # 1. Get and validate grade exists
        grade = await self._grade_repository.get_by_id(grade_id)
        if not grade:
            raise GradeNotFoundException(str(grade_id))

        # 2. Get and validate exam is active
        exam = await self._exam_repository.get_by_id(grade.exam_id)
        if not exam:
            raise ExamNotFoundException(str(grade.exam_id))

        if not exam.is_active:
            raise ExamNotActiveException(str(grade.exam_id))

        # 3. Validate evaluator can grade this competitor (RN02)
        enrollment = await self._enrollment_repository.get_by_competitor_and_modality(
            competitor_id=grade.competitor_id,
            modality_id=exam.modality_id,
        )
        if enrollment and enrollment.evaluator_id != evaluator_id:
            # Check if evaluator has access to this modality
            evaluator_enrollments = await self._enrollment_repository.get_by_evaluator(
                evaluator_id=evaluator_id,
            )
            modality_ids = {e.modality_id for e in evaluator_enrollments}
            if exam.modality_id not in modality_ids:
                raise EvaluatorCannotGradeException(
                    evaluator_id=str(evaluator_id),
                    competitor_id=str(grade.competitor_id),
                )

        # 4. Track old values for audit
        old_score = grade.score.value
        old_notes = grade.notes

        # 5. Update grade
        new_score_value = dto.score if dto.score is not None else old_score
        new_notes = dto.notes if dto.notes is not None else old_notes

        if dto.score is not None:
            new_score = Score(dto.score)  # Validates range (RN03)
            grade.update_score(new_score, evaluator_id)

        if dto.notes is not None:
            grade.update_notes(dto.notes, evaluator_id)

        updated_grade = await self._grade_repository.update(grade)

        # 6. Create audit log
        audit_log = GradeAuditLog.create_for_update(
            grade_id=updated_grade.id,
            old_score=old_score,
            new_score=new_score_value,
            old_notes=old_notes,
            new_notes=new_notes,
            updated_by=evaluator_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await self._audit_repository.add(audit_log)

        return GradeDTO.from_entity(updated_grade)
