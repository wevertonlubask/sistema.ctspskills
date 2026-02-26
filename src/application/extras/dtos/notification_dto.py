"""Notification DTOs."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.domain.extras.entities.notification import Notification
from src.shared.constants.enums import NotificationChannel, NotificationType


@dataclass
class CreateNotificationDTO:
    """DTO for creating a notification."""

    user_id: UUID
    title: str
    message: str
    notification_type: NotificationType = NotificationType.INFO
    channel: NotificationChannel = NotificationChannel.IN_APP
    related_entity_type: str | None = None
    related_entity_id: UUID | None = None
    action_url: str | None = None


@dataclass
class NotificationDTO:
    """DTO for notification responses."""

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

    @classmethod
    def from_entity(cls, entity: Notification) -> "NotificationDTO":
        return cls(
            id=entity.id,
            user_id=entity.user_id,
            title=entity.title,
            message=entity.message,
            notification_type=entity.notification_type.value,
            channel=entity.channel.value,
            status=entity.status.value,
            related_entity_type=entity.related_entity_type,
            related_entity_id=entity.related_entity_id,
            action_url=entity.action_url,
            is_read=entity.is_read,
            read_at=entity.read_at,
            sent_at=entity.sent_at,
            created_at=entity.created_at,
        )


@dataclass
class NotificationListDTO:
    """DTO for notification list."""

    notifications: list[NotificationDTO]
    total: int
    unread_count: int
