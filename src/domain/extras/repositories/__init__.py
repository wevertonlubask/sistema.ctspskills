"""Extra features repository interfaces."""

from src.domain.extras.repositories.badge_repository import AchievementRepository, BadgeRepository
from src.domain.extras.repositories.event_repository import EventRepository, ScheduleRepository
from src.domain.extras.repositories.feedback_repository import FeedbackRepository
from src.domain.extras.repositories.goal_repository import GoalRepository
from src.domain.extras.repositories.message_repository import (
    ConversationRepository,
    MessageRepository,
)
from src.domain.extras.repositories.notification_repository import NotificationRepository
from src.domain.extras.repositories.resource_repository import ResourceRepository
from src.domain.extras.repositories.training_plan_repository import TrainingPlanRepository

__all__ = [
    "NotificationRepository",
    "EventRepository",
    "ScheduleRepository",
    "ResourceRepository",
    "GoalRepository",
    "BadgeRepository",
    "AchievementRepository",
    "ConversationRepository",
    "MessageRepository",
    "FeedbackRepository",
    "TrainingPlanRepository",
]
