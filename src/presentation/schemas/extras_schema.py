"""Extra features schemas."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.shared.constants.enums import (
    EventType,
    FeedbackType,
    GoalPriority,
    MessageType,
    NotificationChannel,
    NotificationType,
    ResourceAccessLevel,
    ResourceType,
)

# =============================================================================
# Notification Schemas
# =============================================================================


class CreateNotificationRequest(BaseModel):
    """Create notification request."""

    user_id: UUID
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1, max_length=2000)
    notification_type: NotificationType = NotificationType.INFO
    channel: NotificationChannel = NotificationChannel.IN_APP
    related_entity_type: str | None = None
    related_entity_id: UUID | None = None
    action_url: str | None = None


class NotificationResponse(BaseModel):
    """Notification response."""

    id: UUID
    user_id: UUID
    title: str
    message: str
    notification_type: str
    channel: str
    status: str
    related_entity_type: str | None
    related_entity_id: UUID | None
    action_url: str | None
    is_read: bool
    read_at: datetime | None
    sent_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationListResponse(BaseModel):
    """Notification list response."""

    notifications: list[NotificationResponse]
    total: int
    unread_count: int


# =============================================================================
# Event Schemas
# =============================================================================


class CreateEventRequest(BaseModel):
    """Create event request."""

    title: str = Field(..., min_length=1, max_length=255)
    start_datetime: datetime
    end_datetime: datetime
    event_type: EventType = EventType.OTHER
    description: str | None = Field(None, max_length=2000)
    location: str | None = Field(None, max_length=500)
    modality_id: UUID | None = None
    is_all_day: bool = False
    recurrence_rule: str | None = None
    reminder_minutes: int | None = 30
    participant_ids: list[UUID] | None = None


class UpdateEventRequest(BaseModel):
    """Update event request."""

    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    start_datetime: datetime | None = None
    end_datetime: datetime | None = None
    location: str | None = Field(None, max_length=500)
    event_type: EventType | None = None


class EventResponse(BaseModel):
    """Event response."""

    id: UUID
    title: str
    description: str | None
    event_type: str
    start_datetime: datetime
    end_datetime: datetime
    location: str | None
    modality_id: UUID | None
    is_all_day: bool
    status: str
    recurrence_rule: str | None
    reminder_minutes: int | None
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    participants: list[UUID]
    duration_minutes: int

    model_config = {"from_attributes": True}


class EventListResponse(BaseModel):
    """Event list response."""

    events: list[EventResponse]
    total: int


# =============================================================================
# Resource Schemas
# =============================================================================


class CreateResourceRequest(BaseModel):
    """Create resource request."""

    title: str = Field(..., min_length=1, max_length=255)
    resource_type: ResourceType
    description: str | None = Field(None, max_length=2000)
    url: str | None = Field(None, max_length=1000)
    modality_id: UUID | None = None
    access_level: ResourceAccessLevel = ResourceAccessLevel.MODALITY
    tags: list[str] | None = None


class ResourceResponse(BaseModel):
    """Resource response."""

    id: UUID
    title: str
    description: str | None
    resource_type: str
    url: str | None
    file_path: str | None
    file_size: int | None
    mime_type: str | None
    modality_id: UUID | None
    access_level: str
    tags: list[str]
    is_active: bool
    view_count: int
    download_count: int
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ResourceListResponse(BaseModel):
    """Resource list response."""

    resources: list[ResourceResponse]
    total: int


# =============================================================================
# Goal Schemas
# =============================================================================


class CreateMilestoneRequest(BaseModel):
    """Create milestone request."""

    title: str = Field(..., min_length=1, max_length=255)
    target_value: float = Field(..., gt=0)
    due_date: date | None = None


class MilestoneResponse(BaseModel):
    """Milestone response."""

    id: UUID
    goal_id: UUID
    title: str
    target_value: float
    current_value: float
    due_date: date | None
    is_completed: bool
    completed_at: datetime | None
    progress_percentage: float
    is_overdue: bool

    model_config = {"from_attributes": True}


class CreateGoalRequest(BaseModel):
    """Create goal request."""

    title: str = Field(..., min_length=1, max_length=255)
    competitor_id: UUID
    description: str | None = Field(None, max_length=2000)
    target_value: float = Field(default=100.0, gt=0)
    unit: str = "percent"
    priority: GoalPriority = GoalPriority.MEDIUM
    start_date: date | None = None
    due_date: date | None = None
    modality_id: UUID | None = None
    competence_id: UUID | None = None
    milestones: list[CreateMilestoneRequest] | None = None


class GoalResponse(BaseModel):
    """Goal response."""

    id: UUID
    title: str
    description: str | None
    competitor_id: UUID
    target_value: float
    current_value: float
    unit: str
    priority: str
    status: str
    start_date: date
    due_date: date | None
    modality_id: UUID | None
    competence_id: UUID | None
    progress_percentage: float
    is_overdue: bool
    days_remaining: int | None
    needs_alert: bool
    milestones: list[MilestoneResponse]
    completed_milestones: int
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class GoalListResponse(BaseModel):
    """Goal list response."""

    goals: list[GoalResponse]
    total: int
    overdue_count: int


class UpdateGoalProgressRequest(BaseModel):
    """Update goal progress request."""

    current_value: float = Field(..., ge=0)


# =============================================================================
# Badge Schemas
# =============================================================================


class BadgeResponse(BaseModel):
    """Badge response."""

    id: UUID
    name: str
    description: str
    category: str
    rarity: str
    icon_url: str | None
    points: int
    criteria: dict
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AchievementResponse(BaseModel):
    """Achievement response."""

    id: UUID
    badge_id: UUID
    user_id: UUID
    competitor_id: UUID | None
    earned_at: datetime
    progress: float
    is_complete: bool
    metadata: dict
    badge: BadgeResponse | None = None

    model_config = {"from_attributes": True}


class UserPointsResponse(BaseModel):
    """User points response."""

    user_id: UUID
    total_points: int
    level: int
    badges_count: int
    points_to_next_level: int

    model_config = {"from_attributes": True}


class LeaderboardEntryResponse(BaseModel):
    """Leaderboard entry response."""

    position: int
    user_id: UUID
    user_name: str
    total_points: int
    level: int
    badges_count: int


class LeaderboardResponse(BaseModel):
    """Leaderboard response."""

    entries: list[LeaderboardEntryResponse]
    total: int


# =============================================================================
# Message Schemas
# =============================================================================


class CreateConversationRequest(BaseModel):
    """Create conversation request."""

    participant_2: UUID
    title: str | None = Field(None, max_length=255)
    modality_id: UUID | None = None
    initial_message: str | None = Field(None, max_length=2000)


class CreateMessageRequest(BaseModel):
    """Create message request."""

    content: str = Field(..., min_length=1, max_length=2000)
    message_type: MessageType = MessageType.TEXT
    file_url: str | None = None


class MessageResponse(BaseModel):
    """Message response."""

    id: UUID
    conversation_id: UUID
    sender_id: UUID
    content: str
    message_type: str
    file_url: str | None
    is_read: bool
    read_at: datetime | None
    is_deleted: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationResponse(BaseModel):
    """Conversation response."""

    id: UUID
    participant_1: UUID
    participant_2: UUID
    title: str | None
    modality_id: UUID | None
    is_active: bool
    last_message_at: datetime | None
    unread_count: int
    created_at: datetime
    updated_at: datetime
    other_participant_name: str | None = None
    last_message: MessageResponse | None = None

    model_config = {"from_attributes": True}


class ConversationListResponse(BaseModel):
    """Conversation list response."""

    conversations: list[ConversationResponse]
    total: int
    total_unread: int


class MessageListResponse(BaseModel):
    """Message list response."""

    messages: list[MessageResponse]
    total: int
    has_more: bool


# =============================================================================
# Feedback Schemas
# =============================================================================


class CreateFeedbackRequest(BaseModel):
    """Create feedback request."""

    competitor_id: UUID
    content: str = Field(..., min_length=1, max_length=2000)
    feedback_type: FeedbackType = FeedbackType.GENERAL
    exam_id: UUID | None = None
    competence_id: UUID | None = None
    grade_id: UUID | None = None
    training_id: UUID | None = None
    rating: int | None = Field(None, ge=1, le=5)
    is_private: bool = False


class FeedbackResponse(BaseModel):
    """Feedback response."""

    id: UUID
    competitor_id: UUID
    evaluator_id: UUID
    content: str
    feedback_type: str
    exam_id: UUID | None
    competence_id: UUID | None
    grade_id: UUID | None
    training_id: UUID | None
    rating: int | None
    is_private: bool
    is_read: bool
    read_at: datetime | None
    related_context: str
    created_at: datetime
    evaluator_name: str | None = None

    model_config = {"from_attributes": True}


class FeedbackListResponse(BaseModel):
    """Feedback list response."""

    feedbacks: list[FeedbackResponse]
    total: int
    unread_count: int


# =============================================================================
# Training Plan Schemas
# =============================================================================


class CreatePlanItemRequest(BaseModel):
    """Create plan item request."""

    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    competence_id: UUID | None = None
    duration_hours: float = Field(default=1.0, gt=0)
    is_required: bool = True
    due_date: date | None = None
    notes: str | None = None
    resource_ids: list[UUID] | None = None


class PlanItemResponse(BaseModel):
    """Plan item response."""

    id: UUID
    plan_id: UUID
    title: str
    description: str | None
    competence_id: UUID | None
    order: int
    duration_hours: float
    is_required: bool
    is_completed: bool
    completed_at: datetime | None
    due_date: date | None
    notes: str | None
    resource_ids: list[UUID]
    is_overdue: bool

    model_config = {"from_attributes": True}


class CreateTrainingPlanRequest(BaseModel):
    """Create training plan request."""

    title: str = Field(..., min_length=1, max_length=255)
    competitor_id: UUID
    description: str | None = Field(None, max_length=2000)
    modality_id: UUID | None = None
    priority: GoalPriority = GoalPriority.MEDIUM
    start_date: date | None = None
    end_date: date | None = None
    target_hours: float = Field(default=0.0, ge=0)
    items: list[CreatePlanItemRequest] | None = None


class TrainingPlanResponse(BaseModel):
    """Training plan response."""

    id: UUID
    title: str
    description: str | None
    competitor_id: UUID
    modality_id: UUID | None
    status: str
    priority: str
    start_date: date | None
    end_date: date | None
    target_hours: float
    is_suggested: bool
    total_hours: float
    completed_hours: float
    progress_percentage: float
    required_items_completed: bool
    is_overdue: bool
    items: list[PlanItemResponse]
    overdue_items_count: int
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TrainingPlanListResponse(BaseModel):
    """Training plan list response."""

    plans: list[TrainingPlanResponse]
    total: int
    active_count: int


class AddPlanItemRequest(BaseModel):
    """Add plan item request."""

    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    competence_id: UUID | None = None
    duration_hours: float = Field(default=1.0, gt=0)
    is_required: bool = True


class ReorderItemsRequest(BaseModel):
    """Reorder items request."""

    item_ids: list[UUID]
