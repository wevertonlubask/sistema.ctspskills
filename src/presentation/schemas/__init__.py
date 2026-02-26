"""Pydantic schemas for request/response."""

from src.presentation.schemas.assessment_schema import (
    CompetenceStatisticsResponse,
    CompetitorAverageResponse,
    CompetitorExamSummaryResponse,
    CreateExamRequest,
    ExamListResponse,
    ExamResponse,
    ExamStatisticsResponse,
    GradeAuditResponse,
    GradeHistoryResponse,
    GradeListResponse,
    GradeResponse,
    GradeStatisticsResponse,
    RegisterGradeRequest,
    UpdateExamRequest,
    UpdateGradeRequest,
)
from src.presentation.schemas.auth_schema import (
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
)
from src.presentation.schemas.common import (
    ErrorDetail,
    ErrorResponse,
    MessageResponse,
    PaginationParams,
)
from src.presentation.schemas.modality_schema import (
    CompetenceResponse,
    CompetitorListResponse,
    CompetitorResponse,
    CreateCompetenceRequest,
    CreateCompetitorRequest,
    CreateModalityRequest,
    EnrollCompetitorRequest,
    EnrollmentResponse,
    ModalityListResponse,
    ModalityResponse,
    UpdateModalityRequest,
)
from src.presentation.schemas.training_schema import (
    CreateTrainingRequest,
    EvidenceResponse,
    PendingTrainingsCountResponse,
    TrainingListResponse,
    TrainingResponse,
    TrainingStatisticsResponse,
    UploadEvidenceRequest,
    ValidateTrainingRequest,
)
from src.presentation.schemas.user_schema import (
    UserListResponse,
    UserResponse,
)

__all__ = [
    # Auth
    "RegisterRequest",
    "LoginRequest",
    "RefreshTokenRequest",
    "TokenResponse",
    "LoginResponse",
    # User
    "UserResponse",
    "UserListResponse",
    # Common
    "ErrorResponse",
    "ErrorDetail",
    "MessageResponse",
    "PaginationParams",
    # Modality
    "ModalityResponse",
    "ModalityListResponse",
    "CreateModalityRequest",
    "UpdateModalityRequest",
    "CompetenceResponse",
    "CreateCompetenceRequest",
    "CompetitorResponse",
    "CompetitorListResponse",
    "CreateCompetitorRequest",
    "EnrollmentResponse",
    "EnrollCompetitorRequest",
    # Training
    "TrainingResponse",
    "TrainingListResponse",
    "CreateTrainingRequest",
    "ValidateTrainingRequest",
    "TrainingStatisticsResponse",
    "EvidenceResponse",
    "UploadEvidenceRequest",
    "PendingTrainingsCountResponse",
    # Assessment
    "ExamResponse",
    "ExamListResponse",
    "CreateExamRequest",
    "UpdateExamRequest",
    "GradeResponse",
    "GradeListResponse",
    "RegisterGradeRequest",
    "UpdateGradeRequest",
    "GradeAuditResponse",
    "GradeHistoryResponse",
    "GradeStatisticsResponse",
    "CompetenceStatisticsResponse",
    "ExamStatisticsResponse",
    "CompetitorAverageResponse",
    "CompetitorExamSummaryResponse",
]
