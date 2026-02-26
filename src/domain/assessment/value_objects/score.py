"""Score value object for assessment grades."""

from src.shared.domain.value_object import ValueObject
from src.shared.exceptions import InvalidValueException


class Score(ValueObject):
    """Score value object representing a grade (0-100 normalized scale).

    The score is stored as a percentage (0-100) and can be converted
    to an absolute value based on the competence's max_score.
    """

    MIN_SCORE = 0.0
    MAX_SCORE = 100.0

    def __init__(self, value: float) -> None:
        """Initialize Score value object.

        Args:
            value: Score value (0-100).

        Raises:
            InvalidValueException: If score is out of valid range.
        """
        self._validate(value)
        self._value = round(float(value), 2)

    def _validate(self, value: float) -> None:
        """Validate score value."""
        if value < self.MIN_SCORE:
            raise InvalidValueException(
                field="score",
                value=value,
                reason=f"Score must be at least {self.MIN_SCORE}",
            )
        if value > self.MAX_SCORE:
            raise InvalidValueException(
                field="score",
                value=value,
                reason=f"Score cannot exceed {self.MAX_SCORE}",
            )

    @property
    def value(self) -> float:
        """Get the score value."""
        return self._value

    def to_absolute(self, max_score: float) -> float:
        """Convert normalized score to absolute value.

        Args:
            max_score: Maximum score for the competence.

        Returns:
            Absolute score value.
        """
        return round((self._value / 100.0) * max_score, 2)

    @classmethod
    def from_absolute(cls, score: float, max_score: float) -> "Score":
        """Create Score from absolute value.

        Args:
            score: Absolute score value.
            max_score: Maximum score for the competence.

        Returns:
            Normalized Score instance.

        Raises:
            InvalidValueException: If max_score is zero or score is invalid.
        """
        if max_score <= 0:
            raise InvalidValueException(
                field="max_score",
                value=max_score,
                reason="max_score must be greater than 0",
            )
        normalized = (score / max_score) * 100.0
        return cls(normalized)

    def _get_equality_components(self) -> tuple:
        """Get the components used for equality comparison."""
        return (self._value,)

    def __str__(self) -> str:
        return f"{self._value}%"

    def __repr__(self) -> str:
        return f"Score(value={self._value})"

    def __add__(self, other: "Score") -> "Score":
        """Add two scores (for averaging calculations)."""
        if not isinstance(other, Score):
            return NotImplemented
        # Allow exceeding 100 for totals (will be validated on creation if needed)
        return Score(min(self._value + other._value, self.MAX_SCORE))

    def __lt__(self, other: "Score") -> bool:
        if not isinstance(other, Score):
            return NotImplemented
        return self._value < other._value

    def __le__(self, other: "Score") -> bool:
        if not isinstance(other, Score):
            return NotImplemented
        return self._value <= other._value
