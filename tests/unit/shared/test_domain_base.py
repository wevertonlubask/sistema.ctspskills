"""Unit tests for shared domain base classes."""

from datetime import datetime
from typing import Any

from src.shared.domain.aggregate_root import AggregateRoot, DomainEvent
from src.shared.domain.entity import Entity
from src.shared.domain.value_object import ValueObject


class SampleValueObject(ValueObject):
    """Sample value object for testing."""

    def __init__(self, value: str) -> None:
        self._value = value

    @property
    def value(self) -> str:
        return self._value

    def _get_equality_components(self) -> tuple[Any, ...]:
        return (self._value,)


class SampleEntity(Entity[str]):
    """Sample entity for testing."""

    def __init__(self, id: str, name: str) -> None:
        super().__init__(id=id)
        self._name = name

    @property
    def name(self) -> str:
        return self._name


class SampleDomainEvent(DomainEvent):
    """Sample domain event for testing."""

    def __init__(self, event_type: str) -> None:
        self.event_type = event_type


class SampleAggregateRoot(AggregateRoot[str]):
    """Sample aggregate root for testing."""

    def __init__(self, id: str, name: str) -> None:
        super().__init__(id=id)
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def update_name(self, name: str) -> None:
        self._name = name
        self._touch()


class TestValueObject:
    """Tests for ValueObject base class."""

    def test_equality(self):
        """Test value object equality."""
        vo1 = SampleValueObject("test")
        vo2 = SampleValueObject("test")
        vo3 = SampleValueObject("other")

        assert vo1 == vo2
        assert vo1 != vo3

    def test_hash(self):
        """Test value object hashing."""
        vo1 = SampleValueObject("test")
        vo2 = SampleValueObject("test")

        assert hash(vo1) == hash(vo2)

    def test_inequality_with_different_type(self):
        """Test inequality with different type."""
        vo = SampleValueObject("test")
        assert vo != "test"
        assert vo != 123


class TestEntity:
    """Tests for Entity base class."""

    def test_equality_by_id(self):
        """Test entity equality is based on ID."""
        e1 = SampleEntity("1", "name1")
        e2 = SampleEntity("1", "name2")
        e3 = SampleEntity("2", "name1")

        assert e1 == e2  # Same ID
        assert e1 != e3  # Different ID

    def test_hash_by_id(self):
        """Test entity hashing is based on ID."""
        e1 = SampleEntity("1", "name1")
        e2 = SampleEntity("1", "name2")

        assert hash(e1) == hash(e2)

    def test_id_property(self):
        """Test entity ID property."""
        entity = SampleEntity("test-id", "Test")
        assert entity.id == "test-id"

    def test_created_at_timestamp(self):
        """Test entity has created_at timestamp."""
        entity = SampleEntity("1", "Test")
        assert entity.created_at is not None
        assert isinstance(entity.created_at, datetime)

    def test_updated_at_timestamp(self):
        """Test entity has updated_at timestamp."""
        entity = SampleEntity("1", "Test")
        assert entity.updated_at is not None
        assert isinstance(entity.updated_at, datetime)

    def test_inequality_with_different_type(self):
        """Test inequality with different type."""
        entity = SampleEntity("1", "Test")
        assert entity != "1"
        assert entity != 1

    def test_repr(self):
        """Test entity string representation."""
        entity = SampleEntity("test-id", "Test")
        assert "SampleEntity" in repr(entity)
        assert "test-id" in repr(entity)


class TestAggregateRoot:
    """Tests for AggregateRoot base class."""

    def test_domain_events_empty_initially(self):
        """Test domain events list is empty initially."""
        agg = SampleAggregateRoot("1", "Test")
        assert agg.domain_events == []

    def test_add_domain_event(self):
        """Test adding domain event."""
        agg = SampleAggregateRoot("1", "Test")
        event = SampleDomainEvent("TestEvent")
        agg.add_domain_event(event)

        assert len(agg.domain_events) == 1
        assert agg.domain_events[0] == event

    def test_clear_domain_events(self):
        """Test clearing domain events."""
        agg = SampleAggregateRoot("1", "Test")
        agg.add_domain_event(SampleDomainEvent("TestEvent"))
        agg.add_domain_event(SampleDomainEvent("AnotherEvent"))

        assert len(agg.domain_events) == 2
        agg.clear_domain_events()
        assert len(agg.domain_events) == 0

    def test_pop_domain_events(self):
        """Test popping domain events returns and clears them."""
        agg = SampleAggregateRoot("1", "Test")
        event1 = SampleDomainEvent("Event1")
        event2 = SampleDomainEvent("Event2")
        agg.add_domain_event(event1)
        agg.add_domain_event(event2)

        events = agg.pop_domain_events()

        assert len(events) == 2
        assert events[0] == event1
        assert events[1] == event2
        assert agg.domain_events == []

    def test_domain_events_is_copy(self):
        """Test domain_events returns a copy, not the original list."""
        agg = SampleAggregateRoot("1", "Test")
        event = SampleDomainEvent("TestEvent")
        agg.add_domain_event(event)

        events = agg.domain_events
        events.clear()

        # Original list should still have the event
        assert len(agg.domain_events) == 1


class TestDomainEvent:
    """Tests for DomainEvent base class."""

    def test_domain_event_instantiation(self):
        """Test domain event can be instantiated."""
        event = DomainEvent()
        assert event is not None

    def test_sample_domain_event(self):
        """Test sample domain event."""
        event = SampleDomainEvent("test_type")
        assert event.event_type == "test_type"
