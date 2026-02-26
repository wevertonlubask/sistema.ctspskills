"""Training schemas."""

from datetime import date, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from src.domain.training.entities.evidence import EvidenceType
from src.shared.constants.enums import TrainingStatus, TrainingType


# Evidence Schemas
class EvidenceResponse(BaseModel):
    """Evidence response schema."""

    id: UUID
    training_session_id: UUID
    file_name: str
    file_path: str
    file_size: int
    mime_type: str
    evidence_type: EvidenceType
    description: str | None
    uploaded_by: UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UploadEvidenceRequest(BaseModel):
    """Upload evidence request schema (for metadata only, file is in form data)."""

    evidence_type: EvidenceType = Field(default=EvidenceType.PHOTO)
    description: str | None = Field(None, max_length=500)


# Training Schemas
class CreateTrainingRequest(BaseModel):
    """Create training request schema."""

    modality_id: UUID = Field(..., description="Modality ID for the training")
    training_date: date = Field(..., description="Date of the training")
    hours: float = Field(
        ...,
        ge=0.5,
        le=12.0,
        description="Training hours (0.5 to 12, RN04)",
    )
    training_type: TrainingType = Field(
        default=TrainingType.SENAI,
        description="Location type (SENAI or EXTERNAL)",
    )
    location: str | None = Field(None, max_length=255, description="Specific location")
    description: str | None = Field(None, max_length=2000, description="Activity description")

    @field_validator("training_date")
    @classmethod
    def validate_training_date(cls, v: date) -> date:
        """Validate training date is not in the future."""
        if v > date.today():
            raise ValueError("Training date cannot be in the future")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "modality_id": "550e8400-e29b-41d4-a716-446655440000",
                "training_date": "2024-01-15",
                "hours": 4.0,
                "training_type": "senai",
                "location": "SENAI Curitiba - Lab 3",
                "description": "Practice with React components and state management",
            }
        }
    }


class UpdateTrainingRequest(BaseModel):
    """Update training request schema (for evaluator/admin corrections)."""

    training_date: date | None = Field(None, description="Date of the training")
    hours: float | None = Field(
        None,
        ge=0.5,
        le=12.0,
        description="Training hours (0.5 to 12)",
    )
    training_type: TrainingType | None = Field(None, description="Location type")
    location: str | None = Field(None, max_length=255, description="Specific location")
    description: str | None = Field(None, max_length=2000, description="Activity description")


class ValidateTrainingRequest(BaseModel):
    """Validate training request schema."""

    approved: bool = Field(..., description="Whether to approve or reject")
    rejection_reason: str | None = Field(
        None,
        max_length=1000,
        description="Required when rejecting",
    )

    @field_validator("rejection_reason")
    @classmethod
    def validate_rejection_reason(cls, v: str | None, info: Any) -> str | None:
        """Validate rejection reason is provided when rejecting."""
        approved = info.data.get("approved")
        if not approved and not v:
            raise ValueError("Rejection reason is required when rejecting training")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "approved": True,
            }
        }
    }


class TrainingResponse(BaseModel):
    """Training response schema."""

    id: UUID
    competitor_id: UUID
    competitor_name: str | None = None  # Nome do competidor
    modality_id: UUID
    modality_name: str | None = None  # Nome da modalidade
    enrollment_id: UUID
    training_date: date
    hours: float
    training_type: TrainingType
    location: str | None
    description: str | None
    status: TrainingStatus
    validated_by: UUID | None
    validated_at: datetime | None
    rejection_reason: str | None
    evidences: list[EvidenceResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TrainingListResponse(BaseModel):
    """Training list response schema."""

    trainings: list[TrainingResponse]
    total: int
    skip: int
    limit: int
    has_more: bool


class TrainingStatisticsResponse(BaseModel):
    """Training statistics response schema."""

    competitor_id: UUID
    modality_id: UUID | None
    senai_hours: float
    external_hours: float
    total_approved_hours: float
    total_sessions: int
    pending_sessions: int
    approved_sessions: int
    rejected_sessions: int

    model_config = {"from_attributes": True}


class PendingTrainingsCountResponse(BaseModel):
    """Pending trainings count response."""

    count: int
    evaluator_id: UUID | None = None
    modality_id: UUID | None = None


# Training Type Config Schemas
class CreateTrainingTypeConfigRequest(BaseModel):
    """Create training type config request schema."""

    code: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Unique code for the training type",
    )
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Display name for the training type",
    )
    description: str | None = Field(
        None,
        max_length=500,
        description="Optional description",
    )
    display_order: int = Field(
        default=0,
        ge=0,
        description="Display order in UI",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "code": "empresa",
                "name": "Empresa",
                "description": "Treinamento realizado em empresa parceira",
                "display_order": 3,
            }
        }
    }


class UpdateTrainingTypeConfigRequest(BaseModel):
    """Update training type config request schema."""

    name: str | None = Field(
        None,
        min_length=2,
        max_length=100,
        description="Display name for the training type",
    )
    description: str | None = Field(
        None,
        max_length=500,
        description="Optional description",
    )
    display_order: int | None = Field(
        None,
        ge=0,
        description="Display order in UI",
    )
    is_active: bool | None = Field(
        None,
        description="Whether the type is active",
    )


class TrainingTypeConfigResponse(BaseModel):
    """Training type config response schema."""

    id: UUID
    code: str
    name: str
    description: str | None
    is_active: bool
    display_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TrainingTypeConfigListResponse(BaseModel):
    """Training type config list response schema."""

    items: list[TrainingTypeConfigResponse]
    total: int
    skip: int
    limit: int
    has_more: bool
