"""Event and Schedule entities."""

from datetime import datetime, time
from uuid import UUID, uuid4

from src.shared.constants.enums import EventStatus, EventType
from src.shared.domain.aggregate_root import AggregateRoot
from src.shared.domain.entity import Entity


class Event(AggregateRoot[UUID]):
    """Event entity for scheduling."""

    def __init__(
        self,
        title: str,
        start_datetime: datetime,
        end_datetime: datetime,
        created_by: UUID,
        event_type: EventType = EventType.OTHER,
        description: str | None = None,
        location: str | None = None,
        modality_id: UUID | None = None,
        is_all_day: bool = False,
        status: EventStatus = EventStatus.SCHEDULED,
        recurrence_rule: str | None = None,
        reminder_minutes: int | None = 30,
        id: UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        super().__init__(id=id or uuid4())
        self._title = title
        self._description = description
        self._event_type = event_type
        self._start_datetime = start_datetime
        self._end_datetime = end_datetime
        self._location = location
        self._modality_id = modality_id
        self._is_all_day = is_all_day
        self._status = status
        self._recurrence_rule = recurrence_rule
        self._reminder_minutes = reminder_minutes
        self._created_by = created_by
        self._created_at = created_at or datetime.utcnow()
        self._updated_at = updated_at or datetime.utcnow()
        self._participants: list[UUID] = []

    @property
    def title(self) -> str:
        return self._title

    @property
    def description(self) -> str | None:
        return self._description

    @property
    def event_type(self) -> EventType:
        return self._event_type

    @property
    def start_datetime(self) -> datetime:
        return self._start_datetime

    @property
    def end_datetime(self) -> datetime:
        return self._end_datetime

    @property
    def location(self) -> str | None:
        return self._location

    @property
    def modality_id(self) -> UUID | None:
        return self._modality_id

    @property
    def is_all_day(self) -> bool:
        return self._is_all_day

    @property
    def status(self) -> EventStatus:
        return self._status

    @property
    def recurrence_rule(self) -> str | None:
        return self._recurrence_rule

    @property
    def reminder_minutes(self) -> int | None:
        return self._reminder_minutes

    @property
    def created_by(self) -> UUID:
        return self._created_by

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    @property
    def participants(self) -> list[UUID]:
        return self._participants.copy()

    @property
    def duration_minutes(self) -> int:
        """Get event duration in minutes."""
        delta = self._end_datetime - self._start_datetime
        return int(delta.total_seconds() / 60)

    def update(
        self,
        title: str | None = None,
        description: str | None = None,
        start_datetime: datetime | None = None,
        end_datetime: datetime | None = None,
        location: str | None = None,
        event_type: EventType | None = None,
    ) -> None:
        """Update event details."""
        if title is not None:
            self._title = title
        if description is not None:
            self._description = description
        if start_datetime is not None:
            self._start_datetime = start_datetime
        if end_datetime is not None:
            self._end_datetime = end_datetime
        if location is not None:
            self._location = location
        if event_type is not None:
            self._event_type = event_type
        self._updated_at = datetime.utcnow()

    def add_participant(self, user_id: UUID) -> bool:
        """Add a participant to the event."""
        if user_id not in self._participants:
            self._participants.append(user_id)
            return True
        return False

    def remove_participant(self, user_id: UUID) -> bool:
        """Remove a participant from the event."""
        if user_id in self._participants:
            self._participants.remove(user_id)
            return True
        return False

    def start(self) -> None:
        """Mark event as in progress."""
        self._status = EventStatus.IN_PROGRESS
        self._updated_at = datetime.utcnow()

    def complete(self) -> None:
        """Mark event as completed."""
        self._status = EventStatus.COMPLETED
        self._updated_at = datetime.utcnow()

    def cancel(self) -> None:
        """Cancel the event."""
        self._status = EventStatus.CANCELLED
        self._updated_at = datetime.utcnow()

    def is_upcoming(self) -> bool:
        """Check if event is upcoming."""
        return self._start_datetime > datetime.utcnow()

    def needs_reminder(self) -> bool:
        """Check if event needs a reminder sent."""
        if self._reminder_minutes is None:
            return False
        if self._status != EventStatus.SCHEDULED:
            return False
        reminder_time = self._start_datetime.timestamp() - (self._reminder_minutes * 60)
        return datetime.utcnow().timestamp() >= reminder_time


class Schedule(Entity[UUID]):
    """Schedule entity for recurring patterns."""

    def __init__(
        self,
        name: str,
        user_id: UUID,
        day_of_week: int,  # 0=Monday, 6=Sunday
        start_time: time,
        end_time: time,
        modality_id: UUID | None = None,
        is_active: bool = True,
        id: UUID | None = None,
    ) -> None:
        super().__init__(id=id or uuid4())
        self._name = name
        self._user_id = user_id
        self._day_of_week = day_of_week
        self._start_time = start_time
        self._end_time = end_time
        self._modality_id = modality_id
        self._is_active = is_active

    @property
    def name(self) -> str:
        return self._name

    @property
    def user_id(self) -> UUID:
        return self._user_id

    @property
    def day_of_week(self) -> int:
        return self._day_of_week

    @property
    def start_time(self) -> time:
        return self._start_time

    @property
    def end_time(self) -> time:
        return self._end_time

    @property
    def modality_id(self) -> UUID | None:
        return self._modality_id

    @property
    def is_active(self) -> bool:
        return self._is_active

    def deactivate(self) -> None:
        """Deactivate the schedule."""
        self._is_active = False

    def activate(self) -> None:
        """Activate the schedule."""
        self._is_active = True
