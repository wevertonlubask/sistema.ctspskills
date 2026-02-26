"""UserId value object."""

from typing import Any
from uuid import UUID, uuid4

from src.shared.domain.value_object import ValueObject
from src.shared.exceptions import InvalidValueException


class UserId(ValueObject):
    """User identifier value object.

    Wraps a UUID to provide type safety and validation.
    """

    def __init__(self, value: UUID | str | None = None) -> None:
        if value is None:
            self._value = uuid4()
        elif isinstance(value, UUID):
            self._value = value
        elif isinstance(value, str):
            try:
                self._value = UUID(value)
            except ValueError as e:
                raise InvalidValueException(
                    field="user_id",
                    value=value,
                    reason=f"Invalid UUID format: {e}",
                ) from e
        else:
            raise InvalidValueException(
                field="user_id",
                value=value,
                reason=f"Expected UUID or string, got {type(value).__name__}",
            )

    @property
    def value(self) -> UUID:
        """Get the UUID value."""
        return self._value

    def _get_equality_components(self) -> tuple[Any, ...]:
        return (self._value,)

    def __str__(self) -> str:
        return str(self._value)

    def __repr__(self) -> str:
        return f"UserId({self._value})"
