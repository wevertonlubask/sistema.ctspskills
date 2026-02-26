"""Training types router."""

from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.training.use_cases import (
    CreateTrainingTypeConfigUseCase,
    DeleteTrainingTypeConfigUseCase,
    GetTrainingTypeConfigUseCase,
    ListTrainingTypeConfigsUseCase,
    UpdateTrainingTypeConfigUseCase,
)
from src.domain.identity.entities.user import User
from src.infrastructure.database.repositories import SQLAlchemyTrainingTypeConfigRepository
from src.presentation.api.v1.dependencies.auth import (
    get_current_active_user,
    require_super_admin,
)
from src.presentation.api.v1.dependencies.database import get_db
from src.presentation.schemas.common import MessageResponse
from src.presentation.schemas.training_schema import (
    CreateTrainingTypeConfigRequest,
    TrainingTypeConfigListResponse,
    TrainingTypeConfigResponse,
    UpdateTrainingTypeConfigRequest,
)

router = APIRouter()


def dto_to_response(dto: Any) -> TrainingTypeConfigResponse:
    """Convert DTO to response model."""
    return TrainingTypeConfigResponse(
        id=dto.id,
        code=dto.code,
        name=dto.name,
        description=dto.description,
        is_active=dto.is_active,
        display_order=dto.display_order,
        created_at=dto.created_at,
        updated_at=dto.updated_at,
    )


@router.post(
    "",
    response_model=TrainingTypeConfigResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create training type",
    description="Create a new training type configuration. Requires super admin role.",
)
async def create_training_type(
    data: CreateTrainingTypeConfigRequest,
    current_user: Annotated[User, Depends(require_super_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TrainingTypeConfigResponse:
    """Create a new training type configuration."""
    use_case = CreateTrainingTypeConfigUseCase(
        repository=SQLAlchemyTrainingTypeConfigRepository(db),
    )

    try:
        result = await use_case.execute(
            code=data.code,
            name=data.name,
            description=data.description,
            display_order=data.display_order,
        )
        await db.commit()
        return dto_to_response(result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.get(
    "",
    response_model=TrainingTypeConfigListResponse,
    summary="List training types",
    description="List all training type configurations with pagination.",
)
async def list_training_types(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    active_only: bool = Query(default=False),
) -> TrainingTypeConfigListResponse:
    """List training type configurations."""
    use_case = ListTrainingTypeConfigsUseCase(
        repository=SQLAlchemyTrainingTypeConfigRepository(db),
    )

    result = await use_case.execute(
        skip=skip,
        limit=limit,
        active_only=active_only,
    )

    return TrainingTypeConfigListResponse(
        items=[dto_to_response(item) for item in result.items],
        total=result.total,
        skip=result.skip,
        limit=result.limit,
        has_more=result.has_more,
    )


@router.get(
    "/{training_type_id}",
    response_model=TrainingTypeConfigResponse,
    summary="Get training type",
    description="Get a single training type configuration by ID.",
)
async def get_training_type(
    training_type_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TrainingTypeConfigResponse:
    """Get training type configuration by ID."""
    use_case = GetTrainingTypeConfigUseCase(
        repository=SQLAlchemyTrainingTypeConfigRepository(db),
    )

    result = await use_case.execute(training_type_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training type not found",
        )

    return dto_to_response(result)


@router.put(
    "/{training_type_id}",
    response_model=TrainingTypeConfigResponse,
    summary="Update training type",
    description="Update a training type configuration. Requires super admin role.",
)
async def update_training_type(
    training_type_id: UUID,
    data: UpdateTrainingTypeConfigRequest,
    current_user: Annotated[User, Depends(require_super_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TrainingTypeConfigResponse:
    """Update a training type configuration."""
    use_case = UpdateTrainingTypeConfigUseCase(
        repository=SQLAlchemyTrainingTypeConfigRepository(db),
    )

    try:
        result = await use_case.execute(
            id=training_type_id,
            name=data.name,
            description=data.description,
            display_order=data.display_order,
            is_active=data.is_active,
        )
        await db.commit()
        return dto_to_response(result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.delete(
    "/{training_type_id}",
    response_model=MessageResponse,
    summary="Delete training type",
    description="Delete a training type configuration. Requires super admin role.",
)
async def delete_training_type(
    training_type_id: UUID,
    current_user: Annotated[User, Depends(require_super_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MessageResponse:
    """Delete a training type configuration."""
    use_case = DeleteTrainingTypeConfigUseCase(
        repository=SQLAlchemyTrainingTypeConfigRepository(db),
    )

    deleted = await use_case.execute(training_type_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training type not found",
        )

    await db.commit()
    return MessageResponse(message="Training type deleted successfully")
