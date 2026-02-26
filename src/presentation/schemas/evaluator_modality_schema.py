"""Evaluator modality schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AssignModalityRequest(BaseModel):
    """Request to assign a modality to an evaluator."""

    modality_id: UUID = Field(..., description="Modality ID to assign")


class EvaluatorModalityResponse(BaseModel):
    """Evaluator modality assignment response."""

    id: UUID
    evaluator_id: UUID
    modality_id: UUID
    modality_code: str
    modality_name: str
    assigned_at: datetime
    assigned_by: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EvaluatorModalityListResponse(BaseModel):
    """List of evaluator modality assignments."""

    assignments: list[EvaluatorModalityResponse]
    total: int
