"""Base Entity class for domain entities."""

from abc import ABC
from datetime import datetime
from typing import Any, Generic, TypeVar
from uuid import UUID, uuid4

from src.shared.utils.date_utils import utc_now

IdType = TypeVar("IdType", bound=UUID | int | str)


class Entity(ABC, Generic[IdType]):
    """Base class for all domain entities.

    Entities are objects that have a distinct identity that runs through time
    and different representations. They are defined by their identity,
    not by their attributes.
    """

    def __init__(
        self,
        id: IdType | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self._id: IdType = id if id is not None else uuid4()  # type: ignore
        self._created_at = created_at or utc_now()
        self._updated_at = updated_at or utc_now()

    @property
    def id(self) -> IdType:
        """Get entity ID."""
        return self._id

    @property
    def created_at(self) -> datetime:
        """Get creation timestamp."""
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        """Get last update timestamp."""
        return self._updated_at

    def _touch(self) -> None:
        """Update the updated_at timestamp."""
        self._updated_at = utc_now()

    def __eq__(self, other: Any) -> bool:
        """Check equality based on entity ID."""
        if not isinstance(other, Entity):
            return False
        return self._id == other._id  # type: ignore[no-any-return]

    def __hash__(self) -> int:
        """Hash based on entity ID."""
        return hash(self._id)

    def __repr__(self) -> str:
        """String representation of entity."""
        return f"{self.__class__.__name__}(id={self._id})"
