"""Extra features domain exceptions."""

from src.shared.exceptions import DomainException
from src.shared.exceptions.base import ErrorCode


class NotificationNotFoundException(DomainException):
    """Notification not found exception."""

    def __init__(self, notification_id: str) -> None:
        super().__init__(
            f"Notification with ID {notification_id} not found",
            code=ErrorCode.ENTITY_NOT_FOUND,
        )


class EventNotFoundException(DomainException):
    """Event not found exception."""

    def __init__(self, event_id: str) -> None:
        super().__init__(
            f"Event with ID {event_id} not found",
            code=ErrorCode.ENTITY_NOT_FOUND,
        )


class ScheduleNotFoundException(DomainException):
    """Schedule not found exception."""

    def __init__(self, schedule_id: str) -> None:
        super().__init__(
            f"Schedule with ID {schedule_id} not found",
            code=ErrorCode.ENTITY_NOT_FOUND,
        )


class ResourceNotFoundException(DomainException):
    """Resource not found exception."""

    def __init__(self, resource_id: str) -> None:
        super().__init__(
            f"Resource with ID {resource_id} not found",
            code=ErrorCode.RESOURCE_NOT_FOUND,
        )


class ResourceAccessDeniedException(DomainException):
    """Resource access denied exception."""

    def __init__(self, resource_id: str) -> None:
        super().__init__(
            f"Access denied to resource {resource_id}",
            code=ErrorCode.PERMISSION_DENIED,
        )


class GoalNotFoundException(DomainException):
    """Goal not found exception."""

    def __init__(self, goal_id: str) -> None:
        super().__init__(
            f"Goal with ID {goal_id} not found",
            code=ErrorCode.ENTITY_NOT_FOUND,
        )


class MilestoneNotFoundException(DomainException):
    """Milestone not found exception."""

    def __init__(self, milestone_id: str) -> None:
        super().__init__(
            f"Milestone with ID {milestone_id} not found",
            code=ErrorCode.ENTITY_NOT_FOUND,
        )


class BadgeNotFoundException(DomainException):
    """Badge not found exception."""

    def __init__(self, badge_id: str) -> None:
        super().__init__(
            f"Badge with ID {badge_id} not found",
            code=ErrorCode.ENTITY_NOT_FOUND,
        )


class AchievementNotFoundException(DomainException):
    """Achievement not found exception."""

    def __init__(self, achievement_id: str) -> None:
        super().__init__(
            f"Achievement with ID {achievement_id} not found",
            code=ErrorCode.ENTITY_NOT_FOUND,
        )


class BadgeAlreadyEarnedException(DomainException):
    """Badge already earned exception."""

    def __init__(self, badge_id: str, user_id: str) -> None:
        super().__init__(
            f"User {user_id} already earned badge {badge_id}",
            code=ErrorCode.RESOURCE_CONFLICT,
        )


class ConversationNotFoundException(DomainException):
    """Conversation not found exception."""

    def __init__(self, conversation_id: str) -> None:
        super().__init__(
            f"Conversation with ID {conversation_id} not found",
            code=ErrorCode.ENTITY_NOT_FOUND,
        )


class MessageNotFoundException(DomainException):
    """Message not found exception."""

    def __init__(self, message_id: str) -> None:
        super().__init__(
            f"Message with ID {message_id} not found",
            code=ErrorCode.ENTITY_NOT_FOUND,
        )


class NotConversationParticipantException(DomainException):
    """User is not a conversation participant exception."""

    def __init__(self, user_id: str, conversation_id: str) -> None:
        super().__init__(
            f"User {user_id} is not a participant in conversation {conversation_id}",
            code=ErrorCode.PERMISSION_DENIED,
        )


class FeedbackNotFoundException(DomainException):
    """Feedback not found exception."""

    def __init__(self, feedback_id: str) -> None:
        super().__init__(
            f"Feedback with ID {feedback_id} not found",
            code=ErrorCode.ENTITY_NOT_FOUND,
        )


class TrainingPlanNotFoundException(DomainException):
    """Training plan not found exception."""

    def __init__(self, plan_id: str) -> None:
        super().__init__(
            f"Training plan with ID {plan_id} not found",
            code=ErrorCode.ENTITY_NOT_FOUND,
        )


class PlanItemNotFoundException(DomainException):
    """Plan item not found exception."""

    def __init__(self, item_id: str) -> None:
        super().__init__(
            f"Plan item with ID {item_id} not found",
            code=ErrorCode.ENTITY_NOT_FOUND,
        )


class InvalidDateRangeException(DomainException):
    """Invalid date range exception."""

    def __init__(self, message: str = "End date must be after start date") -> None:
        super().__init__(message, code=ErrorCode.INVALID_VALUE)


class EventOverlapException(DomainException):
    """Event overlap exception."""

    def __init__(self, event_id: str) -> None:
        super().__init__(
            f"Event overlaps with existing event {event_id}",
            code=ErrorCode.BUSINESS_RULE_VIOLATION,
        )
