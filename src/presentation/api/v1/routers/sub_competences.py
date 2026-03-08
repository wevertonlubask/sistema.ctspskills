"""Sub-competences router (WorldSkills sub-criteria)."""

from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.identity.entities.user import User
from src.infrastructure.database.models.modality_model import CompetenceModel, SubCompetenceModel
from src.presentation.api.v1.dependencies.auth import get_current_active_user, require_evaluator
from src.presentation.api.v1.dependencies.database import get_db
from src.presentation.schemas.assessment_schema import (
    CreateSubCompetenceRequest,
    SubCompetenceListResponse,
    SubCompetenceResponse,
    UpdateSubCompetenceRequest,
)

router = APIRouter()


def _model_to_response(model: SubCompetenceModel) -> SubCompetenceResponse:
    return SubCompetenceResponse(
        id=model.id,
        competence_id=model.competence_id,
        name=model.name,
        description=model.description,
        max_score=model.max_score,
        order=model.order,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


@router.get(
    "/{competence_id}/sub-competences",
    response_model=SubCompetenceListResponse,
    summary="List sub-competences",
)
async def list_sub_competences(
    competence_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SubCompetenceListResponse:
    """List all sub-competences for a competence."""
    stmt = (
        select(SubCompetenceModel)
        .where(SubCompetenceModel.competence_id == competence_id)
        .order_by(SubCompetenceModel.order, SubCompetenceModel.created_at)
    )
    result = await db.execute(stmt)
    models = result.scalars().all()
    return SubCompetenceListResponse(
        sub_competences=[_model_to_response(m) for m in models],
        total=len(models),
    )


@router.post(
    "/{competence_id}/sub-competences",
    response_model=SubCompetenceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create sub-competence",
)
async def create_sub_competence(
    competence_id: UUID,
    data: CreateSubCompetenceRequest,
    current_user: Annotated[User, Depends(require_evaluator)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SubCompetenceResponse:
    """Create a sub-competence under a competence."""
    # Verify parent competence exists
    comp_stmt = select(CompetenceModel).where(CompetenceModel.id == competence_id)
    comp_result = await db.execute(comp_stmt)
    competence = comp_result.scalar_one_or_none()
    if not competence:
        raise HTTPException(status_code=404, detail="Critério de avaliação não encontrado")

    # Validate: sum of sub-competence max_scores must not exceed competence max_score
    existing_stmt = select(SubCompetenceModel).where(SubCompetenceModel.competence_id == competence_id)
    existing_result = await db.execute(existing_stmt)
    existing = existing_result.scalars().all()
    current_sum = sum(s.max_score for s in existing)
    if current_sum + data.max_score > competence.max_score:
        remaining = competence.max_score - current_sum
        raise HTTPException(
            status_code=400,
            detail=(
                f"Pontuação máxima excedida. "
                f"O critério tem pontuação máxima de {competence.max_score}. "
                f"Já distribuído: {current_sum}. "
                f"Disponível: {remaining}."
            ),
        )

    model = SubCompetenceModel(
        id=uuid4(),
        competence_id=competence_id,
        name=data.name,
        description=data.description,
        max_score=data.max_score,
        order=data.order if data.order else len(existing),
    )
    db.add(model)
    await db.commit()
    await db.refresh(model)
    return _model_to_response(model)


@router.put(
    "/{competence_id}/sub-competences/{sub_id}",
    response_model=SubCompetenceResponse,
    summary="Update sub-competence",
)
async def update_sub_competence(
    competence_id: UUID,
    sub_id: UUID,
    data: UpdateSubCompetenceRequest,
    current_user: Annotated[User, Depends(require_evaluator)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SubCompetenceResponse:
    """Update a sub-competence."""
    stmt = select(SubCompetenceModel).where(
        SubCompetenceModel.id == sub_id,
        SubCompetenceModel.competence_id == competence_id,
    )
    result = await db.execute(stmt)
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Sub critério não encontrado")

    if data.max_score is not None and data.max_score != model.max_score:
        # Validate total doesn't exceed competence max_score
        comp_stmt = select(CompetenceModel).where(CompetenceModel.id == competence_id)
        comp_result = await db.execute(comp_stmt)
        competence = comp_result.scalar_one_or_none()
        if competence:
            other_stmt = select(SubCompetenceModel).where(
                SubCompetenceModel.competence_id == competence_id,
                SubCompetenceModel.id != sub_id,
            )
            other_result = await db.execute(other_stmt)
            others = other_result.scalars().all()
            other_sum = sum(s.max_score for s in others)
            if other_sum + data.max_score > competence.max_score:
                remaining = competence.max_score - other_sum
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Pontuação máxima excedida. Disponível: {remaining}."
                    ),
                )
        model.max_score = data.max_score

    if data.name is not None:
        model.name = data.name
    if data.description is not None:
        model.description = data.description
    if data.order is not None:
        model.order = data.order

    await db.commit()
    await db.refresh(model)
    return _model_to_response(model)


@router.delete(
    "/{competence_id}/sub-competences/{sub_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete sub-competence",
)
async def delete_sub_competence(
    competence_id: UUID,
    sub_id: UUID,
    current_user: Annotated[User, Depends(require_evaluator)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Delete a sub-competence."""
    stmt = select(SubCompetenceModel).where(
        SubCompetenceModel.id == sub_id,
        SubCompetenceModel.competence_id == competence_id,
    )
    result = await db.execute(stmt)
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Sub critério não encontrado")
    await db.delete(model)
    await db.commit()
