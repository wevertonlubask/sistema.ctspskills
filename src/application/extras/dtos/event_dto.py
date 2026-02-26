"""Event DTOs."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.domain.extras.entities.event import Event
from src.shared.constants.enums import EventType


@dataclass
class CreateEventDTO:
    """DTO for creating an event."""

    title: str
    start_datetime: datetime
    end_datetime: datetime
    event_type: EventType = EventType.OTHER
    description: str | None = None
    location: str | None = None
    modality_id: UUID | None = None
    is_all_day: bool = False
    recurrence_rule: str | None = None
    reminder_minutes: int | None = 30
    participant_ids: list[UUID] | None = None


@dataclass
class UpdateEventDTO:
    """DTO for updating an event."""

    title: str | None = None
    description: str | None = None
    start_datetime: datetime | None = None
    end_datetime: datetime | None = None
    location: str | None = None
    event_type: EventType | None = None


@dataclass
class EventDTO:
    """DTO for event responses."""

    id: UUID
    title: str
    description: str | None
    event_type: str
    start_datetime: datetime
    end_datetime: datetime
    location: str | None
    modality_id: UUID | None
    is_all_day: bool
    status: str
    recurrence_rule: str | None
    reminder_minutes: int | None
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    participants: list[UUID]
    duration_minutes: int

    @classmethod
    def from_entity(cls, entity: Event) -> "EventDTO":
        return cls(
            id=entity.id,
            title=entity.title,
            description=entity.description,
            event_type=entity.event_type.value,
            start_datetime=entity.start_datetime,
            end_datetime=entity.end_datetime,
            location=entity.location,
            modality_id=entity.modality_id,
            is_all_day=entity.is_all_day,
            status=entity.status.value,
            recurrence_rule=entity.recurrence_rule,
            reminder_minutes=entity.reminder_minutes,
            created_by=entity.created_by,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            participants=entity.participants,
            duration_minutes=entity.duration_minutes,
        )


@dataclass
class EventListDTO:
    """DTO for event list."""

    events: list[EventDTO]
    total: int
