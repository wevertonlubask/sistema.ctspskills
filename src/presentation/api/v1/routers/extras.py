"""Extra features router - Notifications, Events, Resources, Goals, Badges, Messages, Feedback, Training Plans."""

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.identity.entities.user import User
from src.presentation.api.v1.dependencies.auth import (
    get_current_active_user,
    require_evaluator,
)
from src.presentation.api.v1.dependencies.database import get_db
from src.presentation.schemas.extras_schema import (
    AchievementResponse,
    AddPlanItemRequest,
    # Badge schemas
    BadgeResponse,
    ConversationListResponse,
    ConversationResponse,
    # Message schemas
    CreateConversationRequest,
    # Event schemas
    CreateEventRequest,
    # Feedback schemas
    CreateFeedbackRequest,
    # Goal schemas
    CreateGoalRequest,
    CreateMessageRequest,
    # Notification schemas
    CreateResourceRequest,
    # Training Plan schemas
    CreateTrainingPlanRequest,
    EventListResponse,
    EventResponse,
    FeedbackListResponse,
    FeedbackResponse,
    GoalListResponse,
    GoalResponse,
    LeaderboardResponse,
    MessageListResponse,
    MessageResponse,
    NotificationListResponse,
    PlanItemResponse,
    ReorderItemsRequest,
    ResourceListResponse,
    ResourceResponse,
    TrainingPlanListResponse,
    TrainingPlanResponse,
    UpdateEventRequest,
    UpdateGoalProgressRequest,
    UserPointsResponse,
)
from src.shared.constants.enums import (
    BadgeCategory,
    BadgeRarity,
    FeedbackType,
    GoalStatus,
    NotificationStatus,
    ResourceType,
    TrainingPlanStatus,
)

router = APIRouter()


# =============================================================================
# Notification Endpoints
# =============================================================================


@router.get(
    "/notifications",
    response_model=NotificationListResponse,
    summary="List notifications",
    description="List notifications for the current user.",
    tags=["Notifications"],
)
async def list_notifications(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    status: NotificationStatus | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> NotificationListResponse:
    """List notifications for the current user."""
    # Implementation would use ListNotificationsUseCase
    return NotificationListResponse(
        notifications=[],
        total=0,
        unread_count=0,
    )


@router.post(
    "/notifications/{notification_id}/read",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Mark notification as read",
    tags=["Notifications"],
)
async def mark_notification_read(
    notification_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Mark a notification as read."""
    # Implementation would use MarkNotificationReadUseCase
    pass


@router.post(
    "/notifications/read-all",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Mark all notifications as read",
    tags=["Notifications"],
)
async def mark_all_notifications_read(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Mark all notifications as read."""
    # Implementation would use MarkNotificationReadUseCase.mark_all_read
    pass


# =============================================================================
# Event Endpoints
# =============================================================================


@router.post(
    "/events",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create event",
    tags=["Events"],
)
async def create_event(
    data: CreateEventRequest,
    current_user: Annotated[User, Depends(require_evaluator)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> EventResponse:
    """Create a new event."""
    # Implementation would use CreateEventUseCase
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get(
    "/events",
    response_model=EventListResponse,
    summary="List events",
    tags=["Events"],
)
async def list_events(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    modality_id: UUID | None = Query(default=None),
) -> EventListResponse:
    """List events in a date range."""
    # Implementation would use ListEventsUseCase
    return EventListResponse(events=[], total=0)


@router.get(
    "/events/upcoming",
    response_model=EventListResponse,
    summary="Get upcoming events",
    tags=["Events"],
)
async def get_upcoming_events(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    modality_id: UUID | None = Query(default=None),
    limit: int = Query(default=10, ge=1, le=50),
) -> EventListResponse:
    """Get upcoming events."""
    # Implementation would use ListEventsUseCase.get_upcoming
    return EventListResponse(events=[], total=0)


@router.put(
    "/events/{event_id}",
    response_model=EventResponse,
    summary="Update event",
    tags=["Events"],
)
async def update_event(
    event_id: UUID,
    data: UpdateEventRequest,
    current_user: Annotated[User, Depends(require_evaluator)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> EventResponse:
    """Update an event."""
    # Implementation would use UpdateEventUseCase
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post(
    "/events/{event_id}/cancel",
    response_model=EventResponse,
    summary="Cancel event",
    tags=["Events"],
)
async def cancel_event(
    event_id: UUID,
    current_user: Annotated[User, Depends(require_evaluator)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> EventResponse:
    """Cancel an event."""
    # Implementation would use UpdateEventUseCase.cancel
    raise HTTPException(status_code=501, detail="Not implemented")


# =============================================================================
# Resource Endpoints
# =============================================================================


@router.post(
    "/resources",
    response_model=ResourceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create resource",
    tags=["Resources"],
)
async def create_resource(
    data: CreateResourceRequest,
    current_user: Annotated[User, Depends(require_evaluator)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ResourceResponse:
    """Create a new resource."""
    # Implementation would use CreateResourceUseCase
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get(
    "/resources",
    response_model=ResourceListResponse,
    summary="List resources",
    tags=["Resources"],
)
async def list_resources(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    modality_id: UUID | None = Query(default=None),
    resource_type: ResourceType | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> ResourceListResponse:
    """List resources."""
    # Implementation would use ListResourcesUseCase
    return ResourceListResponse(resources=[], total=0)


@router.get(
    "/resources/search",
    response_model=ResourceListResponse,
    summary="Search resources",
    tags=["Resources"],
)
async def search_resources(
    query: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    modality_id: UUID | None = Query(default=None),
    resource_type: ResourceType | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> ResourceListResponse:
    """Search resources."""
    # Implementation would use ListResourcesUseCase.search
    return ResourceListResponse(resources=[], total=0)


@router.get(
    "/resources/{resource_id}",
    response_model=ResourceResponse,
    summary="Get resource",
    tags=["Resources"],
)
async def get_resource(
    resource_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ResourceResponse:
    """Get a resource by ID."""
    # Implementation would use GetResourceUseCase
    raise HTTPException(status_code=501, detail="Not implemented")


# =============================================================================
# Goal Endpoints
# =============================================================================


@router.post(
    "/goals",
    response_model=GoalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create goal",
    tags=["Goals"],
)
async def create_goal(
    data: CreateGoalRequest,
    current_user: Annotated[User, Depends(require_evaluator)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> GoalResponse:
    """Create a new goal."""
    # Implementation would use CreateGoalUseCase
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get(
    "/goals",
    response_model=GoalListResponse,
    summary="List goals",
    tags=["Goals"],
)
async def list_goals(
    competitor_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    status: GoalStatus | None = Query(default=None),
    modality_id: UUID | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> GoalListResponse:
    """List goals for a competitor."""
    # Implementation would use ListGoalsUseCase
    return GoalListResponse(goals=[], total=0, overdue_count=0)


@router.put(
    "/goals/{goal_id}/progress",
    response_model=GoalResponse,
    summary="Update goal progress",
    tags=["Goals"],
)
async def update_goal_progress(
    goal_id: UUID,
    data: UpdateGoalProgressRequest,
    current_user: Annotated[User, Depends(require_evaluator)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> GoalResponse:
    """Update goal progress."""
    # Implementation would use UpdateGoalProgressUseCase
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get(
    "/goals/alerts",
    response_model=list[GoalResponse],
    summary="Get goals needing alerts (RN10)",
    tags=["Goals"],
)
async def get_goal_alerts(
    current_user: Annotated[User, Depends(require_evaluator)],
    db: Annotated[AsyncSession, Depends(get_db)],
    days_threshold: int = Query(default=7, ge=1, le=30),
) -> list[GoalResponse]:
    """Get goals needing alerts (RN10 - automatic alerts)."""
    # Implementation would use CheckGoalAlertsUseCase
    return []


# =============================================================================
# Badge Endpoints
# =============================================================================


@router.get(
    "/badges",
    response_model=list[BadgeResponse],
    summary="List badges",
    tags=["Gamification"],
)
async def list_badges(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    category: BadgeCategory | None = Query(default=None),
    rarity: BadgeRarity | None = Query(default=None),
) -> list[BadgeResponse]:
    """List all available badges."""
    # Implementation would use ListBadgesUseCase
    return []


@router.get(
    "/badges/achievements",
    response_model=list[AchievementResponse],
    summary="Get user achievements",
    tags=["Gamification"],
)
async def get_user_achievements(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[AchievementResponse]:
    """Get achievements for the current user."""
    # Implementation would use ListBadgesUseCase.get_user_achievements
    return []


@router.get(
    "/badges/points",
    response_model=UserPointsResponse,
    summary="Get user points",
    tags=["Gamification"],
)
async def get_user_points(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserPointsResponse:
    """Get points for the current user."""
    # Implementation would use ListBadgesUseCase.get_user_points
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get(
    "/badges/leaderboard",
    response_model=LeaderboardResponse,
    summary="Get leaderboard",
    tags=["Gamification"],
)
async def get_leaderboard(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    modality_id: UUID | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
) -> LeaderboardResponse:
    """Get gamification leaderboard."""
    # Implementation would use GetLeaderboardUseCase
    return LeaderboardResponse(entries=[], total=0)


# =============================================================================
# Message Endpoints
# =============================================================================


@router.post(
    "/conversations",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create conversation",
    tags=["Messages"],
)
async def create_conversation(
    data: CreateConversationRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ConversationResponse:
    """Create a new conversation."""
    # Implementation would use SendMessageUseCase.create_conversation
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get(
    "/conversations",
    response_model=ConversationListResponse,
    summary="List conversations",
    tags=["Messages"],
)
async def list_conversations(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> ConversationListResponse:
    """List conversations for the current user."""
    # Implementation would use ListConversationsUseCase
    return ConversationListResponse(conversations=[], total=0, total_unread=0)


@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=MessageListResponse,
    summary="List messages",
    tags=["Messages"],
)
async def list_messages(
    conversation_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    before_id: UUID | None = Query(default=None),
) -> MessageListResponse:
    """List messages in a conversation."""
    # Implementation would use ListMessagesUseCase
    return MessageListResponse(messages=[], total=0, has_more=False)


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Send message",
    tags=["Messages"],
)
async def send_message(
    conversation_id: UUID,
    data: CreateMessageRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MessageResponse:
    """Send a message in a conversation."""
    # Implementation would use SendMessageUseCase
    raise HTTPException(status_code=501, detail="Not implemented")


# =============================================================================
# Feedback Endpoints
# =============================================================================


@router.post(
    "/feedback",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create feedback",
    tags=["Feedback"],
)
async def create_feedback(
    data: CreateFeedbackRequest,
    current_user: Annotated[User, Depends(require_evaluator)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> FeedbackResponse:
    """Create feedback for a competitor."""
    # Implementation would use CreateFeedbackUseCase
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get(
    "/feedback",
    response_model=FeedbackListResponse,
    summary="List feedback",
    tags=["Feedback"],
)
async def list_feedback(
    competitor_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    feedback_type: FeedbackType | None = Query(default=None),
    is_read: bool | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> FeedbackListResponse:
    """List feedback for a competitor."""
    # Implementation would use ListFeedbackUseCase
    return FeedbackListResponse(feedbacks=[], total=0, unread_count=0)


@router.post(
    "/feedback/{feedback_id}/read",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Mark feedback as read",
    tags=["Feedback"],
)
async def mark_feedback_read(
    feedback_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Mark feedback as read."""
    # Implementation would use ListFeedbackUseCase.mark_as_read
    pass


# =============================================================================
# Training Plan Endpoints
# =============================================================================


@router.post(
    "/training-plans",
    response_model=TrainingPlanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create training plan",
    tags=["Training Plans"],
)
async def create_training_plan(
    data: CreateTrainingPlanRequest,
    current_user: Annotated[User, Depends(require_evaluator)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TrainingPlanResponse:
    """Create a new training plan."""
    # Implementation would use CreateTrainingPlanUseCase
    raise HTTPException(status_code=501, detail="Not implemented")


@router.get(
    "/training-plans",
    response_model=TrainingPlanListResponse,
    summary="List training plans",
    tags=["Training Plans"],
)
async def list_training_plans(
    competitor_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    status: TrainingPlanStatus | None = Query(default=None),
    modality_id: UUID | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> TrainingPlanListResponse:
    """List training plans for a competitor."""
    # Implementation would use ListTrainingPlansUseCase
    return TrainingPlanListResponse(plans=[], total=0, active_count=0)


@router.get(
    "/training-plans/suggested",
    response_model=list[TrainingPlanResponse],
    summary="Get suggested plans",
    tags=["Training Plans"],
)
async def get_suggested_plans(
    competitor_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    modality_id: UUID | None = Query(default=None),
) -> list[TrainingPlanResponse]:
    """Get suggested training plans for a competitor."""
    # Implementation would use ListTrainingPlansUseCase.get_suggested
    return []


@router.get(
    "/training-plans/{plan_id}",
    response_model=TrainingPlanResponse,
    summary="Get training plan",
    tags=["Training Plans"],
)
async def get_training_plan(
    plan_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TrainingPlanResponse:
    """Get a training plan by ID."""
    # Implementation would get plan from repository
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post(
    "/training-plans/{plan_id}/activate",
    response_model=TrainingPlanResponse,
    summary="Activate training plan",
    tags=["Training Plans"],
)
async def activate_training_plan(
    plan_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TrainingPlanResponse:
    """Activate a training plan."""
    # Implementation would use UpdatePlanProgressUseCase.activate_plan
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post(
    "/training-plans/{plan_id}/complete",
    response_model=TrainingPlanResponse,
    summary="Complete training plan",
    tags=["Training Plans"],
)
async def complete_training_plan(
    plan_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TrainingPlanResponse:
    """Mark a training plan as completed."""
    # Implementation would use UpdatePlanProgressUseCase.complete_plan
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post(
    "/training-plans/{plan_id}/items",
    response_model=TrainingPlanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add plan item",
    tags=["Training Plans"],
)
async def add_plan_item(
    plan_id: UUID,
    data: AddPlanItemRequest,
    current_user: Annotated[User, Depends(require_evaluator)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TrainingPlanResponse:
    """Add an item to a training plan."""
    # Implementation would use UpdatePlanProgressUseCase.add_item
    raise HTTPException(status_code=501, detail="Not implemented")


@router.post(
    "/training-plans/{plan_id}/items/{item_id}/complete",
    response_model=PlanItemResponse,
    summary="Complete plan item",
    tags=["Training Plans"],
)
async def complete_plan_item(
    plan_id: UUID,
    item_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PlanItemResponse:
    """Mark a plan item as completed."""
    # Implementation would use UpdatePlanProgressUseCase.complete_item
    raise HTTPException(status_code=501, detail="Not implemented")


@router.put(
    "/training-plans/{plan_id}/items/reorder",
    response_model=TrainingPlanResponse,
    summary="Reorder plan items",
    tags=["Training Plans"],
)
async def reorder_plan_items(
    plan_id: UUID,
    data: ReorderItemsRequest,
    current_user: Annotated[User, Depends(require_evaluator)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TrainingPlanResponse:
    """Reorder items in a training plan."""
    # Implementation would use UpdatePlanProgressUseCase.reorder_items
    raise HTTPException(status_code=501, detail="Not implemented")
