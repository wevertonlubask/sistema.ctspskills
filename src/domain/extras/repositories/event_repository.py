"""Event and Schedule repository interfaces."""

from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from src.domain.extras.entities.event import Event, Schedule
from src.shared.constants.enums import EventStatus


class EventRepository(ABC):
    """Abstract repository for events."""

    @abstractmethod
    async def save(self, event: Event) -> Event:
        """Save an event."""
        ...

    @abstractmethod
    async def get_by_id(self, event_id: UUID) -> Event | None:
        """Get event by ID."""
        ...

    @abstractmethod
    async def get_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        modality_id: UUID | None = None,
        user_id: UUID | None = None,
    ) -> list[Event]:
        """Get events in a date range."""
        ...

    @abstractmethod
    async def get_upcoming(
        self,
        user_id: UUID | None = None,
        modality_id: UUID | None = None,
        limit: int = 10,
    ) -> list[Event]:
        """Get upcoming events."""
        ...

    @abstractmethod
    async def get_by_participant(
        self,
        user_id: UUID,
        status: EventStatus | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Event]:
        """Get events where user is a participant."""
        ...

    @abstractmethod
    async def get_needing_reminder(self) -> list[Event]:
        """Get events that need reminders sent."""
        ...

    @abstractmethod
    async def update(self, event: Event) -> Event:
        """Update an event."""
        ...

    @abstractmethod
    async def delete(self, event_id: UUID) -> bool:
        """Delete an event."""
        ...

    @abstractmethod
    async def add_participant(self, event_id: UUID, user_id: UUID) -> bool:
        """Add participant to event."""
        ...

    @abstractmethod
    async def remove_participant(self, event_id: UUID, user_id: UUID) -> bool:
        """Remove participant from event."""
        ...


class ScheduleRepository(ABC):
    """Abstract repository for schedules."""

    @abstractmethod
    async def save(self, schedule: Schedule) -> Schedule:
        """Save a schedule."""
        ...

    @abstractmethod
    async def get_by_id(self, schedule_id: UUID) -> Schedule | None:
        """Get schedule by ID."""
        ...

    @abstractmethod
    async def get_by_user(
        self,
        user_id: UUID,
        is_active: bool | None = None,
    ) -> list[Schedule]:
        """Get schedules for a user."""
        ...

    @abstractmethod
    async def get_by_day(
        self,
        day_of_week: int,
        user_id: UUID | None = None,
        modality_id: UUID | None = None,
    ) -> list[Schedule]:
        """Get schedules for a specific day."""
        ...

    @abstractmethod
    async def update(self, schedule: Schedule) -> Schedule:
        """Update a schedule."""
        ...

    @abstractmethod
    async def delete(self, schedule_id: UUID) -> bool:
        """Delete a schedule."""
        ...
