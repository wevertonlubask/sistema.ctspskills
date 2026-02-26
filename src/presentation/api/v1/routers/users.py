"""Users router."""

from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.identity.use_cases.list_users import ListUsersUseCase
from src.domain.identity.entities.user import User
from src.infrastructure.database.repositories.user_repository_impl import (
    SQLAlchemyUserRepository,
)
from src.presentation.api.v1.dependencies.auth import (
    get_current_active_user,
    require_super_admin,
)
from src.presentation.api.v1.dependencies.database import get_db
from src.presentation.schemas.evaluator_modality_schema import (
    AssignModalityRequest,
    EvaluatorModalityResponse,
)
from src.presentation.schemas.modality_schema import (
    ModalityResponse,
)
from src.presentation.schemas.user_schema import UserListResponse, UserResponse
from src.shared.constants.enums import UserRole

router = APIRouter()


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get the currently authenticated user's information.",
)
async def get_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> UserResponse:
    """Get current authenticated user."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email.value,
        full_name=current_user.full_name,
        role=current_user.role.value,
        status=current_user.status.value,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        last_login_at=current_user.last_login_at,
        must_change_password=current_user.must_change_password,
    )


@router.get(
    "",
    response_model=UserListResponse,
    summary="List users",
    description="List all users with pagination. Requires super admin role.",
)
async def list_users(
    current_user: Annotated[User, Depends(require_super_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum records to return"),
    role: UserRole | None = Query(default=None, description="Filter by role"),
) -> UserListResponse:
    """List users with pagination."""
    use_case = ListUsersUseCase(
        user_repository=SQLAlchemyUserRepository(db),
    )

    result = await use_case.execute(skip=skip, limit=limit, role=role)

    return UserListResponse(
        users=[
            UserResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                role=user.role.value,
                status=user.status.value,
                created_at=user.created_at,
                updated_at=user.updated_at,
                last_login_at=user.last_login_at,
                must_change_password=user.must_change_password,
            )
            for user in result.users
        ],
        total=result.total,
        skip=result.skip,
        limit=result.limit,
        has_more=result.has_more,
    )


@router.get(
    "/me/modalities",
    response_model=list[ModalityResponse],
    summary="Get my modalities",
    description="Get modalities for the current user based on their role.",
)
async def get_my_modalities(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[ModalityResponse]:
    """Get modalities for the current user based on their role."""
    import logging

    logger = logging.getLogger(__name__)

    from sqlalchemy import union_all

    from src.infrastructure.database.models.modality_model import (
        CompetenceModel,
        CompetitorModel,
        EnrollmentModel,
        EvaluatorModalityModel,
        ModalityModel,
    )
    from src.presentation.schemas.modality_schema import CompetenceResponse

    logger.info(f"[MyModalities] User: {current_user.id}, Role: {current_user.role}")

    # Super admins can see all modalities
    if current_user.role == UserRole.SUPER_ADMIN:
        stmt = select(ModalityModel).where(ModalityModel.is_active).order_by(ModalityModel.name)
        result = await db.execute(stmt)
        modalities = result.scalars().unique().all()

    # Competitors see modalities they are enrolled in
    elif current_user.role == UserRole.COMPETITOR:
        # First, find the competitor record for this user
        competitor_stmt = select(CompetitorModel).where(CompetitorModel.user_id == current_user.id)
        competitor_result = await db.execute(competitor_stmt)
        competitor = competitor_result.scalar_one_or_none()

        if not competitor:
            # No competitor profile found
            modalities = []
        else:
            # Get modalities from enrollments
            stmt = (
                select(ModalityModel)
                .join(EnrollmentModel, EnrollmentModel.modality_id == ModalityModel.id)
                .where(EnrollmentModel.competitor_id == competitor.id)
                .where(EnrollmentModel.status == "active")
                .where(ModalityModel.is_active)
                .order_by(ModalityModel.name)
            )
            result = await db.execute(stmt)
            modalities = result.scalars().unique().all()

    # Evaluators see modalities from both direct assignments and enrollment assignments
    else:
        # Query 1: Direct assignments (evaluator_modalities table)
        direct_stmt = (
            select(ModalityModel.id)
            .join(EvaluatorModalityModel, EvaluatorModalityModel.modality_id == ModalityModel.id)
            .where(EvaluatorModalityModel.evaluator_id == current_user.id)
            .where(EvaluatorModalityModel.is_active)
            .where(ModalityModel.is_active)
        )

        # Query 2: Enrollment assignments (evaluators assigned to competitors)
        enrollment_stmt = (
            select(ModalityModel.id)
            .join(EnrollmentModel, EnrollmentModel.modality_id == ModalityModel.id)
            .where(EnrollmentModel.evaluator_id == current_user.id)
            .where(EnrollmentModel.status == "active")
            .where(ModalityModel.is_active)
        )

        # Combine with union
        combined = union_all(direct_stmt, enrollment_stmt).subquery()

        # Get distinct modalities
        stmt = (
            select(ModalityModel)
            .where(ModalityModel.id.in_(select(combined.c.id)))
            .order_by(ModalityModel.name)
        )
        result = await db.execute(stmt)
        modalities = result.scalars().unique().all()

    # Build responses with competences
    responses = []
    for modality in modalities:
        comp_stmt = (
            select(CompetenceModel)
            .where(CompetenceModel.modality_id == modality.id)
            .where(CompetenceModel.is_active)
        )
        comp_result = await db.execute(comp_stmt)
        competences = comp_result.scalars().all()

        responses.append(
            ModalityResponse(
                id=modality.id,
                code=modality.code,
                name=modality.name,
                description=modality.description or "",
                is_active=modality.is_active,
                min_training_hours=modality.min_training_hours,
                competences=[
                    CompetenceResponse(
                        id=c.id,
                        modality_id=c.modality_id,
                        name=c.name,
                        description=c.description or "",
                        weight=c.weight,
                        max_score=c.max_score,
                        is_active=c.is_active,
                        created_at=c.created_at,
                        updated_at=c.updated_at,
                    )
                    for c in competences
                ],
                created_at=modality.created_at,
                updated_at=modality.updated_at,
            )
        )

    logger.info(f"[MyModalities] Returning {len(responses)} modalities")
    return responses


@router.get(
    "/evaluators",
    response_model=UserListResponse,
    summary="List evaluators",
    description="List all evaluators. Requires super admin role.",
)
async def list_evaluators(
    current_user: Annotated[User, Depends(require_super_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserListResponse:
    """List all evaluators."""
    use_case = ListUsersUseCase(
        user_repository=SQLAlchemyUserRepository(db),
    )

    result = await use_case.execute(skip=0, limit=1000, role=UserRole.EVALUATOR)

    return UserListResponse(
        users=[
            UserResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                role=user.role.value,
                status=user.status.value,
                created_at=user.created_at,
                updated_at=user.updated_at,
                last_login_at=user.last_login_at,
                must_change_password=user.must_change_password,
            )
            for user in result.users
        ],
        total=result.total,
        skip=result.skip,
        limit=result.limit,
        has_more=result.has_more,
    )


@router.patch(
    "/{user_id}/activate",
    response_model=UserResponse,
    summary="Activate user",
    description="Activate a user account. Requires super admin role.",
)
async def activate_user(
    user_id: UUID,
    current_user: Annotated[User, Depends(require_super_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    """Activate a user account."""
    from src.infrastructure.database.models.user_model import UserModel
    from src.shared.utils.date_utils import utc_now

    stmt = select(UserModel).where(UserModel.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user.status = "active"
    user.updated_at = utc_now()
    await db.commit()
    await db.refresh(user)

    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        status=user.status,
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_login_at=user.last_login_at,
        must_change_password=user.must_change_password,
    )


@router.patch(
    "/{user_id}/deactivate",
    response_model=UserResponse,
    summary="Deactivate user",
    description="Deactivate a user account. Requires super admin role.",
)
async def deactivate_user(
    user_id: UUID,
    current_user: Annotated[User, Depends(require_super_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    """Deactivate a user account."""
    from src.infrastructure.database.models.user_model import UserModel
    from src.shared.utils.date_utils import utc_now

    stmt = select(UserModel).where(UserModel.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account",
        )

    user.status = "inactive"
    user.updated_at = utc_now()
    await db.commit()
    await db.refresh(user)

    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        status=user.status,
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_login_at=user.last_login_at,
        must_change_password=user.must_change_password,
    )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
    description="Delete a user and all related data. Requires super admin role.",
)
async def delete_user(
    user_id: UUID,
    current_user: Annotated[User, Depends(require_super_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete a user and all related data."""
    import logging

    from sqlalchemy import inspect, text

    from src.infrastructure.database.models.user_model import UserModel

    logger = logging.getLogger(__name__)

    stmt = select(UserModel).where(UserModel.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )

    # Check which extras tables exist before trying to delete from them
    def get_existing_tables(sync_session: Any) -> set[str]:
        inspector = inspect(sync_session.get_bind())
        return set(inspector.get_table_names())

    existing_tables = await db.run_sync(get_existing_tables)
    logger.info(f"Existing tables: {existing_tables}")

    # Delete from extras tables only if they exist
    extras_user_id_tables = [
        "event_participants",
        "notifications",
        "schedules",
        "achievements",
        "user_points",
    ]
    for table_name in extras_user_id_tables:
        if table_name in existing_tables:
            await db.execute(
                text(f"DELETE FROM {table_name} WHERE user_id = :uid"),  # nosec B608
                {"uid": str(user_id)},
            )

    # Messages and conversations
    if "conversations" in existing_tables:
        conv_result = await db.execute(
            text("SELECT id FROM conversations WHERE participant_1 = :uid OR participant_2 = :uid"),
            {"uid": str(user_id)},
        )
        conv_ids = [str(row[0]) for row in conv_result.all()]
        if conv_ids and "messages" in existing_tables:
            placeholders = ",".join([f"'{cid}'" for cid in conv_ids])
            await db.execute(
                text(
                    f"DELETE FROM messages WHERE conversation_id IN ({placeholders})"  # nosec B608
                )
            )
        await db.execute(
            text("DELETE FROM conversations WHERE participant_1 = :uid OR participant_2 = :uid"),
            {"uid": str(user_id)},
        )

    if "messages" in existing_tables:
        await db.execute(text("DELETE FROM messages WHERE sender_id = :uid"), {"uid": str(user_id)})

    if "feedbacks" in existing_tables:
        await db.execute(
            text("DELETE FROM feedbacks WHERE evaluator_id = :uid"), {"uid": str(user_id)}
        )

    # Goals and milestones
    if "goals" in existing_tables:
        if "milestones" in existing_tables:
            goal_result = await db.execute(
                text("SELECT id FROM goals WHERE created_by = :uid"), {"uid": str(user_id)}
            )
            goal_ids = [str(row[0]) for row in goal_result.all()]
            if goal_ids:
                placeholders = ",".join([f"'{gid}'" for gid in goal_ids])
                await db.execute(
                    text(f"DELETE FROM milestones WHERE goal_id IN ({placeholders})")  # nosec B608
                )
        await db.execute(text("DELETE FROM goals WHERE created_by = :uid"), {"uid": str(user_id)})

    if "training_plans" in existing_tables:
        await db.execute(
            text("DELETE FROM training_plans WHERE created_by = :uid"), {"uid": str(user_id)}
        )

    if "resources" in existing_tables:
        await db.execute(
            text("DELETE FROM resources WHERE created_by = :uid"), {"uid": str(user_id)}
        )

    if "events" in existing_tables:
        await db.execute(text("DELETE FROM events WHERE created_by = :uid"), {"uid": str(user_id)})

    # Delete the user (CASCADE handles: refresh_tokens, competitors, evaluator_modalities)
    # SET NULL handles: exams.created_by, grades.created_by/updated_by, etc.
    await db.execute(delete(UserModel).where(UserModel.id == user_id))
    await db.commit()


@router.get(
    "/{user_id}/modalities",
    response_model=list[EvaluatorModalityResponse],
    summary="Get evaluator modalities",
    description="Get modalities assigned to an evaluator. Requires super admin role.",
)
async def get_evaluator_modalities(
    user_id: UUID,
    current_user: Annotated[User, Depends(require_super_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[EvaluatorModalityResponse]:
    """Get modalities assigned to an evaluator."""
    from src.infrastructure.database.models.modality_model import (
        EvaluatorModalityModel,
        ModalityModel,
    )

    stmt = (
        select(EvaluatorModalityModel, ModalityModel)
        .join(ModalityModel, EvaluatorModalityModel.modality_id == ModalityModel.id)
        .where(EvaluatorModalityModel.evaluator_id == user_id)
        .where(EvaluatorModalityModel.is_active)
        .order_by(ModalityModel.name)
    )
    result = await db.execute(stmt)
    rows = result.all()

    return [
        EvaluatorModalityResponse(
            id=em.id,
            evaluator_id=em.evaluator_id,
            modality_id=em.modality_id,
            modality_code=modality.code,
            modality_name=modality.name,
            assigned_at=em.assigned_at,
            assigned_by=em.assigned_by,
            is_active=em.is_active,
            created_at=em.created_at,
            updated_at=em.updated_at,
        )
        for em, modality in rows
    ]


@router.post(
    "/{user_id}/modalities",
    response_model=EvaluatorModalityResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Assign modality to evaluator",
    description="Assign a modality to an evaluator. Requires super admin role.",
)
async def assign_modality_to_evaluator(
    user_id: UUID,
    request: AssignModalityRequest,
    current_user: Annotated[User, Depends(require_super_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> EvaluatorModalityResponse:
    """Assign a modality to an evaluator."""
    from uuid import uuid4

    from src.infrastructure.database.models.modality_model import (
        EvaluatorModalityModel,
        ModalityModel,
    )
    from src.infrastructure.database.models.user_model import UserModel
    from src.shared.utils.date_utils import utc_now

    # Check if user exists and is an evaluator
    user_stmt = select(UserModel).where(UserModel.id == user_id)
    user_result = await db.execute(user_stmt)
    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.role != UserRole.EVALUATOR.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not an evaluator",
        )

    # Check if modality exists
    modality_stmt = select(ModalityModel).where(ModalityModel.id == request.modality_id)
    modality_result = await db.execute(modality_stmt)
    modality = modality_result.scalar_one_or_none()

    if not modality:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Modality not found",
        )

    # Check if assignment already exists
    existing_stmt = select(EvaluatorModalityModel).where(
        EvaluatorModalityModel.evaluator_id == user_id,
        EvaluatorModalityModel.modality_id == request.modality_id,
    )
    existing_result = await db.execute(existing_stmt)
    existing = existing_result.scalar_one_or_none()

    if existing:
        # Reactivate if inactive
        if not existing.is_active:
            existing.is_active = True
            existing.assigned_by = current_user.id
            existing.assigned_at = utc_now()
            await db.commit()
            await db.refresh(existing)
            return EvaluatorModalityResponse(
                id=existing.id,
                evaluator_id=existing.evaluator_id,
                modality_id=existing.modality_id,
                modality_code=modality.code,
                modality_name=modality.name,
                assigned_at=existing.assigned_at,
                assigned_by=existing.assigned_by,
                is_active=existing.is_active,
                created_at=existing.created_at,
                updated_at=existing.updated_at,
            )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Modality already assigned to this evaluator",
        )

    # Create new assignment
    now = utc_now()
    assignment = EvaluatorModalityModel(
        id=uuid4(),
        evaluator_id=user_id,
        modality_id=request.modality_id,
        assigned_at=now,
        assigned_by=current_user.id,
        is_active=True,
        created_at=now,
        updated_at=now,
    )
    db.add(assignment)
    await db.commit()
    await db.refresh(assignment)

    return EvaluatorModalityResponse(
        id=assignment.id,
        evaluator_id=assignment.evaluator_id,
        modality_id=assignment.modality_id,
        modality_code=modality.code,
        modality_name=modality.name,
        assigned_at=assignment.assigned_at,
        assigned_by=assignment.assigned_by,
        is_active=assignment.is_active,
        created_at=assignment.created_at,
        updated_at=assignment.updated_at,
    )


@router.delete(
    "/{user_id}/modalities/{modality_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove modality from evaluator",
    description="Remove a modality assignment from an evaluator. Requires super admin role.",
)
async def remove_modality_from_evaluator(
    user_id: UUID,
    modality_id: UUID,
    current_user: Annotated[User, Depends(require_super_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Remove a modality assignment from an evaluator."""
    from src.infrastructure.database.models.modality_model import EvaluatorModalityModel

    # Find the assignment
    stmt = select(EvaluatorModalityModel).where(
        EvaluatorModalityModel.evaluator_id == user_id,
        EvaluatorModalityModel.modality_id == modality_id,
    )
    result = await db.execute(stmt)
    assignment = result.scalar_one_or_none()

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Modality assignment not found",
        )

    # Soft delete
    assignment.is_active = False
    await db.commit()
