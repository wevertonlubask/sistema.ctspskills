"""Notification use cases."""

from uuid import UUID

from src.application.extras.dtos.notification_dto import (
    CreateNotificationDTO,
    NotificationDTO,
    NotificationListDTO,
)
from src.domain.extras.entities.notification import Notification
from src.domain.extras.exceptions import NotificationNotFoundException
from src.domain.extras.repositories.notification_repository import NotificationRepository
from src.shared.constants.enums import NotificationStatus, NotificationType


class SendNotificationUseCase:
    """Use case for sending notifications."""

    def __init__(self, notification_repository: NotificationRepository) -> None:
        self._notification_repository = notification_repository

    async def execute(self, dto: CreateNotificationDTO) -> NotificationDTO:
        """Send a notification.

        Args:
            dto: Notification data.

        Returns:
            Created notification DTO.
        """
        notification = Notification(
            user_id=dto.user_id,
            title=dto.title,
            message=dto.message,
            notification_type=dto.notification_type,
            channel=dto.channel,
            related_entity_type=dto.related_entity_type,
            related_entity_id=dto.related_entity_id,
            action_url=dto.action_url,
        )

        # Mark as sent for in-app notifications
        notification.mark_as_sent()

        saved = await self._notification_repository.save(notification)
        return NotificationDTO.from_entity(saved)

    async def send_info(
        self,
        user_id: UUID,
        title: str,
        message: str,
        action_url: str | None = None,
    ) -> NotificationDTO:
        """Send an info notification."""
        dto = CreateNotificationDTO(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=NotificationType.INFO,
            action_url=action_url,
        )
        return await self.execute(dto)

    async def send_warning(
        self,
        user_id: UUID,
        title: str,
        message: str,
        action_url: str | None = None,
    ) -> NotificationDTO:
        """Send a warning notification."""
        dto = CreateNotificationDTO(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=NotificationType.WARNING,
            action_url=action_url,
        )
        return await self.execute(dto)

    async def send_alert(
        self,
        user_id: UUID,
        title: str,
        message: str,
        action_url: str | None = None,
    ) -> NotificationDTO:
        """Send an alert notification."""
        dto = CreateNotificationDTO(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=NotificationType.ALERT,
            action_url=action_url,
        )
        return await self.execute(dto)


class ListNotificationsUseCase:
    """Use case for listing notifications."""

    def __init__(self, notification_repository: NotificationRepository) -> None:
        self._notification_repository = notification_repository

    async def execute(
        self,
        user_id: UUID,
        status: NotificationStatus | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> NotificationListDTO:
        """List notifications for a user.

        Args:
            user_id: User UUID.
            status: Optional status filter.
            skip: Number of items to skip.
            limit: Maximum items to return.

        Returns:
            Notification list DTO.
        """
        notifications = await self._notification_repository.get_by_user(
            user_id=user_id,
            status=status,
            skip=skip,
            limit=limit,
        )

        unread_count = await self._notification_repository.count_unread(user_id)

        return NotificationListDTO(
            notifications=[NotificationDTO.from_entity(n) for n in notifications],
            total=len(notifications),
            unread_count=unread_count,
        )


class MarkNotificationReadUseCase:
    """Use case for marking notifications as read."""

    def __init__(self, notification_repository: NotificationRepository) -> None:
        self._notification_repository = notification_repository

    async def execute(self, notification_id: UUID) -> bool:
        """Mark a notification as read.

        Args:
            notification_id: Notification UUID.

        Returns:
            True if successful.

        Raises:
            NotificationNotFoundException: If notification not found.
        """
        notification = await self._notification_repository.get_by_id(notification_id)
        if not notification:
            raise NotificationNotFoundException(str(notification_id))

        return await self._notification_repository.mark_as_read(notification_id)

    async def mark_all_read(self, user_id: UUID) -> int:
        """Mark all notifications as read for a user.

        Args:
            user_id: User UUID.

        Returns:
            Number of notifications marked as read.
        """
        return await self._notification_repository.mark_all_as_read(user_id)
