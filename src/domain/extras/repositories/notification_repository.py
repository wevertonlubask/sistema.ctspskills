"""Notification repository interface."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.extras.entities.notification import Notification
from src.shared.constants.enums import NotificationStatus, NotificationType


class NotificationRepository(ABC):
    """Abstract repository for notifications."""

    @abstractmethod
    async def save(self, notification: Notification) -> Notification:
        """Save a notification."""
        ...

    @abstractmethod
    async def get_by_id(self, notification_id: UUID) -> Notification | None:
        """Get notification by ID."""
        ...

    @abstractmethod
    async def get_by_user(
        self,
        user_id: UUID,
        status: NotificationStatus | None = None,
        notification_type: NotificationType | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Notification]:
        """Get notifications for a user."""
        ...

    @abstractmethod
    async def count_unread(self, user_id: UUID) -> int:
        """Count unread notifications for a user."""
        ...

    @abstractmethod
    async def mark_as_read(self, notification_id: UUID) -> bool:
        """Mark notification as read."""
        ...

    @abstractmethod
    async def mark_all_as_read(self, user_id: UUID) -> int:
        """Mark all notifications as read for a user. Returns count."""
        ...

    @abstractmethod
    async def delete(self, notification_id: UUID) -> bool:
        """Delete a notification."""
        ...

    @abstractmethod
    async def delete_old(self, days: int = 30) -> int:
        """Delete notifications older than specified days. Returns count."""
        ...
