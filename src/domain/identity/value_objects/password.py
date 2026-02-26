"""Password value object."""

from typing import Any

from src.shared.domain.value_object import ValueObject
from src.shared.exceptions import InvalidValueException
from src.shared.utils.validators import validate_password_strength


class Password(ValueObject):
    """Password value object.

    Stores the hashed password and provides validation for raw passwords.
    This value object is created with an already hashed password.
    Use Password.create() for creating from a raw password.
    """

    def __init__(self, hashed_value: str) -> None:
        if not hashed_value:
            raise InvalidValueException(
                field="password",
                value="",
                reason="Password hash cannot be empty",
            )
        self._hashed_value = hashed_value

    @classmethod
    def validate_raw(cls, raw_password: str) -> None:
        """Validate raw password strength before hashing.

        Args:
            raw_password: The plain text password to validate.

        Raises:
            InvalidValueException: If password doesn't meet requirements.
        """
        result = validate_password_strength(raw_password)
        if not result.is_valid:
            raise InvalidValueException(
                field="password",
                value="[REDACTED]",
                reason=result.error_message,
            )

    @property
    def hashed_value(self) -> str:
        """Get the hashed password value."""
        return self._hashed_value

    def _get_equality_components(self) -> tuple[Any, ...]:
        return (self._hashed_value,)

    def __str__(self) -> str:
        return "[PROTECTED]"

    def __repr__(self) -> str:
        return "Password([PROTECTED])"
