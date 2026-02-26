"""Application enumerations."""

from enum import Enum


class UserRole(str, Enum):
    """User roles in the system."""

    SUPER_ADMIN = "super_admin"
    EVALUATOR = "evaluator"
    COMPETITOR = "competitor"

    @classmethod
    def get_hierarchy(cls) -> dict[str, int]:
        """Get role hierarchy levels (higher number = more permissions)."""
        return {
            cls.COMPETITOR.value: 1,
            cls.EVALUATOR.value: 2,
            cls.SUPER_ADMIN.value: 3,
        }

    def has_permission_over(self, other: "UserRole") -> bool:
        """Check if this role has permission over another role."""
        hierarchy = self.get_hierarchy()
        return hierarchy[self.value] >= hierarchy[other.value]


class UserStatus(str, Enum):
    """User account status."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    SUSPENDED = "suspended"


class TokenType(str, Enum):
    """JWT token types."""

    ACCESS = "access"
    REFRESH = "refresh"


class TrainingType(str, Enum):
    """Training location type."""

    SENAI = "senai"
    EXTERNAL = "external"
    EMPRESA = "empresa"  # Company/business training
    AUTONOMO = "autonomo"  # Self-directed training


class TrainingStatus(str, Enum):
    """Training validation status."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    VALIDATED = "validated"  # Legacy alias for approved


class AssessmentType(str, Enum):
    """Assessment/exam types."""

    SIMULATION = "simulation"
    PRACTICAL = "practical"
    THEORETICAL = "theoretical"
    MIXED = "mixed"


class CompetenceLevel(str, Enum):
    """Competence proficiency levels."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


# =============================================================================
# Phase 6 - Extra Features Enums
# =============================================================================


class NotificationType(str, Enum):
    """Notification types."""

    INFO = "info"
    WARNING = "warning"
    ALERT = "alert"
    SUCCESS = "success"


class NotificationChannel(str, Enum):
    """Notification delivery channels."""

    IN_APP = "in_app"
    EMAIL = "email"
    PUSH = "push"


class NotificationStatus(str, Enum):
    """Notification status."""

    PENDING = "pending"
    SENT = "sent"
    READ = "read"
    FAILED = "failed"


class EventType(str, Enum):
    """Event types."""

    TRAINING = "training"
    EXAM = "exam"
    MEETING = "meeting"
    DEADLINE = "deadline"
    OTHER = "other"


class EventStatus(str, Enum):
    """Event status."""

    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ResourceType(str, Enum):
    """Resource types."""

    PDF = "pdf"
    VIDEO = "video"
    LINK = "link"
    IMAGE = "image"
    DOCUMENT = "document"


class ResourceAccessLevel(str, Enum):
    """Resource access levels."""

    PUBLIC = "public"
    MODALITY = "modality"
    PRIVATE = "private"


class GoalStatus(str, Enum):
    """Goal status."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class GoalPriority(str, Enum):
    """Goal priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BadgeCategory(str, Enum):
    """Badge categories."""

    TRAINING = "training"
    PERFORMANCE = "performance"
    CONSISTENCY = "consistency"
    ACHIEVEMENT = "achievement"
    SPECIAL = "special"


class BadgeRarity(str, Enum):
    """Badge rarity levels."""

    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


class MessageType(str, Enum):
    """Message types."""

    TEXT = "text"
    FILE = "file"
    SYSTEM = "system"


class FeedbackType(str, Enum):
    """Feedback types."""

    POSITIVE = "positive"
    CONSTRUCTIVE = "constructive"
    GENERAL = "general"


class TrainingPlanStatus(str, Enum):
    """Training plan status."""

    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"
