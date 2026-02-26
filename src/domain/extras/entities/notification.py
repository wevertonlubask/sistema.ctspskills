"""Notification entity."""

from datetime import datetime
from uuid import UUID, uuid4

from src.shared.constants.enums import (
    NotificationChannel,
    NotificationStatus,
    NotificationType,
)
from src.shared.domain.entity import Entity


class Notification(Entity[UUID]):
    """Notification entity for user communications."""

    def __init__(
        self,
        user_id: UUID,
        title: str,
        message: str,
        notification_type: NotificationType = NotificationType.INFO,
        channel: NotificationChannel = NotificationChannel.IN_APP,
        status: NotificationStatus = NotificationStatus.PENDING,
        id: UUID | None = None,
        related_entity_type: str | None = None,
        related_entity_id: UUID | None = None,
        action_url: str | None = None,
        read_at: datetime | None = None,
        sent_at: datetime | None = None,
        created_at: datetime | None = None,
    ) -> None:
        super().__init__(id=id or uuid4())
        self._user_id = user_id
        self._title = title
        self._message = message
        self._notification_type = notification_type
        self._channel = channel
        self._status = status
        self._related_entity_type = related_entity_type
        self._related_entity_id = related_entity_id
        self._action_url = action_url
        self._read_at = read_at
        self._sent_at = sent_at
        self._created_at = created_at or datetime.utcnow()

    @property
    def user_id(self) -> UUID:
        return self._user_id

    @property
    def title(self) -> str:
        return self._title

    @property
    def message(self) -> str:
        return self._message

    @property
    def notification_type(self) -> NotificationType:
        return self._notification_type

    @property
    def channel(self) -> NotificationChannel:
        return self._channel

    @property
    def status(self) -> NotificationStatus:
        return self._status

    @property
    def related_entity_type(self) -> str | None:
        return self._related_entity_type

    @property
    def related_entity_id(self) -> UUID | None:
        return self._related_entity_id

    @property
    def action_url(self) -> str | None:
        return self._action_url

    @property
    def read_at(self) -> datetime | None:
        return self._read_at

    @property
    def sent_at(self) -> datetime | None:
        return self._sent_at

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def is_read(self) -> bool:
        return self._read_at is not None

    def mark_as_sent(self) -> None:
        """Mark notification as sent."""
        self._status = NotificationStatus.SENT
        self._sent_at = datetime.utcnow()

    def mark_as_read(self) -> None:
        """Mark notification as read."""
        self._status = NotificationStatus.READ
        self._read_at = datetime.utcnow()

    def mark_as_failed(self) -> None:
        """Mark notification as failed."""
        self._status = NotificationStatus.FAILED

    @classmethod
    def create_info(
        cls,
        user_id: UUID,
        title: str,
        message: str,
        channel: NotificationChannel = NotificationChannel.IN_APP,
    ) -> "Notification":
        """Create an info notification."""
        return cls(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=NotificationType.INFO,
            channel=channel,
        )

    @classmethod
    def create_warning(
        cls,
        user_id: UUID,
        title: str,
        message: str,
        channel: NotificationChannel = NotificationChannel.IN_APP,
    ) -> "Notification":
        """Create a warning notification."""
        return cls(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=NotificationType.WARNING,
            channel=channel,
        )

    @classmethod
    def create_alert(
        cls,
        user_id: UUID,
        title: str,
        message: str,
        channel: NotificationChannel = NotificationChannel.IN_APP,
    ) -> "Notification":
        """Create an alert notification."""
        return cls(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=NotificationType.ALERT,
            channel=channel,
        )
