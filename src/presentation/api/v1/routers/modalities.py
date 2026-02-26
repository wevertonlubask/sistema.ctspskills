"""Modalities router."""

from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.modality.dtos.competence_dto import CreateCompetenceDTO
from src.application.modality.dtos.enrollment_dto import EnrollCompetitorDTO
from src.application.modality.dtos.modality_dto import (
    CreateModalityDTO,
    UpdateModalityDTO,
)
from src.application.modality.use_cases import (
    AddCompetenceUseCase,
    CreateModalityUseCase,
    DeleteModalityUseCase,
    EnrollCompetitorUseCase,
    GetModalityUseCase,
    ListModalitiesUseCase,
    UpdateModalityUseCase,
)
from src.domain.identity.entities.user import User
from src.infrastructure.database.repositories import (
    SQLAlchemyCompetenceRepository,
    SQLAlchemyCompetitorRepository,
    SQLAlchemyEnrollmentRepository,
    SQLAlchemyModalityRepository,
)
from src.presentation.api.v1.dependencies.auth import (
    get_current_active_user,
    require_evaluator,
    require_super_admin,
)
from src.presentation.api.v1.dependencies.database import get_db
from src.presentation.schemas.common import MessageResponse
from src.presentation.schemas.modality_schema import (
    CompetenceResponse,
    CreateCompetenceRequest,
    CreateModalityRequest,
    EnrollCompetitorRequest,
    EnrollmentDetailResponse,
    EnrollmentListResponse,
    EnrollmentResponse,
    ModalityListResponse,
    ModalityResponse,
    UpdateCompetenceRequest,
    UpdateEnrollmentRequest,
    UpdateModalityRequest,
)

router = APIRouter()


# Helper to convert DTOs to response models
def modality_dto_to_response(dto: Any) -> ModalityResponse:
    return ModalityResponse(
        id=dto.id,
        code=dto.code,
        name=dto.name,
        description=dto.description,
        is_active=dto.is_active,
        min_training_hours=dto.min_training_hours,
        competences=[
            CompetenceResponse(
                id=c.id,
                modality_id=c.modality_id,
                name=c.name,
                description=c.description,
                weight=c.weight,
                max_score=c.max_score,
                is_active=c.is_active,
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
            for c in dto.competences
        ],
        created_at=dto.created_at,
        updated_at=dto.updated_at,
    )


@router.post(
    "",
    response_model=ModalityResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create modality",
    description="Create a new competition modality. Requires super admin role.",
)
async def create_modality(
    data: CreateModalityRequest,
    current_user: Annotated[User, Depends(require_super_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ModalityResponse:
    """Create a new modality."""
    use_case = CreateModalityUseCase(
        modality_repository=SQLAlchemyModalityRepository(db),
    )

    dto = CreateModalityDTO(
        code=data.code,
        name=data.name,
        description=data.description,
        min_training_hours=data.min_training_hours,
    )

    result = await use_case.execute(dto)
    await db.commit()

    return modality_dto_to_response(result)


@router.get(
    "",
    response_model=ModalityListResponse,
    summary="List modalities",
    description="List all modalities with pagination and filtering.",
)
async def list_modalities(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    active_only: bool = Query(default=False),
    search: str | None = Query(default=None, max_length=100),
) -> ModalityListResponse:
    """List modalities."""
    use_case = ListModalitiesUseCase(
        modality_repository=SQLAlchemyModalityRepository(db),
    )

    result = await use_case.execute(
        skip=skip,
        limit=limit,
        active_only=active_only,
        search=search,
    )

    return ModalityListResponse(
        modalities=[modality_dto_to_response(m) for m in result.modalities],
        total=result.total,
        skip=result.skip,
        limit=result.limit,
        has_more=result.has_more,
    )


@router.get(
    "/{modality_id}",
    response_model=ModalityResponse,
    summary="Get modality",
    description="Get a single modality by ID.",
)
async def get_modality(
    modality_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ModalityResponse:
    """Get modality by ID."""
    use_case = GetModalityUseCase(
        modality_repository=SQLAlchemyModalityRepository(db),
    )

    result = await use_case.execute(modality_id)

    return modality_dto_to_response(result)


@router.put(
    "/{modality_id}",
    response_model=ModalityResponse,
    summary="Update modality",
    description="Update a modality. Requires super admin role.",
)
async def update_modality(
    modality_id: UUID,
    data: UpdateModalityRequest,
    current_user: Annotated[User, Depends(require_super_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ModalityResponse:
    """Update a modality."""
    use_case = UpdateModalityUseCase(
        modality_repository=SQLAlchemyModalityRepository(db),
    )

    dto = UpdateModalityDTO(
        code=data.code,
        name=data.name,
        description=data.description,
        min_training_hours=data.min_training_hours,
        is_active=data.is_active,
    )

    result = await use_case.execute(modality_id, dto)
    await db.commit()

    return modality_dto_to_response(result)


@router.delete(
    "/{modality_id}",
    response_model=MessageResponse,
    summary="Delete modality",
    description="Delete a modality. Requires super admin role.",
)
async def delete_modality(
    modality_id: UUID,
    current_user: Annotated[User, Depends(require_super_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MessageResponse:
    """Delete a modality."""
    use_case = DeleteModalityUseCase(
        modality_repository=SQLAlchemyModalityRepository(db),
    )

    await use_case.execute(modality_id)
    await db.commit()

    return MessageResponse(message="Modality deleted successfully")


@router.post(
    "/{modality_id}/competitors",
    response_model=EnrollmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Enroll competitor",
    description="Enroll a competitor in a modality. Requires evaluator or super admin role.",
)
async def enroll_competitor(
    modality_id: UUID,
    data: EnrollCompetitorRequest,
    current_user: Annotated[User, Depends(require_evaluator)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> EnrollmentResponse:
    """Enroll a competitor in a modality."""
    import logging

    logger = logging.getLogger(__name__)

    logger.info(
        f"[Enroll] Creating enrollment: modality_id={modality_id}, competitor_id={data.competitor_id}, evaluator_id={data.evaluator_id}, current_user={current_user.id}"
    )

    use_case = EnrollCompetitorUseCase(
        modality_repository=SQLAlchemyModalityRepository(db),
        competitor_repository=SQLAlchemyCompetitorRepository(db),
        enrollment_repository=SQLAlchemyEnrollmentRepository(db),
    )

    dto = EnrollCompetitorDTO(
        competitor_id=data.competitor_id,
        evaluator_id=data.evaluator_id or current_user.id,  # Default to current user
        notes=data.notes,
    )

    result = await use_case.execute(modality_id, dto)
    await db.commit()

    logger.info(
        f"[Enroll] Created enrollment: id={result.id}, competitor_id={result.competitor_id}, modality_id={result.modality_id}"
    )

    return EnrollmentResponse(
        id=result.id,
        competitor_id=result.competitor_id,
        modality_id=result.modality_id,
        evaluator_id=result.evaluator_id,
        enrolled_at=result.enrolled_at,
        status=result.status,
        notes=result.notes,
        created_at=result.created_at,
        updated_at=result.updated_at,
    )


@router.get(
    "/{modality_id}/competences",
    response_model=list[CompetenceResponse],
    summary="List competences",
    description="List all competences for a modality.",
)
async def list_competences(
    modality_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[CompetenceResponse]:
    """List competences for a modality."""
    competence_repository = SQLAlchemyCompetenceRepository(db)
    competences = await competence_repository.get_by_modality(modality_id)

    return [
        CompetenceResponse(
            id=c.id,
            modality_id=c.modality_id,
            name=c.name,
            description=c.description,
            weight=c.weight,
            max_score=c.max_score,
            is_active=c.is_active,
            created_at=c.created_at,
            updated_at=c.updated_at,
        )
        for c in competences
    ]


@router.post(
    "/{modality_id}/competences",
    response_model=CompetenceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add competence",
    description="Add a competence to a modality. Requires evaluator or super admin role.",
)
async def add_competence(
    modality_id: UUID,
    data: CreateCompetenceRequest,
    current_user: Annotated[User, Depends(require_evaluator)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CompetenceResponse:
    """Add a competence to a modality."""
    use_case = AddCompetenceUseCase(
        modality_repository=SQLAlchemyModalityRepository(db),
        competence_repository=SQLAlchemyCompetenceRepository(db),
    )

    dto = CreateCompetenceDTO(
        name=data.name,
        description=data.description,
        weight=data.weight,
        max_score=data.max_score,
    )

    result = await use_case.execute(modality_id, dto)
    await db.commit()

    return CompetenceResponse(
        id=result.id,
        modality_id=result.modality_id,
        name=result.name,
        description=result.description,
        weight=result.weight,
        max_score=result.max_score,
        is_active=result.is_active,
        created_at=result.created_at,
        updated_at=result.updated_at,
    )


@router.put(
    "/{modality_id}/competences/{competence_id}",
    response_model=CompetenceResponse,
    summary="Update competence",
    description="Update a competence in a modality. Requires evaluator or super admin role.",
)
async def update_competence(
    modality_id: UUID,
    competence_id: UUID,
    data: UpdateCompetenceRequest,
    current_user: Annotated[User, Depends(require_evaluator)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CompetenceResponse:
    """Update a competence in a modality."""
    competence_repository = SQLAlchemyCompetenceRepository(db)
    competence = await competence_repository.get_by_id(competence_id)

    if not competence:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Competence not found")

    if competence.modality_id != modality_id:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=400,
            detail="Competence does not belong to this modality",
        )

    # Update fields
    if data.name is not None:
        competence._name = data.name
    if data.description is not None:
        competence._description = data.description
    if data.weight is not None:
        competence._weight = data.weight
    if data.max_score is not None:
        competence._max_score = data.max_score
    if data.is_active is not None:
        competence._is_active = data.is_active

    competence._touch()

    result = await competence_repository.update(competence)
    await db.commit()

    return CompetenceResponse(
        id=result.id,
        modality_id=result.modality_id,
        name=result.name,
        description=result.description,
        weight=result.weight,
        max_score=result.max_score,
        is_active=result.is_active,
        created_at=result.created_at,
        updated_at=result.updated_at,
    )


@router.delete(
    "/{modality_id}/competences/{competence_id}",
    response_model=MessageResponse,
    summary="Delete competence",
    description="Delete a competence from a modality. Requires super admin role.",
)
async def delete_competence(
    modality_id: UUID,
    competence_id: UUID,
    current_user: Annotated[User, Depends(require_super_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MessageResponse:
    """Delete a competence from a modality."""
    competence_repository = SQLAlchemyCompetenceRepository(db)
    competence = await competence_repository.get_by_id(competence_id)

    if not competence:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Competence not found")

    if competence.modality_id != modality_id:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=400,
            detail="Competence does not belong to this modality",
        )

    await competence_repository.delete(competence_id)
    await db.commit()

    return MessageResponse(message="Competence deleted successfully")


@router.get(
    "/{modality_id}/enrollments",
    response_model=EnrollmentListResponse,
    summary="List enrollments",
    description="List all enrollments for a modality with competitor and evaluator details.",
)
async def list_modality_enrollments(
    modality_id: UUID,
    current_user: Annotated[User, Depends(require_evaluator)],
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    status_filter: str | None = Query(default=None, alias="status"),
) -> EnrollmentListResponse:
    """List enrollments for a modality with details."""
    from sqlalchemy import select

    from src.domain.modality.entities.enrollment import EnrollmentStatus
    from src.infrastructure.database.models.modality_model import (
        CompetitorModel,
        EnrollmentModel,
        ModalityModel,
    )
    from src.infrastructure.database.models.user_model import UserModel

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
        .where(EnrollmentModel.modality_id == modality_id)
    )

    if status_filter:
        stmt = stmt.where(EnrollmentModel.status == status_filter)

    # Count total
    from sqlalchemy import func

    count_stmt = select(func.count(EnrollmentModel.id)).where(
        EnrollmentModel.modality_id == modality_id
    )
    if status_filter:
        count_stmt = count_stmt.where(EnrollmentModel.status == status_filter)
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    # Apply pagination
    stmt = stmt.offset(skip).limit(limit).order_by(EnrollmentModel.enrolled_at.desc())

    result = await db.execute(stmt)
    rows = result.all()

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
        total=total,
        skip=skip,
        limit=limit,
        has_more=skip + len(enrollments) < total,
    )


@router.put(
    "/{modality_id}/enrollments/{enrollment_id}",
    response_model=EnrollmentResponse,
    summary="Update enrollment",
    description="Update an enrollment (assign evaluator, change status). Requires super admin.",
)
async def update_enrollment(
    modality_id: UUID,
    enrollment_id: UUID,
    data: UpdateEnrollmentRequest,
    current_user: Annotated[User, Depends(require_super_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> EnrollmentResponse:
    """Update an enrollment."""
    enrollment_repository = SQLAlchemyEnrollmentRepository(db)
    enrollment = await enrollment_repository.get_by_id(enrollment_id)

    if not enrollment:
        from src.domain.modality.exceptions import EnrollmentNotFoundException

        raise EnrollmentNotFoundException(identifier=str(enrollment_id))

    if enrollment.modality_id != modality_id:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=400,
            detail="Enrollment does not belong to this modality",
        )

    # Update fields
    if data.evaluator_id is not None:
        enrollment.assign_evaluator(data.evaluator_id)
    if data.status is not None:
        enrollment._status = data.status
        enrollment._touch()
    if data.notes is not None:
        enrollment.update_notes(data.notes)

    result = await enrollment_repository.update(enrollment)
    await db.commit()

    return EnrollmentResponse(
        id=result.id,
        competitor_id=result.competitor_id,
        modality_id=result.modality_id,
        evaluator_id=result.evaluator_id,
        enrolled_at=result.enrolled_at,
        status=result.status,
        notes=result.notes,
        created_at=result.created_at,
        updated_at=result.updated_at,
    )


@router.delete(
    "/{modality_id}/enrollments/{enrollment_id}",
    response_model=MessageResponse,
    summary="Remove enrollment",
    description="Remove a competitor from a modality. Requires super admin role.",
)
async def delete_enrollment(
    modality_id: UUID,
    enrollment_id: UUID,
    current_user: Annotated[User, Depends(require_super_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MessageResponse:
    """Remove an enrollment."""
    enrollment_repository = SQLAlchemyEnrollmentRepository(db)
    enrollment = await enrollment_repository.get_by_id(enrollment_id)

    if not enrollment:
        from src.domain.modality.exceptions import EnrollmentNotFoundException

        raise EnrollmentNotFoundException(identifier=str(enrollment_id))

    if enrollment.modality_id != modality_id:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=400,
            detail="Enrollment does not belong to this modality",
        )

    await enrollment_repository.delete(enrollment_id)
    await db.commit()

    return MessageResponse(message="Enrollment removed successfully")
