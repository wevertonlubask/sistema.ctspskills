"""Modality schemas."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from src.domain.modality.entities.enrollment import EnrollmentStatus


# Competence Schemas
class CompetenceBase(BaseModel):
    """Base competence schema."""

    name: str = Field(..., min_length=2, max_length=255, description="Competence name")
    description: str = Field(default="", max_length=1000, description="Competence description")
    weight: float = Field(default=1.0, ge=0.1, le=10.0, description="Scoring weight")
    max_score: float = Field(default=100.0, ge=1.0, le=1000.0, description="Maximum score")


class CreateCompetenceRequest(CompetenceBase):
    """Create competence request schema."""

    pass


class UpdateCompetenceRequest(BaseModel):
    """Update competence request schema."""

    name: str | None = Field(None, min_length=2, max_length=255)
    description: str | None = Field(None, max_length=1000)
    weight: float | None = Field(None, ge=0.1, le=10.0)
    max_score: float | None = Field(None, ge=1.0, le=1000.0)
    is_active: bool | None = None


class CompetenceResponse(CompetenceBase):
    """Competence response schema."""

    id: UUID
    modality_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Modality Schemas
class ModalityBase(BaseModel):
    """Base modality schema."""

    code: str = Field(
        ...,
        min_length=2,
        max_length=7,
        description="Modality code (e.g., WS17, IT, MECH01)",
    )
    name: str = Field(..., min_length=2, max_length=255, description="Modality name")
    description: str = Field(default="", max_length=2000, description="Modality description")
    min_training_hours: int | None = Field(
        None, ge=1, le=10000, description="Minimum training hours"
    )

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        """Validate and normalize code."""
        return v.strip().upper()


class CreateModalityRequest(ModalityBase):
    """Create modality request schema."""

    model_config = {
        "json_schema_extra": {
            "example": {
                "code": "WD17",
                "name": "Web Development",
                "description": "Development of web applications using modern technologies",
                "min_training_hours": 500,
            }
        }
    }


class UpdateModalityRequest(BaseModel):
    """Update modality request schema."""

    code: str | None = Field(None, min_length=2, max_length=7)
    name: str | None = Field(None, min_length=2, max_length=255)
    description: str | None = Field(None, max_length=2000)
    min_training_hours: int | None = Field(None, ge=1, le=10000)
    is_active: bool | None = None

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str | None) -> str | None:
        """Validate and normalize code."""
        if v is not None:
            return v.strip().upper()
        return v


class ModalityResponse(BaseModel):
    """Modality response schema."""

    id: UUID
    code: str
    name: str
    description: str
    is_active: bool
    min_training_hours: int | None
    competences: list[CompetenceResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ModalityListResponse(BaseModel):
    """Modality list response schema."""

    modalities: list[ModalityResponse]
    total: int
    skip: int
    limit: int
    has_more: bool


# Competitor Schemas
class CompetitorBase(BaseModel):
    """Base competitor schema."""

    full_name: str = Field(..., min_length=2, max_length=255, description="Full name")
    birth_date: date | None = Field(None, description="Birth date")
    document_number: str | None = Field(None, max_length=20, description="Document number")
    phone: str | None = Field(None, max_length=20, description="Phone number")
    emergency_contact: str | None = Field(None, max_length=255, description="Emergency contact")
    emergency_phone: str | None = Field(None, max_length=20, description="Emergency phone")
    notes: str | None = Field(None, max_length=1000, description="Additional notes")


class CreateCompetitorRequest(CompetitorBase):
    """Create competitor request schema."""

    user_id: UUID = Field(..., description="User ID to link competitor to")

    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "full_name": "John Doe",
                "birth_date": "2000-01-15",
                "phone": "+55 11 99999-9999",
            }
        }
    }


class UpdateCompetitorRequest(BaseModel):
    """Update competitor request schema."""

    full_name: str | None = Field(None, min_length=2, max_length=255)
    birth_date: date | None = None
    document_number: str | None = Field(None, max_length=20)
    phone: str | None = Field(None, max_length=20)
    emergency_contact: str | None = Field(None, max_length=255)
    emergency_phone: str | None = Field(None, max_length=20)
    notes: str | None = Field(None, max_length=1000)
    is_active: bool | None = None


class CompetitorResponse(CompetitorBase):
    """Competitor response schema."""

    id: UUID
    user_id: UUID
    email: str | None = Field(None, description="User email for login")
    is_active: bool
    age: int | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CompetitorListResponse(BaseModel):
    """Competitor list response schema."""

    competitors: list[CompetitorResponse]
    total: int
    skip: int
    limit: int
    has_more: bool


# Enrollment Schemas
class EnrollCompetitorRequest(BaseModel):
    """Enroll competitor request schema."""

    competitor_id: UUID = Field(..., description="Competitor ID to enroll")
    evaluator_id: UUID | None = Field(None, description="Optional evaluator to assign")
    notes: str | None = Field(None, max_length=1000, description="Enrollment notes")

    model_config = {
        "json_schema_extra": {
            "example": {
                "competitor_id": "550e8400-e29b-41d4-a716-446655440000",
                "evaluator_id": "660e8400-e29b-41d4-a716-446655440001",
            }
        }
    }


class AssignEvaluatorRequest(BaseModel):
    """Assign evaluator request schema."""

    evaluator_id: UUID = Field(..., description="Evaluator ID to assign")


class UpdateEnrollmentRequest(BaseModel):
    """Update enrollment request schema."""

    evaluator_id: UUID | None = Field(None, description="Evaluator ID to assign")
    status: EnrollmentStatus | None = Field(None, description="Enrollment status")
    notes: str | None = Field(None, max_length=1000, description="Enrollment notes")


class EnrollmentResponse(BaseModel):
    """Enrollment response schema."""

    id: UUID
    competitor_id: UUID
    modality_id: UUID
    evaluator_id: UUID | None
    enrolled_at: date
    status: EnrollmentStatus
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EnrollmentDetailResponse(BaseModel):
    """Enrollment response with competitor and modality details."""

    id: UUID
    competitor_id: UUID
    competitor_name: str
    modality_id: UUID
    modality_name: str
    modality_code: str
    evaluator_id: UUID | None
    evaluator_name: str | None
    enrolled_at: date
    status: EnrollmentStatus
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EnrollmentListResponse(BaseModel):
    """Enrollment list response schema."""

    enrollments: list[EnrollmentDetailResponse]
    total: int
    skip: int
    limit: int
    has_more: bool
