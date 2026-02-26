"""Trainings router."""

from datetime import date
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.training.dtos.evidence_dto import UploadEvidenceDTO
from src.application.training.dtos.training_dto import (
    RegisterTrainingDTO,
    ValidateTrainingDTO,
)
from src.application.training.use_cases import (
    DeleteTrainingUseCase,
    GetTrainingStatisticsUseCase,
    GetTrainingUseCase,
    ListTrainingsUseCase,
    RegisterTrainingUseCase,
    UploadEvidenceUseCase,
    ValidateTrainingUseCase,
)
from src.domain.identity.entities.user import User
from src.domain.training.entities.evidence import EvidenceType
from src.infrastructure.database.repositories import (
    SQLAlchemyCompetitorRepository,
    SQLAlchemyEnrollmentRepository,
    SQLAlchemyEvidenceRepository,
    SQLAlchemyModalityRepository,
    SQLAlchemyTrainingRepository,
)
from src.presentation.api.v1.dependencies.auth import (
    get_current_active_user,
    require_competitor,
    require_evaluator,
)
from src.presentation.api.v1.dependencies.database import get_db
from src.presentation.schemas.common import MessageResponse
from src.presentation.schemas.training_schema import (
    CreateTrainingRequest,
    EvidenceResponse,
    PendingTrainingsCountResponse,
    TrainingListResponse,
    TrainingResponse,
    TrainingStatisticsResponse,
    UpdateTrainingRequest,
    ValidateTrainingRequest,
)
from src.shared.constants.enums import TrainingStatus, UserRole

router = APIRouter()


def training_dto_to_response(dto: Any) -> TrainingResponse:
    """Convert TrainingDTO to response model."""
    return TrainingResponse(
        id=dto.id,
        competitor_id=dto.competitor_id,
        competitor_name=getattr(dto, "competitor_name", None),
        modality_id=dto.modality_id,
        modality_name=getattr(dto, "modality_name", None),
        enrollment_id=dto.enrollment_id,
        training_date=dto.training_date,
        hours=dto.hours,
        training_type=dto.training_type,
        location=dto.location,
        description=dto.description,
        status=dto.status,
        validated_by=dto.validated_by,
        validated_at=dto.validated_at,
        rejection_reason=dto.rejection_reason,
        evidences=[
            EvidenceResponse(
                id=e.id,
                training_session_id=e.training_session_id,
                file_name=e.file_name,
                file_path=e.file_path,
                file_size=e.file_size,
                mime_type=e.mime_type,
                evidence_type=e.evidence_type,
                description=e.description,
                uploaded_by=e.uploaded_by,
                created_at=e.created_at,
                updated_at=e.updated_at,
            )
            for e in dto.evidences
        ],
        created_at=dto.created_at,
        updated_at=dto.updated_at,
    )


@router.post(
    "",
    response_model=TrainingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register training",
    description="Register a new training session. Requires competitor role.",
)
async def register_training(
    data: CreateTrainingRequest,
    current_user: Annotated[User, Depends(require_competitor)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TrainingResponse:
    """Register a new training session."""
    # Get competitor ID from user
    competitor_repo = SQLAlchemyCompetitorRepository(db)
    competitor = await competitor_repo.get_by_user_id(current_user.id)
    if not competitor:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Competitor profile not found for this user",
        )

    use_case = RegisterTrainingUseCase(
        training_repository=SQLAlchemyTrainingRepository(db),
        enrollment_repository=SQLAlchemyEnrollmentRepository(db),
        competitor_repository=competitor_repo,
    )

    dto = RegisterTrainingDTO(
        modality_id=data.modality_id,
        training_date=data.training_date,
        hours=data.hours,
        training_type=data.training_type,
        location=data.location,
        description=data.description,
    )

    result = await use_case.execute(competitor.id, dto)
    await db.commit()

    return training_dto_to_response(result)


@router.get(
    "",
    response_model=TrainingListResponse,
    summary="List trainings",
    description="List training sessions with filters.",
)
async def list_trainings(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    competitor_id: UUID | None = Query(default=None),
    modality_id: UUID | None = Query(default=None),
    status_filter: TrainingStatus | None = Query(default=None, alias="status"),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
) -> TrainingListResponse:
    """List training sessions."""
    use_case = ListTrainingsUseCase(
        training_repository=SQLAlchemyTrainingRepository(db),
    )

    # Determine filter based on user role
    evaluator_id = None
    if current_user.role == UserRole.EVALUATOR:
        evaluator_id = current_user.id
    elif current_user.role == UserRole.COMPETITOR:
        # Competitors can only see their own trainings
        competitor_repo = SQLAlchemyCompetitorRepository(db)
        competitor = await competitor_repo.get_by_user_id(current_user.id)
        if competitor:
            competitor_id = competitor.id

    result = await use_case.execute(
        competitor_id=competitor_id,
        modality_id=modality_id,
        evaluator_id=evaluator_id,
        status=status_filter,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit,
    )

    # Buscar nomes dos competidores e modalidades em batch
    competitor_ids = list({t.competitor_id for t in result.trainings})
    modality_ids = list({t.modality_id for t in result.trainings})

    competitor_repo = SQLAlchemyCompetitorRepository(db)
    modality_repo = SQLAlchemyModalityRepository(db)

    # Criar mapas de ID -> nome
    competitor_names: dict[UUID, str] = {}
    modality_names: dict[UUID, str] = {}

    for cid in competitor_ids:
        comp = await competitor_repo.get_by_id(cid)
        if comp:
            competitor_names[cid] = comp.full_name

    for mid in modality_ids:
        mod = await modality_repo.get_by_id(mid)
        if mod:
            modality_names[mid] = mod.name

    # Atribuir nomes aos DTOs
    for training in result.trainings:
        training.competitor_name = competitor_names.get(training.competitor_id)
        training.modality_name = modality_names.get(training.modality_id)

    return TrainingListResponse(
        trainings=[training_dto_to_response(t) for t in result.trainings],
        total=result.total,
        skip=result.skip,
        limit=result.limit,
        has_more=result.has_more,
    )


@router.get(
    "/statistics",
    response_model=TrainingStatisticsResponse,
    summary="Get training statistics",
    description="Get training statistics for a competitor.",
)
async def get_training_statistics(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    competitor_id: UUID | None = Query(default=None),
    modality_id: UUID | None = Query(default=None),
) -> TrainingStatisticsResponse:
    """Get training statistics."""
    # Determine competitor ID
    if not competitor_id:
        if current_user.role == UserRole.COMPETITOR:
            competitor_repo = SQLAlchemyCompetitorRepository(db)
            competitor = await competitor_repo.get_by_user_id(current_user.id)
            if competitor:
                competitor_id = competitor.id

    if not competitor_id:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="competitor_id is required",
        )

    use_case = GetTrainingStatisticsUseCase(
        training_repository=SQLAlchemyTrainingRepository(db),
    )

    result = await use_case.execute(
        competitor_id=competitor_id,
        modality_id=modality_id,
    )

    return TrainingStatisticsResponse(
        competitor_id=result.competitor_id,
        modality_id=result.modality_id,
        senai_hours=result.senai_hours,
        external_hours=result.external_hours,
        total_approved_hours=result.total_approved_hours,
        total_sessions=result.total_sessions,
        pending_sessions=result.pending_sessions,
        approved_sessions=result.approved_sessions,
        rejected_sessions=result.rejected_sessions,
    )


@router.get(
    "/pending/count",
    response_model=PendingTrainingsCountResponse,
    summary="Get pending trainings count",
    description="Get count of pending trainings for notification.",
)
async def get_pending_count(
    current_user: Annotated[User, Depends(require_evaluator)],
    db: Annotated[AsyncSession, Depends(get_db)],
    modality_id: UUID | None = Query(default=None),
) -> PendingTrainingsCountResponse:
    """Get pending trainings count for evaluator."""
    training_repo = SQLAlchemyTrainingRepository(db)
    count = await training_repo.get_pending_count(
        evaluator_id=current_user.id,
        modality_id=modality_id,
    )

    return PendingTrainingsCountResponse(
        count=count,
        evaluator_id=current_user.id,
        modality_id=modality_id,
    )


@router.get(
    "/{training_id}",
    response_model=TrainingResponse,
    summary="Get training",
    description="Get a single training session by ID.",
)
async def get_training(
    training_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TrainingResponse:
    """Get training by ID."""
    use_case = GetTrainingUseCase(
        training_repository=SQLAlchemyTrainingRepository(db),
    )

    result = await use_case.execute(training_id)
    return training_dto_to_response(result)


@router.put(
    "/{training_id}",
    response_model=TrainingResponse,
    summary="Update training",
    description="Update training session details. Requires evaluator or super admin role.",
)
async def update_training(
    training_id: UUID,
    data: UpdateTrainingRequest,
    current_user: Annotated[User, Depends(require_evaluator)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TrainingResponse:
    """Update training session details (admin/evaluator correction)."""
    from fastapi import HTTPException
    from sqlalchemy import select

    from src.infrastructure.database.models.training_model import TrainingSessionModel
    from src.shared.utils.date_utils import utc_now

    stmt = select(TrainingSessionModel).where(TrainingSessionModel.id == training_id)
    result = await db.execute(stmt)
    training = result.scalar_one_or_none()

    if not training:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training not found",
        )

    # Update only provided fields
    if data.training_date is not None:
        training.training_date = data.training_date
    if data.hours is not None:
        training.hours = data.hours
    if data.training_type is not None:
        training.training_type = data.training_type.value
    if data.location is not None:
        training.location = data.location
    if data.description is not None:
        training.description = data.description

    training.updated_at = utc_now()
    await db.commit()
    await db.refresh(training)

    # Fetch names for response
    competitor_repo = SQLAlchemyCompetitorRepository(db)
    modality_repo = SQLAlchemyModalityRepository(db)
    comp = await competitor_repo.get_by_id(training.competitor_id)
    mod = await modality_repo.get_by_id(training.modality_id)

    return TrainingResponse(
        id=training.id,
        competitor_id=training.competitor_id,
        competitor_name=comp.full_name if comp else None,
        modality_id=training.modality_id,
        modality_name=mod.name if mod else None,
        enrollment_id=training.enrollment_id,
        training_date=training.training_date,
        hours=training.hours,
        training_type=training.training_type,  # type: ignore[arg-type]
        location=training.location,
        description=training.description,
        status=training.status,  # type: ignore[arg-type]
        validated_by=training.validated_by,
        validated_at=training.validated_at,
        rejection_reason=training.rejection_reason,
        evidences=[],
        created_at=training.created_at,
        updated_at=training.updated_at,
    )


@router.put(
    "/{training_id}/validate",
    response_model=TrainingResponse,
    summary="Validate training",
    description="Approve or reject a training session. Requires evaluator role.",
)
async def validate_training(
    training_id: UUID,
    data: ValidateTrainingRequest,
    current_user: Annotated[User, Depends(require_evaluator)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TrainingResponse:
    """Validate (approve/reject) a training session."""
    use_case = ValidateTrainingUseCase(
        training_repository=SQLAlchemyTrainingRepository(db),
        enrollment_repository=SQLAlchemyEnrollmentRepository(db),
    )

    dto = ValidateTrainingDTO(
        approved=data.approved,
        rejection_reason=data.rejection_reason,
    )

    result = await use_case.execute(
        training_id=training_id,
        evaluator_id=current_user.id,
        evaluator_role=current_user.role,
        dto=dto,
    )
    await db.commit()

    return training_dto_to_response(result)


@router.delete(
    "/{training_id}",
    response_model=MessageResponse,
    summary="Delete training",
    description="Delete a training session. Competitors can only delete pending trainings.",
)
async def delete_training(
    training_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MessageResponse:
    """Delete a training session."""
    # Check if user is deleting their own training
    is_own = False
    if current_user.role == UserRole.COMPETITOR:
        competitor_repo = SQLAlchemyCompetitorRepository(db)
        competitor = await competitor_repo.get_by_user_id(current_user.id)
        if competitor:
            training_repo = SQLAlchemyTrainingRepository(db)
            training = await training_repo.get_by_id(training_id)
            if training and training.competitor_id == competitor.id:
                is_own = True

    use_case = DeleteTrainingUseCase(
        training_repository=SQLAlchemyTrainingRepository(db),
    )

    await use_case.execute(
        training_id=training_id,
        user_id=current_user.id,
        user_role=current_user.role,
        is_own_training=is_own,
    )
    await db.commit()

    return MessageResponse(message="Training deleted successfully")


@router.post(
    "/{training_id}/evidences",
    response_model=EvidenceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload evidence",
    description="Upload evidence file for a training session.",
)
async def upload_evidence(
    training_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    file: UploadFile = File(...),
    evidence_type: EvidenceType = Form(default=EvidenceType.PHOTO),
    description: str | None = Form(default=None, max_length=500),
) -> EvidenceResponse:
    """Upload evidence for a training session."""
    use_case = UploadEvidenceUseCase(
        training_repository=SQLAlchemyTrainingRepository(db),
        evidence_repository=SQLAlchemyEvidenceRepository(db),
    )

    # Read file content
    file_content = await file.read()

    dto = UploadEvidenceDTO(
        file_name=file.filename or "unnamed",
        file_content=file_content,
        mime_type=file.content_type or "application/octet-stream",
        evidence_type=evidence_type,
        description=description,
    )

    result = await use_case.execute(
        training_id=training_id,
        uploader_id=current_user.id,
        dto=dto,
    )
    await db.commit()

    return EvidenceResponse(
        id=result.id,
        training_session_id=result.training_session_id,
        file_name=result.file_name,
        file_path=result.file_path,
        file_size=result.file_size,
        mime_type=result.mime_type,
        evidence_type=result.evidence_type,
        description=result.description,
        uploaded_by=result.uploaded_by,
        created_at=result.created_at,
        updated_at=result.updated_at,
    )
