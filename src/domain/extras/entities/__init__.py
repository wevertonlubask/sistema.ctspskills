"""Extra features entities."""

from src.domain.extras.entities.badge import Achievement, Badge
from src.domain.extras.entities.event import Event, Schedule
from src.domain.extras.entities.feedback import Feedback
from src.domain.extras.entities.goal import Goal, Milestone
from src.domain.extras.entities.message import Conversation, Message
from src.domain.extras.entities.notification import Notification
from src.domain.extras.entities.resource import Resource
from src.domain.extras.entities.training_plan import PlanItem, TrainingPlan

__all__ = [
    "Notification",
    "Event",
    "Schedule",
    "Resource",
    "Goal",
    "Milestone",
    "Badge",
    "Achievement",
    "Message",
    "Conversation",
    "Feedback",
    "TrainingPlan",
    "PlanItem",
]
