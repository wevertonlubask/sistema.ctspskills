"""Assessment schemas."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.shared.constants.enums import AssessmentType


# Exam Schemas
class CreateExamRequest(BaseModel):
    """Create exam request schema."""

    name: str = Field(..., min_length=3, max_length=255, description="Exam name")
    modality_id: UUID = Field(..., description="Modality ID for the exam")
    assessment_type: AssessmentType = Field(..., description="Type of assessment")
    exam_date: date = Field(..., description="Date of the exam")
    description: str | None = Field(None, max_length=2000, description="Exam description")
    competence_ids: list[UUID] | None = Field(
        None,
        description="List of competence IDs to evaluate",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Simulado de Desenvolvimento Web",
                "modality_id": "550e8400-e29b-41d4-a716-446655440000",
                "assessment_type": "simulation",
                "exam_date": "2024-02-15",
                "description": "Simulado prático de desenvolvimento web com React",
                "competence_ids": [
                    "550e8400-e29b-41d4-a716-446655440001",
                    "550e8400-e29b-41d4-a716-446655440002",
                ],
            }
        }
    }


class UpdateExamRequest(BaseModel):
    """Update exam request schema."""

    name: str | None = Field(None, min_length=3, max_length=255)
    description: str | None = Field(None, max_length=2000)
    exam_date: date | None = None
    assessment_type: AssessmentType | None = None
    competence_ids: list[UUID] | None = None
    is_active: bool | None = None


class ExamResponse(BaseModel):
    """Exam response schema."""

    id: UUID
    name: str
    description: str | None
    modality_id: UUID
    assessment_type: AssessmentType
    exam_date: date
    is_active: bool
    competence_ids: list[UUID]
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ExamListResponse(BaseModel):
    """Exam list response schema."""

    exams: list[ExamResponse]
    total: int
    skip: int
    limit: int
    has_more: bool


# Grade Schemas
class RegisterGradeRequest(BaseModel):
    """Register grade request schema."""

    exam_id: UUID = Field(..., description="Exam ID")
    competitor_id: UUID = Field(..., description="Competitor ID")
    competence_id: UUID = Field(..., description="Competence ID")
    score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Score value (0-100, RN03)",
    )
    notes: str | None = Field(None, max_length=1000, description="Optional notes")

    model_config = {
        "json_schema_extra": {
            "example": {
                "exam_id": "550e8400-e29b-41d4-a716-446655440000",
                "competitor_id": "550e8400-e29b-41d4-a716-446655440001",
                "competence_id": "550e8400-e29b-41d4-a716-446655440002",
                "score": 85.5,
                "notes": "Good performance on state management",
            }
        }
    }


class UpdateGradeRequest(BaseModel):
    """Update grade request schema."""

    score: float | None = Field(None, ge=0.0, le=100.0)
    notes: str | None = Field(None, max_length=1000)


class GradeResponse(BaseModel):
    """Grade response schema."""

    id: UUID
    exam_id: UUID
    competitor_id: UUID
    competence_id: UUID
    score: float
    notes: str | None
    created_by: UUID
    updated_by: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class GradeListResponse(BaseModel):
    """Grade list response schema."""

    grades: list[GradeResponse]
    total: int
    skip: int
    limit: int
    has_more: bool


# Audit Schemas
class GradeAuditResponse(BaseModel):
    """Grade audit log response schema."""

    id: UUID
    grade_id: UUID
    action: str
    old_score: float | None
    new_score: float | None
    old_notes: str | None
    new_notes: str | None
    changed_by: UUID
    ip_address: str | None
    user_agent: str | None
    changed_at: datetime

    model_config = {"from_attributes": True}


class GradeHistoryResponse(BaseModel):
    """Grade history response schema."""

    grade: GradeResponse
    history: list[GradeAuditResponse]


# Statistics Schemas
class GradeStatisticsResponse(BaseModel):
    """Grade statistics response schema."""

    average: float
    median: float
    std_deviation: float
    min_score: float
    max_score: float
    count: int


class CompetenceStatisticsResponse(BaseModel):
    """Competence statistics response schema."""

    competence_id: UUID
    average: float
    median: float
    std_deviation: float
    min_score: float
    max_score: float
    count: int


class ExamStatisticsResponse(BaseModel):
    """Exam statistics response schema."""

    exam_id: UUID
    total_competitors: int
    total_grades: int
    overall_average: float
    competence_stats: list[CompetenceStatisticsResponse]


class CompetitorAverageResponse(BaseModel):
    """Competitor average response schema."""

    competitor_id: UUID
    average: float | None
    modality_id: UUID | None = None
    competence_id: UUID | None = None
    exam_id: UUID | None = None


class CompetitorExamSummaryResponse(BaseModel):
    """Competitor exam summary response schema."""

    competitor_id: UUID
    exam_id: UUID
    grades_count: int
    average: float | None
    weighted_average: float | None
