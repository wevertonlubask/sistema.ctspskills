"""Grades router."""

from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.assessment.dtos.grade_dto import (
    RegisterGradeDTO,
    UpdateGradeDTO,
)
from src.application.assessment.use_cases import (
    CalculateAverageUseCase,
    GetCompetitorGradesUseCase,
    GetGradeHistoryUseCase,
    RegisterGradeUseCase,
    UpdateGradeUseCase,
)
from src.domain.identity.entities.user import User
from src.infrastructure.database.repositories import (
    SQLAlchemyCompetenceRepository,
    SQLAlchemyCompetitorRepository,
    SQLAlchemyEnrollmentRepository,
    SQLAlchemyExamRepository,
    SQLAlchemyGradeAuditLogRepository,
    SQLAlchemyGradeRepository,
)
from src.presentation.api.v1.dependencies.auth import (
    get_current_active_user,
    require_evaluator,
)
from src.presentation.api.v1.dependencies.database import get_db
from src.presentation.schemas.assessment_schema import (
    CompetitorAverageResponse,
    CompetitorExamSummaryResponse,
    GradeAuditResponse,
    GradeHistoryResponse,
    GradeListResponse,
    GradeResponse,
    RegisterGradeRequest,
    UpdateGradeRequest,
)
from src.shared.constants.enums import UserRole

router = APIRouter()


def grade_dto_to_response(dto: Any) -> GradeResponse:
    """Convert GradeDTO to response model."""
    return GradeResponse(
        id=dto.id,
        exam_id=dto.exam_id,
        competitor_id=dto.competitor_id,
        competence_id=dto.competence_id,
        score=dto.score,
        notes=dto.notes,
        created_by=dto.created_by,
        updated_by=dto.updated_by,
        created_at=dto.created_at,
        updated_at=dto.updated_at,
    )


@router.post(
    "",
    response_model=GradeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register grade",
    description="Register a new grade for a competitor. Requires evaluator role. (RN02, RN03, RN08)",
)
async def register_grade(
    data: RegisterGradeRequest,
    request: Request,
    current_user: Annotated[User, Depends(require_evaluator)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> GradeResponse:
    """Register a new grade."""
    use_case = RegisterGradeUseCase(
        exam_repository=SQLAlchemyExamRepository(db),
        grade_repository=SQLAlchemyGradeRepository(db),
        audit_repository=SQLAlchemyGradeAuditLogRepository(db),
        enrollment_repository=SQLAlchemyEnrollmentRepository(db),
        competitor_repository=SQLAlchemyCompetitorRepository(db),
        competence_repository=SQLAlchemyCompetenceRepository(db),
    )

    dto = RegisterGradeDTO(
        exam_id=data.exam_id,
        competitor_id=data.competitor_id,
        competence_id=data.competence_id,
        score=data.score,
        notes=data.notes,
    )

    # Get client info for audit
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    result = await use_case.execute(
        evaluator_id=current_user.id,
        dto=dto,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.commit()

    return grade_dto_to_response(result)


@router.get(
    "",
    response_model=GradeListResponse,
    summary="List grades",
    description="List grades with filters. Evaluators can filter by exam_id.",
)
async def list_grades(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    competitor_id: UUID | None = Query(default=None),
    exam_id: UUID | None = Query(default=None),
    competence_id: UUID | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
) -> GradeListResponse:
    """List grades."""
    # If competitor, filter to own grades
    target_competitor_id = competitor_id
    if current_user.role == UserRole.COMPETITOR:
        competitor_repo = SQLAlchemyCompetitorRepository(db)
        competitor = await competitor_repo.get_by_user_id(current_user.id)
        if competitor:
            target_competitor_id = competitor.id

    # Evaluators and admins can list grades by exam_id without competitor_id
    if not target_competitor_id and not exam_id:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either competitor_id or exam_id is required",
        )

    grade_repo = SQLAlchemyGradeRepository(db)

    # If filtering by exam only (evaluator/admin)
    if exam_id and not target_competitor_id:
        grades = await grade_repo.get_by_exam(
            exam_id=exam_id,
            skip=skip,
            limit=limit,
        )
        total = await grade_repo.count(exam_id=exam_id)
        from src.application.assessment.dtos.grade_dto import GradeDTO

        return GradeListResponse(
            grades=[grade_dto_to_response(GradeDTO.from_entity(g)) for g in grades],
            total=total,
            skip=skip,
            limit=limit,
            has_more=(skip + len(grades)) < total,
        )

    use_case = GetCompetitorGradesUseCase(
        grade_repository=grade_repo,
        competitor_repository=SQLAlchemyCompetitorRepository(db),
    )

    result = await use_case.execute(
        competitor_id=target_competitor_id,  # type: ignore[arg-type]
        exam_id=exam_id,
        competence_id=competence_id,
        skip=skip,
        limit=limit,
    )

    return GradeListResponse(
        grades=[grade_dto_to_response(g) for g in result.grades],
        total=result.total,
        skip=result.skip,
        limit=result.limit,
        has_more=result.has_more,
    )


@router.get(
    "/{grade_id}",
    response_model=GradeResponse,
    summary="Get grade",
    description="Get a single grade by ID.",
)
async def get_grade(
    grade_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> GradeResponse:
    """Get grade by ID."""
    grade_repo = SQLAlchemyGradeRepository(db)
    grade = await grade_repo.get_by_id(grade_id)

    if not grade:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Grade with ID {grade_id} not found",
        )

    from src.application.assessment.dtos.grade_dto import GradeDTO

    return grade_dto_to_response(GradeDTO.from_entity(grade))


@router.put(
    "/{grade_id}",
    response_model=GradeResponse,
    summary="Update grade",
    description="Update an existing grade. Requires evaluator role. (RN02, RN03)",
)
async def update_grade(
    grade_id: UUID,
    data: UpdateGradeRequest,
    request: Request,
    current_user: Annotated[User, Depends(require_evaluator)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> GradeResponse:
    """Update a grade."""
    use_case = UpdateGradeUseCase(
        exam_repository=SQLAlchemyExamRepository(db),
        grade_repository=SQLAlchemyGradeRepository(db),
        audit_repository=SQLAlchemyGradeAuditLogRepository(db),
        enrollment_repository=SQLAlchemyEnrollmentRepository(db),
    )

    dto = UpdateGradeDTO(
        score=data.score,
        notes=data.notes,
    )

    # Get client info for audit
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    result = await use_case.execute(
        grade_id=grade_id,
        evaluator_id=current_user.id,
        dto=dto,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await db.commit()

    return grade_dto_to_response(result)


@router.get(
    "/{grade_id}/history",
    response_model=GradeHistoryResponse,
    summary="Get grade history",
    description="Get audit history for a grade. Requires evaluator role.",
)
async def get_grade_history(
    grade_id: UUID,
    current_user: Annotated[User, Depends(require_evaluator)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> GradeHistoryResponse:
    """Get grade audit history."""
    use_case = GetGradeHistoryUseCase(
        grade_repository=SQLAlchemyGradeRepository(db),
        audit_repository=SQLAlchemyGradeAuditLogRepository(db),
    )

    result = await use_case.execute(grade_id)

    return GradeHistoryResponse(
        grade=grade_dto_to_response(result.grade),
        history=[
            GradeAuditResponse(
                id=h.id,
                grade_id=h.grade_id,
                action=h.action,
                old_score=h.old_score,
                new_score=h.new_score,
                old_notes=h.old_notes,
                new_notes=h.new_notes,
                changed_by=h.changed_by,
                ip_address=h.ip_address,
                user_agent=h.user_agent,
                changed_at=h.changed_at,
            )
            for h in result.history
        ],
    )


@router.get(
    "/competitor/{competitor_id}/average",
    response_model=CompetitorAverageResponse,
    summary="Get competitor average",
    description="Get average score for a competitor.",
)
async def get_competitor_average(
    competitor_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    modality_id: UUID | None = Query(default=None),
    competence_id: UUID | None = Query(default=None),
) -> CompetitorAverageResponse:
    """Get competitor average."""
    use_case = CalculateAverageUseCase(
        grade_repository=SQLAlchemyGradeRepository(db),
        exam_repository=SQLAlchemyExamRepository(db),
        competitor_repository=SQLAlchemyCompetitorRepository(db),
    )

    result = await use_case.competitor_average(
        competitor_id=competitor_id,
        modality_id=modality_id,
        competence_id=competence_id,
    )

    return CompetitorAverageResponse(
        competitor_id=result.competitor_id,
        average=result.average,
        modality_id=result.modality_id,
        competence_id=result.competence_id,
    )


@router.get(
    "/competitor/{competitor_id}/exam/{exam_id}/summary",
    response_model=CompetitorExamSummaryResponse,
    summary="Get competitor exam summary",
    description="Get summary of a competitor's performance in an exam.",
)
async def get_competitor_exam_summary(
    competitor_id: UUID,
    exam_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CompetitorExamSummaryResponse:
    """Get competitor exam summary."""
    use_case = CalculateAverageUseCase(
        grade_repository=SQLAlchemyGradeRepository(db),
        exam_repository=SQLAlchemyExamRepository(db),
        competitor_repository=SQLAlchemyCompetitorRepository(db),
    )

    result = await use_case.exam_competitor_summary(
        competitor_id=competitor_id,
        exam_id=exam_id,
    )

    return CompetitorExamSummaryResponse(
        competitor_id=result.competitor_id,
        exam_id=result.exam_id,
        grades_count=result.grades_count,
        average=result.average,
        weighted_average=result.weighted_average,
    )
