"""Exams router."""

from datetime import date
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.assessment.dtos.exam_dto import (
    CreateExamDTO,
    UpdateExamDTO,
)
from src.application.assessment.use_cases import (
    CreateExamUseCase,
    GetExamStatisticsUseCase,
    GetExamUseCase,
    ListExamsUseCase,
    UpdateExamUseCase,
)
from src.domain.identity.entities.user import User
from sqlalchemy import select

from src.infrastructure.database.models.assessment_model import ExamCompetitorTimeModel
from src.infrastructure.database.repositories import (
    SQLAlchemyCompetenceRepository,
    SQLAlchemyExamRepository,
    SQLAlchemyGradeRepository,
    SQLAlchemyModalityRepository,
)
from src.infrastructure.database.base import GUID
from src.presentation.api.v1.dependencies.auth import (
    get_current_active_user,
    require_evaluator,
)
from src.presentation.api.v1.dependencies.database import get_db
from src.presentation.schemas.assessment_schema import (
    CompetenceStatisticsResponse,
    CompetitorTimeResponse,
    CreateExamRequest,
    ExamListResponse,
    ExamResponse,
    ExamStatisticsResponse,
    ExamTimesResponse,
    SetCompetitorTimeRequest,
    UpdateExamRequest,
)
from src.presentation.schemas.common import MessageResponse

router = APIRouter()


def exam_dto_to_response(dto: Any) -> ExamResponse:
    """Convert ExamDTO to response model."""
    return ExamResponse(
        id=dto.id,
        name=dto.name,
        description=dto.description,
        modality_id=dto.modality_id,
        assessment_type=dto.assessment_type,
        exam_date=dto.exam_date,
        is_active=dto.is_active,
        competence_ids=dto.competence_ids,
        created_by=dto.created_by,
        created_at=dto.created_at,
        updated_at=dto.updated_at,
        time_limit_minutes=dto.time_limit_minutes,
    )


@router.post(
    "",
    response_model=ExamResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create exam",
    description="Create a new exam. Requires evaluator role.",
)
async def create_exam(
    data: CreateExamRequest,
    current_user: Annotated[User, Depends(require_evaluator)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ExamResponse:
    """Create a new exam."""
    use_case = CreateExamUseCase(
        exam_repository=SQLAlchemyExamRepository(db),
        modality_repository=SQLAlchemyModalityRepository(db),
        competence_repository=SQLAlchemyCompetenceRepository(db),
    )

    dto = CreateExamDTO(
        name=data.name,
        modality_id=data.modality_id,
        assessment_type=data.assessment_type,
        exam_date=data.exam_date,
        description=data.description,
        competence_ids=data.competence_ids,
        time_limit_minutes=data.time_limit_minutes,
    )

    result = await use_case.execute(current_user.id, dto)
    await db.commit()

    return exam_dto_to_response(result)


@router.get(
    "",
    response_model=ExamListResponse,
    summary="List exams",
    description="List exams with filters.",
)
async def list_exams(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    modality_id: UUID | None = Query(default=None),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    active_only: bool = Query(default=True),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
) -> ExamListResponse:
    """List exams."""
    use_case = ListExamsUseCase(
        exam_repository=SQLAlchemyExamRepository(db),
    )

    result = await use_case.execute(
        modality_id=modality_id,
        start_date=start_date,
        end_date=end_date,
        active_only=active_only,
        skip=skip,
        limit=limit,
    )

    return ExamListResponse(
        exams=[exam_dto_to_response(e) for e in result.exams],
        total=result.total,
        skip=result.skip,
        limit=result.limit,
        has_more=result.has_more,
    )


@router.get(
    "/{exam_id}",
    response_model=ExamResponse,
    summary="Get exam",
    description="Get a single exam by ID.",
)
async def get_exam(
    exam_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ExamResponse:
    """Get exam by ID."""
    use_case = GetExamUseCase(
        exam_repository=SQLAlchemyExamRepository(db),
    )

    result = await use_case.execute(exam_id)
    return exam_dto_to_response(result)


@router.put(
    "/{exam_id}",
    response_model=ExamResponse,
    summary="Update exam",
    description="Update an exam. Requires evaluator role.",
)
async def update_exam(
    exam_id: UUID,
    data: UpdateExamRequest,
    current_user: Annotated[User, Depends(require_evaluator)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ExamResponse:
    """Update an exam."""
    use_case = UpdateExamUseCase(
        exam_repository=SQLAlchemyExamRepository(db),
        competence_repository=SQLAlchemyCompetenceRepository(db),
    )

    dto = UpdateExamDTO(
        name=data.name,
        description=data.description,
        exam_date=data.exam_date,
        assessment_type=data.assessment_type,
        competence_ids=data.competence_ids,
        is_active=data.is_active,
        time_limit_minutes=data.time_limit_minutes,
    )

    result = await use_case.execute(exam_id, dto)
    await db.commit()

    return exam_dto_to_response(result)


@router.delete(
    "/{exam_id}",
    response_model=MessageResponse,
    summary="Deactivate exam",
    description="Deactivate an exam (soft delete). Requires evaluator role.",
)
async def deactivate_exam(
    exam_id: UUID,
    current_user: Annotated[User, Depends(require_evaluator)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MessageResponse:
    """Deactivate an exam."""
    use_case = UpdateExamUseCase(
        exam_repository=SQLAlchemyExamRepository(db),
        competence_repository=SQLAlchemyCompetenceRepository(db),
    )

    dto = UpdateExamDTO(is_active=False)
    await use_case.execute(exam_id, dto)
    await db.commit()

    return MessageResponse(message="Exam deactivated successfully")


@router.get(
    "/{exam_id}/statistics",
    response_model=ExamStatisticsResponse,
    summary="Get exam statistics",
    description="Get comprehensive statistics for an exam. Requires evaluator role.",
)
async def get_exam_statistics(
    exam_id: UUID,
    current_user: Annotated[User, Depends(require_evaluator)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ExamStatisticsResponse:
    """Get exam statistics."""
    use_case = GetExamStatisticsUseCase(
        exam_repository=SQLAlchemyExamRepository(db),
        grade_repository=SQLAlchemyGradeRepository(db),
    )

    result = await use_case.execute(exam_id)

    return ExamStatisticsResponse(
        exam_id=result.exam_id,
        total_competitors=result.total_competitors,
        total_grades=result.total_grades,
        overall_average=result.overall_average,
        competence_stats=[
            CompetenceStatisticsResponse(
                competence_id=cs.competence_id,
                average=cs.average,
                median=cs.median,
                std_deviation=cs.std_deviation,
                min_score=cs.min_score,
                max_score=cs.max_score,
                count=cs.count,
            )
            for cs in result.competence_stats
        ],
    )


@router.get(
    "/{exam_id}/times",
    response_model=ExamTimesResponse,
    summary="Get competitor times for an exam",
)
async def get_exam_times(
    exam_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ExamTimesResponse:
    """Get all competitor durations for an exam."""
    from src.infrastructure.database.models.assessment_model import ExamCompetitorTimeModel  # noqa: PLC0415
    stmt = select(ExamCompetitorTimeModel).where(ExamCompetitorTimeModel.exam_id == exam_id)
    result = await db.execute(stmt)
    times = result.scalars().all()
    return ExamTimesResponse(
        exam_id=exam_id,
        times=[
            CompetitorTimeResponse(
                exam_id=t.exam_id,
                competitor_id=t.competitor_id,
                duration_minutes=t.duration_minutes,
                created_at=t.created_at,
                updated_at=t.updated_at,
            )
            for t in times
        ],
    )


@router.post(
    "/{exam_id}/times",
    response_model=CompetitorTimeResponse,
    summary="Set competitor time for an exam",
    status_code=status.HTTP_200_OK,
)
async def set_competitor_time(
    exam_id: UUID,
    data: SetCompetitorTimeRequest,
    current_user: Annotated[User, Depends(require_evaluator)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CompetitorTimeResponse:
    """Upsert a competitor's duration for an exam."""
    from src.infrastructure.database.models.assessment_model import ExamCompetitorTimeModel  # noqa: PLC0415
    from uuid import uuid4  # noqa: PLC0415

    stmt = select(ExamCompetitorTimeModel).where(
        ExamCompetitorTimeModel.exam_id == exam_id,
        ExamCompetitorTimeModel.competitor_id == data.competitor_id,
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        existing.duration_minutes = data.duration_minutes
        record = existing
    else:
        record = ExamCompetitorTimeModel(
            id=uuid4(),
            exam_id=exam_id,
            competitor_id=data.competitor_id,
            duration_minutes=data.duration_minutes,
        )
        db.add(record)

    await db.flush()
    await db.commit()

    return CompetitorTimeResponse(
        exam_id=record.exam_id,
        competitor_id=record.competitor_id,
        duration_minutes=record.duration_minutes,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )
