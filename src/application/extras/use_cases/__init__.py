"""Extra features use cases."""

from src.application.extras.use_cases.badge_use_cases import (
    AwardBadgeUseCase,
    GetLeaderboardUseCase,
    ListBadgesUseCase,
)
from src.application.extras.use_cases.event_use_cases import (
    CreateEventUseCase,
    ListEventsUseCase,
    UpdateEventUseCase,
)
from src.application.extras.use_cases.feedback_use_cases import (
    CreateFeedbackUseCase,
    ListFeedbackUseCase,
)
from src.application.extras.use_cases.goal_use_cases import (
    CheckGoalAlertsUseCase,
    CreateGoalUseCase,
    ListGoalsUseCase,
    UpdateGoalProgressUseCase,
)
from src.application.extras.use_cases.message_use_cases import (
    ListConversationsUseCase,
    ListMessagesUseCase,
    SendMessageUseCase,
)
from src.application.extras.use_cases.notification_use_cases import (
    ListNotificationsUseCase,
    MarkNotificationReadUseCase,
    SendNotificationUseCase,
)
from src.application.extras.use_cases.resource_use_cases import (
    CreateResourceUseCase,
    GetResourceUseCase,
    ListResourcesUseCase,
)
from src.application.extras.use_cases.training_plan_use_cases import (
    CreateTrainingPlanUseCase,
    ListTrainingPlansUseCase,
    UpdatePlanProgressUseCase,
)

__all__ = [
    "SendNotificationUseCase",
    "ListNotificationsUseCase",
    "MarkNotificationReadUseCase",
    "CreateEventUseCase",
    "ListEventsUseCase",
    "UpdateEventUseCase",
    "CreateResourceUseCase",
    "ListResourcesUseCase",
    "GetResourceUseCase",
    "CreateGoalUseCase",
    "ListGoalsUseCase",
    "UpdateGoalProgressUseCase",
    "CheckGoalAlertsUseCase",
    "AwardBadgeUseCase",
    "ListBadgesUseCase",
    "GetLeaderboardUseCase",
    "SendMessageUseCase",
    "ListConversationsUseCase",
    "ListMessagesUseCase",
    "CreateFeedbackUseCase",
    "ListFeedbackUseCase",
    "CreateTrainingPlanUseCase",
    "ListTrainingPlansUseCase",
    "UpdatePlanProgressUseCase",
]
