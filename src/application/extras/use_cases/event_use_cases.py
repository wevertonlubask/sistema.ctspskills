"""Event use cases."""

from datetime import datetime
from uuid import UUID

from src.application.extras.dtos.event_dto import (
    CreateEventDTO,
    EventDTO,
    EventListDTO,
    UpdateEventDTO,
)
from src.domain.extras.entities.event import Event
from src.domain.extras.exceptions import EventNotFoundException
from src.domain.extras.repositories.event_repository import EventRepository


class CreateEventUseCase:
    """Use case for creating events."""

    def __init__(self, event_repository: EventRepository) -> None:
        self._event_repository = event_repository

    async def execute(
        self,
        creator_id: UUID,
        dto: CreateEventDTO,
    ) -> EventDTO:
        """Create an event.

        Args:
            creator_id: Creator user UUID.
            dto: Event data.

        Returns:
            Created event DTO.
        """
        event = Event(
            title=dto.title,
            start_datetime=dto.start_datetime,
            end_datetime=dto.end_datetime,
            event_type=dto.event_type,
            description=dto.description,
            location=dto.location,
            modality_id=dto.modality_id,
            is_all_day=dto.is_all_day,
            recurrence_rule=dto.recurrence_rule,
            reminder_minutes=dto.reminder_minutes,
            created_by=creator_id,
        )

        # Add participants
        if dto.participant_ids:
            for participant_id in dto.participant_ids:
                event.add_participant(participant_id)

        saved = await self._event_repository.save(event)
        return EventDTO.from_entity(saved)


class ListEventsUseCase:
    """Use case for listing events."""

    def __init__(self, event_repository: EventRepository) -> None:
        self._event_repository = event_repository

    async def execute(
        self,
        start_date: datetime,
        end_date: datetime,
        modality_id: UUID | None = None,
        user_id: UUID | None = None,
    ) -> EventListDTO:
        """List events in a date range.

        Args:
            start_date: Start datetime.
            end_date: End datetime.
            modality_id: Optional modality filter.
            user_id: Optional user filter.

        Returns:
            Event list DTO.
        """
        events = await self._event_repository.get_by_date_range(
            start_date=start_date,
            end_date=end_date,
            modality_id=modality_id,
            user_id=user_id,
        )

        return EventListDTO(
            events=[EventDTO.from_entity(e) for e in events],
            total=len(events),
        )

    async def get_upcoming(
        self,
        user_id: UUID | None = None,
        modality_id: UUID | None = None,
        limit: int = 10,
    ) -> EventListDTO:
        """Get upcoming events.

        Args:
            user_id: Optional user filter.
            modality_id: Optional modality filter.
            limit: Maximum events to return.

        Returns:
            Event list DTO.
        """
        events = await self._event_repository.get_upcoming(
            user_id=user_id,
            modality_id=modality_id,
            limit=limit,
        )

        return EventListDTO(
            events=[EventDTO.from_entity(e) for e in events],
            total=len(events),
        )


class UpdateEventUseCase:
    """Use case for updating events."""

    def __init__(self, event_repository: EventRepository) -> None:
        self._event_repository = event_repository

    async def execute(
        self,
        event_id: UUID,
        dto: UpdateEventDTO,
    ) -> EventDTO:
        """Update an event.

        Args:
            event_id: Event UUID.
            dto: Update data.

        Returns:
            Updated event DTO.

        Raises:
            EventNotFoundException: If event not found.
        """
        event = await self._event_repository.get_by_id(event_id)
        if not event:
            raise EventNotFoundException(str(event_id))

        event.update(
            title=dto.title,
            description=dto.description,
            start_datetime=dto.start_datetime,
            end_datetime=dto.end_datetime,
            location=dto.location,
            event_type=dto.event_type,
        )

        saved = await self._event_repository.update(event)
        return EventDTO.from_entity(saved)

    async def cancel(self, event_id: UUID) -> EventDTO:
        """Cancel an event.

        Args:
            event_id: Event UUID.

        Returns:
            Updated event DTO.
        """
        event = await self._event_repository.get_by_id(event_id)
        if not event:
            raise EventNotFoundException(str(event_id))

        event.cancel()
        saved = await self._event_repository.update(event)
        return EventDTO.from_entity(saved)

    async def add_participant(self, event_id: UUID, user_id: UUID) -> bool:
        """Add a participant to an event."""
        return await self._event_repository.add_participant(event_id, user_id)

    async def remove_participant(self, event_id: UUID, user_id: UUID) -> bool:
        """Remove a participant from an event."""
        return await self._event_repository.remove_participant(event_id, user_id)
