"""Date and time utility functions."""

from datetime import UTC, datetime

import pytz
from dateutil import parser as date_parser


def utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(UTC)


def to_utc(dt: datetime) -> datetime:
    """Convert datetime to UTC timezone."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def format_datetime(dt: datetime, fmt: str = "%Y-%m-%dT%H:%M:%SZ") -> str:
    """Format datetime to string."""
    return dt.strftime(fmt)


def parse_datetime(dt_string: str) -> datetime:
    """Parse string to datetime."""
    return date_parser.parse(dt_string)


def to_timezone(dt: datetime, tz_name: str = "America/Sao_Paulo") -> datetime:
    """Convert datetime to specified timezone."""
    tz = pytz.timezone(tz_name)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(tz)


def get_date_range(
    start_date: datetime,
    end_date: datetime,
) -> tuple[datetime, datetime]:
    """Ensure start and end dates are properly ordered and in UTC."""
    start = to_utc(start_date)
    end = to_utc(end_date)
    if start > end:
        start, end = end, start
    return start, end


def is_expired(expiry_date: datetime) -> bool:
    """Check if a datetime has expired."""
    return utc_now() > to_utc(expiry_date)


def add_days(dt: datetime, days: int) -> datetime:
    """Add days to a datetime."""
    from datetime import timedelta

    return dt + timedelta(days=days)


def add_minutes(dt: datetime, minutes: int) -> datetime:
    """Add minutes to a datetime."""
    from datetime import timedelta

    return dt + timedelta(minutes=minutes)
