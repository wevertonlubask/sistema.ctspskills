"""SQLAlchemy models."""

from src.infrastructure.database.models.assessment_model import (
    ExamModel,
    GradeAuditLogModel,
    GradeModel,
    exam_competences,
)
from src.infrastructure.database.models.extras_model import (
    AchievementModel,
    BadgeModel,
    ConversationModel,
    EventModel,
    FeedbackModel,
    GoalModel,
    MessageModel,
    MilestoneModel,
    NotificationModel,
    PlanItemModel,
    ResourceModel,
    ScheduleModel,
    TrainingPlanModel,
    UserPointsModel,
    event_participants,
    plan_item_resources,
)
from src.infrastructure.database.models.modality_model import (
    CompetenceModel,
    CompetitorModel,
    EnrollmentModel,
    ModalityModel,
)
from src.infrastructure.database.models.training_model import (
    EvidenceModel,
    TrainingSessionModel,
)
from src.infrastructure.database.models.user_model import (
    PermissionModel,
    RefreshTokenModel,
    RoleModel,
    UserModel,
)

__all__ = [
    "UserModel",
    "RoleModel",
    "PermissionModel",
    "RefreshTokenModel",
    "ModalityModel",
    "CompetenceModel",
    "CompetitorModel",
    "EnrollmentModel",
    "TrainingSessionModel",
    "EvidenceModel",
    "ExamModel",
    "GradeModel",
    "GradeAuditLogModel",
    "exam_competences",
    "NotificationModel",
    "EventModel",
    "ScheduleModel",
    "ResourceModel",
    "GoalModel",
    "MilestoneModel",
    "BadgeModel",
    "AchievementModel",
    "UserPointsModel",
    "ConversationModel",
    "MessageModel",
    "FeedbackModel",
    "TrainingPlanModel",
    "PlanItemModel",
    "event_participants",
    "plan_item_resources",
]
