"""Email value object."""

from typing import Any

from src.shared.domain.value_object import ValueObject
from src.shared.exceptions import InvalidValueException
from src.shared.utils.validators import validate_email


class Email(ValueObject):
    """Email value object with validation.

    Ensures email format is valid and normalizes the value.
    """

    def __init__(self, value: str) -> None:
        normalized = value.strip().lower()

        if not normalized:
            raise InvalidValueException(
                field="email",
                value=value,
                reason="Email cannot be empty",
            )

        if not validate_email(normalized):
            raise InvalidValueException(
                field="email",
                value=value,
                reason="Invalid email format",
            )

        self._value = normalized

    @property
    def value(self) -> str:
        """Get email value."""
        return self._value

    @property
    def domain(self) -> str:
        """Get email domain."""
        return self._value.split("@")[1]

    @property
    def local_part(self) -> str:
        """Get local part of email (before @)."""
        return self._value.split("@")[0]

    def _get_equality_components(self) -> tuple[Any, ...]:
        return (self._value,)

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"Email({self._value!r})"
