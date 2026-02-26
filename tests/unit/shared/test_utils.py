"""Unit tests for shared utilities."""

from datetime import UTC, datetime

from src.shared.utils.date_utils import (
    add_days,
    add_minutes,
    format_datetime,
    get_date_range,
    is_expired,
    parse_datetime,
    to_timezone,
    to_utc,
    utc_now,
)
from src.shared.utils.validators import (
    PasswordStrengthResult,
    sanitize_string,
    validate_cpf,
    validate_email,
    validate_password_strength,
)


class TestDateUtils:
    """Tests for date utilities."""

    def test_utc_now(self):
        """Test getting current UTC datetime."""
        result = utc_now()
        assert isinstance(result, datetime)
        assert result.tzinfo is not None

    def test_to_utc_naive(self):
        """Test converting naive datetime to UTC."""
        naive_dt = datetime(2024, 1, 15, 10, 30, 0)
        result = to_utc(naive_dt)
        assert result.tzinfo == UTC

    def test_to_utc_aware(self):
        """Test converting aware datetime to UTC."""
        import pytz

        sao_paulo = pytz.timezone("America/Sao_Paulo")
        aware_dt = datetime(2024, 1, 15, 10, 30, 0, tzinfo=sao_paulo)
        result = to_utc(aware_dt)
        assert result.tzinfo == UTC

    def test_format_datetime(self):
        """Test formatting datetime."""
        test_datetime = datetime(2024, 1, 15, 10, 30, 0, tzinfo=UTC)
        result = format_datetime(test_datetime)
        assert result == "2024-01-15T10:30:00Z"

    def test_format_datetime_custom_format(self):
        """Test formatting datetime with custom format."""
        test_datetime = datetime(2024, 1, 15, 10, 30, 0, tzinfo=UTC)
        result = format_datetime(test_datetime, "%Y-%m-%d")
        assert result == "2024-01-15"

    def test_parse_datetime(self):
        """Test parsing datetime string."""
        result = parse_datetime("2024-01-15T10:30:00Z")
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15

    def test_parse_datetime_various_formats(self):
        """Test parsing various datetime formats."""
        result = parse_datetime("2024-01-15")
        assert result.year == 2024

        result = parse_datetime("January 15, 2024")
        assert result.year == 2024

    def test_to_timezone(self):
        """Test converting datetime to specific timezone."""
        utc_dt = datetime(2024, 1, 15, 12, 0, 0, tzinfo=UTC)
        result = to_timezone(utc_dt, "America/Sao_Paulo")
        assert result.tzinfo is not None

    def test_get_date_range_ordered(self):
        """Test getting ordered date range."""
        start = datetime(2024, 1, 1, 0, 0, 0)
        end = datetime(2024, 1, 31, 23, 59, 59)
        result_start, result_end = get_date_range(start, end)
        assert result_start <= result_end

    def test_get_date_range_swapped(self):
        """Test date range auto-swaps if reversed."""
        start = datetime(2024, 1, 31, 23, 59, 59)
        end = datetime(2024, 1, 1, 0, 0, 0)
        result_start, result_end = get_date_range(start, end)
        assert result_start <= result_end

    def test_is_expired_true(self):
        """Test expired datetime."""
        past = datetime(2020, 1, 1, 0, 0, 0, tzinfo=UTC)
        assert is_expired(past) is True

    def test_is_expired_false(self):
        """Test non-expired datetime."""
        future = datetime(2030, 1, 1, 0, 0, 0, tzinfo=UTC)
        assert is_expired(future) is False

    def test_add_days(self):
        """Test adding days to datetime."""
        dt = datetime(2024, 1, 15, 12, 0, 0)
        result = add_days(dt, 7)
        assert result.day == 22

    def test_add_days_negative(self):
        """Test subtracting days from datetime."""
        dt = datetime(2024, 1, 15, 12, 0, 0)
        result = add_days(dt, -5)
        assert result.day == 10

    def test_add_minutes(self):
        """Test adding minutes to datetime."""
        dt = datetime(2024, 1, 15, 12, 0, 0)
        result = add_minutes(dt, 30)
        assert result.minute == 30

    def test_add_minutes_overflow(self):
        """Test adding minutes with hour overflow."""
        dt = datetime(2024, 1, 15, 12, 45, 0)
        result = add_minutes(dt, 30)
        assert result.hour == 13
        assert result.minute == 15


class TestValidators:
    """Tests for validators."""

    def test_validate_email_valid(self):
        """Test validating valid email."""
        assert validate_email("test@example.com") is True
        assert validate_email("user.name@domain.org") is True
        assert validate_email("user+tag@sub.domain.com") is True

    def test_validate_email_invalid(self):
        """Test validating invalid email."""
        assert validate_email("invalid-email") is False
        assert validate_email("@domain.com") is False
        assert validate_email("user@") is False
        assert validate_email("user@.com") is False

    def test_validate_email_empty(self):
        """Test validating empty email."""
        assert validate_email("") is False

    def test_validate_password_strength_strong(self):
        """Test validating strong password."""
        result = validate_password_strength("SecurePass123!")
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_password_strength_weak(self):
        """Test validating weak password."""
        result = validate_password_strength("weak")
        assert result.is_valid is False
        assert len(result.errors) > 0

    def test_validate_password_strength_no_uppercase(self):
        """Test password without uppercase."""
        result = validate_password_strength("lowercase123!")
        assert result.is_valid is False
        assert any("uppercase" in e.lower() for e in result.errors)

    def test_validate_password_strength_no_digit(self):
        """Test password without digit."""
        result = validate_password_strength("NoDigitsHere!")
        assert result.is_valid is False
        assert any("digit" in e.lower() for e in result.errors)

    def test_validate_password_strength_no_special(self):
        """Test password without special character."""
        result = validate_password_strength("NoSpecial123")
        assert result.is_valid is False
        assert any("special" in e.lower() for e in result.errors)

    def test_validate_password_strength_short(self):
        """Test password too short."""
        result = validate_password_strength("Aa1!")
        assert result.is_valid is False
        assert any("8" in e for e in result.errors)

    def test_password_strength_result_error_message(self):
        """Test error message property."""
        result = PasswordStrengthResult(is_valid=False, errors=["Error 1", "Error 2"])
        assert "Error 1" in result.error_message
        assert "Error 2" in result.error_message

    def test_password_strength_result_empty_error_message(self):
        """Test empty error message when valid."""
        result = PasswordStrengthResult(is_valid=True, errors=[])
        assert result.error_message == ""

    def test_validate_cpf_valid(self):
        """Test validating valid CPF."""
        # Valid test CPF
        assert validate_cpf("529.982.247-25") is True
        assert validate_cpf("52998224725") is True

    def test_validate_cpf_invalid(self):
        """Test validating invalid CPF."""
        assert validate_cpf("123.456.789-00") is False
        assert validate_cpf("000.000.000-00") is False
        assert validate_cpf("111.111.111-11") is False

    def test_validate_cpf_invalid_length(self):
        """Test CPF with invalid length."""
        assert validate_cpf("123") is False
        assert validate_cpf("1234567890123") is False

    def test_sanitize_string(self):
        """Test string sanitization."""
        assert sanitize_string("  hello  ") == "hello"
        assert sanitize_string("hello\x00world") == "helloworld"

    def test_sanitize_string_null_bytes(self):
        """Test removing null bytes."""
        result = sanitize_string("test\x00string")
        assert "\x00" not in result

    def test_sanitize_string_whitespace(self):
        """Test trimming whitespace."""
        result = sanitize_string("   spaced   ")
        assert result == "spaced"
