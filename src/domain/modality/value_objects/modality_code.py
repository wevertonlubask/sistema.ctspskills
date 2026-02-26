"""ModalityCode value object."""

import re
from typing import Any

from src.shared.domain.value_object import ValueObject
from src.shared.exceptions import InvalidValueException


class ModalityCode(ValueObject):
    """Modality code value object.

    Represents a unique code for a modality following WorldSkills standards.
    Format: 2-4 uppercase letters optionally followed by 2-3 digits.
    Examples: WS17, IT, MECH01, AUTO
    """

    PATTERN = re.compile(r"^[A-Z]{2,4}(\d{2,3})?$")

    def __init__(self, value: str) -> None:
        normalized = value.strip().upper()

        if not normalized:
            raise InvalidValueException(
                field="modality_code",
                value=value,
                reason="Modality code cannot be empty",
            )

        if len(normalized) < 2 or len(normalized) > 7:
            raise InvalidValueException(
                field="modality_code",
                value=value,
                reason="Modality code must be between 2 and 7 characters",
            )

        if not self.PATTERN.match(normalized):
            raise InvalidValueException(
                field="modality_code",
                value=value,
                reason="Modality code must be 2-4 uppercase letters optionally followed by 2-3 digits (e.g., WS17, IT, MECH01)",
            )

        self._value = normalized

    @property
    def value(self) -> str:
        """Get the code value."""
        return self._value

    def _get_equality_components(self) -> tuple[Any, ...]:
        return (self._value,)

    def __str__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"ModalityCode({self._value!r})"
