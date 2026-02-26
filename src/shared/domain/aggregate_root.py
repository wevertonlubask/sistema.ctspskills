"""Base Aggregate Root class."""

from typing import Any, TypeVar
from uuid import UUID

from src.shared.domain.entity import Entity

IdType = TypeVar("IdType", bound=UUID | int | str)


class DomainEvent:
    """Base class for domain events."""

    pass


class AggregateRoot(Entity[IdType]):
    """Base class for aggregate roots.

    An aggregate root is an entity that serves as the entry point to an aggregate.
    It ensures the consistency of changes being made within the aggregate
    by forbidding external objects from holding references to its members.

    Aggregate roots can raise domain events to communicate changes to other
    parts of the system.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._domain_events: list[DomainEvent] = []

    @property
    def domain_events(self) -> list[DomainEvent]:
        """Get list of pending domain events."""
        return self._domain_events.copy()

    def add_domain_event(self, event: DomainEvent) -> None:
        """Add a domain event to be dispatched."""
        self._domain_events.append(event)

    def clear_domain_events(self) -> None:
        """Clear all pending domain events."""
        self._domain_events.clear()

    def pop_domain_events(self) -> list[DomainEvent]:
        """Get and clear all pending domain events."""
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events
