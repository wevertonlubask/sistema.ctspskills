"""Competitors router."""

from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.modality.dtos.competitor_dto import CreateCompetitorDTO
from src.application.modality.use_cases import (
    CreateCompetitorUseCase,
    ListCompetitorsUseCase,
)
from src.domain.identity.entities.user import User
from src.infrastructure.database.repositories import (
    SQLAlchemyCompetitorRepository,
    SQLAlchemyUserRepository,
)
from src.presentation.api.v1.dependencies.auth import (
    get_current_active_user,
    require_evaluator,
)
from src.presentation.api.v1.dependencies.database import get_db
from src.presentation.schemas.modality_schema import (
    CompetitorListResponse,
    CompetitorResponse,
    CreateCompetitorRequest,
    EnrollmentDetailResponse,
    EnrollmentListResponse,
)

router = APIRouter()


def competitor_dto_to_response(dto: Any, email: str | None = None) -> CompetitorResponse:
    """Convert competitor DTO to response model."""
    return CompetitorResponse(
        id=dto.id,
        user_id=dto.user_id,
        email=email,
        full_name=dto.full_name,
        birth_date=dto.birth_date,
        document_number=dto.document_number,
        phone=dto.phone,
        emergency_contact=dto.emergency_contact,
        emergency_phone=dto.emergency_phone,
        notes=dto.notes,
        is_active=dto.is_active,
        age=dto.age,
        created_at=dto.created_at,
        updated_at=dto.updated_at,
    )


@router.post(
    "",
    response_model=CompetitorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create competitor",
    description="Create a competitor profile for a user. Requires evaluator or super admin role.",
)
async def create_competitor(
    data: CreateCompetitorRequest,
    current_user: Annotated[User, Depends(require_evaluator)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CompetitorResponse:
    """Create a competitor profile."""
    use_case = CreateCompetitorUseCase(
        competitor_repository=SQLAlchemyCompetitorRepository(db),
        user_repository=SQLAlchemyUserRepository(db),
    )

    dto = CreateCompetitorDTO(
        user_id=data.user_id,
        full_name=data.full_name,
        birth_date=data.birth_date,
        document_number=data.document_number,
        phone=data.phone,
        emergency_contact=data.emergency_contact,
        emergency_phone=data.emergency_phone,
        notes=data.notes,
    )

    result = await use_case.execute(dto)
    await db.commit()

    return competitor_dto_to_response(result)


@router.get(
    "",
    response_model=CompetitorListResponse,
    summary="List competitors",
    description="List all competitors with pagination and filtering.",
)
async def list_competitors(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    active_only: bool = Query(default=False),
    modality_id: UUID | None = Query(default=None),
    search: str | None = Query(default=None, max_length=100),
) -> CompetitorListResponse:
    """List competitors."""
    use_case = ListCompetitorsUseCase(
        competitor_repository=SQLAlchemyCompetitorRepository(db),
    )

    result = await use_case.execute(
        skip=skip,
        limit=limit,
        active_only=active_only,
        modality_id=modality_id,
        search=search,
    )

    # Fetch emails for all competitors
    from sqlalchemy import select

    from src.infrastructure.database.models.user_model import UserModel

    user_ids = [c.user_id for c in result.competitors]
    if user_ids:
        stmt = select(UserModel.id, UserModel.email).where(UserModel.id.in_(user_ids))
        user_result = await db.execute(stmt)
        user_emails = {row.id: row.email for row in user_result.all()}
    else:
        user_emails = {}

    return CompetitorListResponse(
        competitors=[
            competitor_dto_to_response(c, email=user_emails.get(c.user_id))
            for c in result.competitors
        ],
        total=result.total,
        skip=result.skip,
        limit=result.limit,
        has_more=result.has_more,
    )


@router.get(
    "/{competitor_id}",
    response_model=CompetitorResponse,
    summary="Get competitor",
    description="Get a single competitor by ID.",
)
async def get_competitor(
    competitor_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CompetitorResponse:
    """Get competitor by ID."""
    repository = SQLAlchemyCompetitorRepository(db)
    competitor = await repository.get_by_id(competitor_id)

    if not competitor:
        from src.domain.modality.exceptions import CompetitorNotFoundException

        raise CompetitorNotFoundException(identifier=str(competitor_id))

    # Fetch email from user
    from sqlalchemy import select

    from src.infrastructure.database.models.user_model import UserModel

    stmt = select(UserModel.email).where(UserModel.id == competitor.user_id)
    result = await db.execute(stmt)
    email = result.scalar()

    from src.application.modality.dtos.competitor_dto import CompetitorDTO

    return competitor_dto_to_response(CompetitorDTO.from_entity(competitor), email=email)


@router.get(
    "/{competitor_id}/enrollments",
    response_model=EnrollmentListResponse,
    summary="Get competitor enrollments",
    description="Get all modality enrollments for a competitor.",
)
async def get_competitor_enrollments(
    competitor_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> EnrollmentListResponse:
    """Get all enrollments for a competitor."""
    import logging

    logger = logging.getLogger(__name__)

    from sqlalchemy import select

    from src.domain.modality.entities.enrollment import EnrollmentStatus
    from src.infrastructure.database.models.modality_model import (
        CompetitorModel,
        EnrollmentModel,
        ModalityModel,
    )
    from src.infrastructure.database.models.user_model import UserModel

    logger.info(f"[Enrollments] Fetching enrollments for competitor_id: {competitor_id}")

    # First, check if there are any enrollments for this competitor (simple query)
    simple_stmt = select(EnrollmentModel).where(EnrollmentModel.competitor_id == competitor_id)
    simple_result = await db.execute(simple_stmt)
    simple_rows = simple_result.scalars().all()
    logger.info(f"[Enrollments] Simple query found {len(simple_rows)} enrollments")
    for row in simple_rows:
        logger.info(
            f"[Enrollments] Enrollment: id={row.id}, modality_id={row.modality_id}, evaluator_id={row.evaluator_id}"
        )

    # Build query with joins
    stmt = (
        select(
            EnrollmentModel,
            CompetitorModel.full_name.label("competitor_name"),
            ModalityModel.name.label("modality_name"),
            ModalityModel.code.label("modality_code"),
            UserModel.full_name.label("evaluator_name"),
        )
        .join(CompetitorModel, EnrollmentModel.competitor_id == CompetitorModel.id)
        .join(ModalityModel, EnrollmentModel.modality_id == ModalityModel.id)
        .outerjoin(UserModel, EnrollmentModel.evaluator_id == UserModel.id)
        .where(EnrollmentModel.competitor_id == competitor_id)
        .order_by(EnrollmentModel.enrolled_at.desc())
    )

    result = await db.execute(stmt)
    rows = result.all()
    logger.info(f"[Enrollments] Join query found {len(rows)} enrollments")

    enrollments = [
        EnrollmentDetailResponse(
            id=row.EnrollmentModel.id,
            competitor_id=row.EnrollmentModel.competitor_id,
            competitor_name=row.competitor_name,
            modality_id=row.EnrollmentModel.modality_id,
            modality_name=row.modality_name,
            modality_code=row.modality_code,
            evaluator_id=row.EnrollmentModel.evaluator_id,
            evaluator_name=row.evaluator_name,
            enrolled_at=row.EnrollmentModel.enrolled_at,
            status=EnrollmentStatus(row.EnrollmentModel.status),
            notes=row.EnrollmentModel.notes,
            created_at=row.EnrollmentModel.created_at,
            updated_at=row.EnrollmentModel.updated_at,
        )
        for row in rows
    ]

    return EnrollmentListResponse(
        enrollments=enrollments,
        total=len(enrollments),
        skip=0,
        limit=len(enrollments),
        has_more=False,
    )
