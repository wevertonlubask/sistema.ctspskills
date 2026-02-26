"""Extra features DTOs."""

from src.application.extras.dtos.badge_dto import AchievementDTO, BadgeDTO, UserPointsDTO
from src.application.extras.dtos.event_dto import CreateEventDTO, EventDTO, UpdateEventDTO
from src.application.extras.dtos.feedback_dto import CreateFeedbackDTO, FeedbackDTO
from src.application.extras.dtos.goal_dto import CreateGoalDTO, GoalDTO, MilestoneDTO
from src.application.extras.dtos.message_dto import ConversationDTO, CreateMessageDTO, MessageDTO
from src.application.extras.dtos.notification_dto import CreateNotificationDTO, NotificationDTO
from src.application.extras.dtos.resource_dto import CreateResourceDTO, ResourceDTO
from src.application.extras.dtos.training_plan_dto import (
    CreatePlanDTO,
    PlanItemDTO,
    TrainingPlanDTO,
)

__all__ = [
    "NotificationDTO",
    "CreateNotificationDTO",
    "EventDTO",
    "CreateEventDTO",
    "UpdateEventDTO",
    "ResourceDTO",
    "CreateResourceDTO",
    "GoalDTO",
    "CreateGoalDTO",
    "MilestoneDTO",
    "BadgeDTO",
    "AchievementDTO",
    "UserPointsDTO",
    "MessageDTO",
    "ConversationDTO",
    "CreateMessageDTO",
    "FeedbackDTO",
    "CreateFeedbackDTO",
    "TrainingPlanDTO",
    "PlanItemDTO",
    "CreatePlanDTO",
]
