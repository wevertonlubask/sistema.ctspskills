"""Date range value object for analytics queries."""

from dataclasses import dataclass
from datetime import date, timedelta

from src.shared.domain.value_object import ValueObject
from src.shared.exceptions import InvalidValueException


@dataclass(frozen=True)
class DateRange(ValueObject):
    """Date range value object for filtering analytics data.

    Provides common date range presets and validation.
    """

    start_date: date
    end_date: date

    def __post_init__(self) -> None:
        """Validate date range."""
        if self.start_date > self.end_date:
            raise InvalidValueException(
                field="date_range",
                value=f"{self.start_date} - {self.end_date}",
                reason="Start date must be before or equal to end date",
            )

    @property
    def days(self) -> int:
        """Get number of days in range."""
        return (self.end_date - self.start_date).days + 1

    @classmethod
    def last_7_days(cls) -> "DateRange":
        """Create range for last 7 days."""
        today = date.today()
        return cls(start_date=today - timedelta(days=6), end_date=today)

    @classmethod
    def last_30_days(cls) -> "DateRange":
        """Create range for last 30 days."""
        today = date.today()
        return cls(start_date=today - timedelta(days=29), end_date=today)

    @classmethod
    def last_90_days(cls) -> "DateRange":
        """Create range for last 90 days."""
        today = date.today()
        return cls(start_date=today - timedelta(days=89), end_date=today)

    @classmethod
    def last_365_days(cls) -> "DateRange":
        """Create range for last year."""
        today = date.today()
        return cls(start_date=today - timedelta(days=364), end_date=today)

    @classmethod
    def current_month(cls) -> "DateRange":
        """Create range for current month."""
        today = date.today()
        start = today.replace(day=1)
        return cls(start_date=start, end_date=today)

    @classmethod
    def current_year(cls) -> "DateRange":
        """Create range for current year."""
        today = date.today()
        start = today.replace(month=1, day=1)
        return cls(start_date=start, end_date=today)

    @classmethod
    def all_time(cls) -> "DateRange":
        """Create range from beginning of time to now."""
        return cls(start_date=date(2020, 1, 1), end_date=date.today())

    def _get_equality_components(self) -> tuple:
        """Get components for equality comparison."""
        return (self.start_date, self.end_date)

    def contains(self, d: date) -> bool:
        """Check if date is within range."""
        return self.start_date <= d <= self.end_date

    def __str__(self) -> str:
        return f"{self.start_date} to {self.end_date}"
