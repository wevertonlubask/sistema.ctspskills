"""TrainingHours value object."""

from src.shared.domain.value_object import ValueObject
from src.shared.exceptions import InvalidValueException


class TrainingHours(ValueObject):
    """Value object representing training hours.

    Business Rules:
    - RN04: Maximum 12 hours per day
    - Minimum is 0.5 hours (30 minutes)
    """

    MIN_HOURS = 0.5
    MAX_HOURS_PER_DAY = 12.0

    def __init__(self, value: float) -> None:
        """Initialize training hours.

        Args:
            value: Number of training hours.

        Raises:
            InvalidValueException: If hours are invalid.
        """
        self._validate(value)
        self._value = round(value, 2)

    def _validate(self, value: float) -> None:
        """Validate training hours."""
        if value < self.MIN_HOURS:
            raise InvalidValueException(
                field="hours",
                value=value,
                reason=f"Training hours must be at least {self.MIN_HOURS} hours",
            )
        if value > self.MAX_HOURS_PER_DAY:
            raise InvalidValueException(
                field="hours",
                value=value,
                reason=f"Training hours cannot exceed {self.MAX_HOURS_PER_DAY} hours per day (RN04)",
            )

    @property
    def value(self) -> float:
        """Get hours value."""
        return self._value

    def _get_equality_components(self) -> tuple:
        """Get the components used for equality comparison."""
        return (self._value,)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TrainingHours):
            return False
        return self._value == other._value

    def __hash__(self) -> int:
        return hash(self._value)

    def __repr__(self) -> str:
        return f"TrainingHours({self._value})"

    def __float__(self) -> float:
        return self._value

    def __add__(self, other: "TrainingHours") -> "TrainingHours":
        """Add two training hours (for totals, bypasses max validation)."""
        total = self._value + other._value
        # For totals, we create without validation
        hours = object.__new__(TrainingHours)
        hours._value = round(total, 2)
        return hours

    @classmethod
    def create_total(cls, value: float) -> "TrainingHours":
        """Create training hours for totals (bypasses daily max validation).

        Use this only for aggregate totals, not individual sessions.
        """
        if value < 0:
            raise InvalidValueException(
                field="hours",
                value=value,
                reason="Total training hours cannot be negative",
            )
        hours = object.__new__(cls)
        hours._value = round(value, 2)
        return hours
