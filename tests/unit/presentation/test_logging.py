"""Tests for structured logging."""

import json
import logging

import pytest

from src.config.logging_config import (
    ColoredTextFormatter,
    LogContext,
    StructuredJsonFormatter,
    get_logger,
    request_id_var,
    user_id_var,
)


class TestStructuredJsonFormatter:
    """Tests for StructuredJsonFormatter."""

    @pytest.fixture
    def formatter(self) -> StructuredJsonFormatter:
        """Create a formatter instance."""
        return StructuredJsonFormatter()

    @pytest.fixture
    def log_record(self) -> logging.LogRecord:
        """Create a test log record."""
        return logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/path/to/file.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

    def test_formats_as_json(
        self,
        formatter: StructuredJsonFormatter,
        log_record: logging.LogRecord,
    ) -> None:
        """Test that output is valid JSON."""
        output = formatter.format(log_record)
        parsed = json.loads(output)

        assert parsed["level"] == "INFO"
        assert parsed["logger"] == "test.logger"
        assert parsed["message"] == "Test message"
        assert "timestamp" in parsed
        assert parsed["timestamp"].endswith("Z")

    def test_includes_location_info(
        self,
        formatter: StructuredJsonFormatter,
        log_record: logging.LogRecord,
    ) -> None:
        """Test that location info is included."""
        output = formatter.format(log_record)
        parsed = json.loads(output)

        assert "location" in parsed
        assert parsed["location"]["line"] == 42

    def test_includes_request_id_from_context(
        self,
        formatter: StructuredJsonFormatter,
        log_record: logging.LogRecord,
    ) -> None:
        """Test that request_id from context var is included."""
        request_id_var.set("test-request-id-123")
        try:
            output = formatter.format(log_record)
            parsed = json.loads(output)
            assert parsed["request_id"] == "test-request-id-123"
        finally:
            request_id_var.set(None)

    def test_includes_user_id_from_context(
        self,
        formatter: StructuredJsonFormatter,
        log_record: logging.LogRecord,
    ) -> None:
        """Test that user_id from context var is included."""
        user_id_var.set("test-user-id-456")
        try:
            output = formatter.format(log_record)
            parsed = json.loads(output)
            assert parsed["user_id"] == "test-user-id-456"
        finally:
            user_id_var.set(None)

    def test_includes_exception_info(self, formatter: StructuredJsonFormatter) -> None:
        """Test that exception info is included."""
        try:
            raise ValueError("Test error")
        except ValueError:
            import sys

            exc_info = sys.exc_info()

        record = logging.LogRecord(
            name="test.logger",
            level=logging.ERROR,
            pathname="/path/to/file.py",
            lineno=42,
            msg="Error occurred",
            args=(),
            exc_info=exc_info,
        )

        output = formatter.format(record)
        parsed = json.loads(output)

        assert "exception" in parsed
        assert parsed["exception"]["type"] == "ValueError"
        assert "Test error" in parsed["exception"]["message"]

    def test_includes_extra_fields(self, formatter: StructuredJsonFormatter) -> None:
        """Test that extra fields are included."""
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/path/to/file.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.custom_field = "custom_value"
        record.another_field = 123

        output = formatter.format(record)
        parsed = json.loads(output)

        assert "extra" in parsed
        assert parsed["extra"]["custom_field"] == "custom_value"
        assert parsed["extra"]["another_field"] == 123


class TestColoredTextFormatter:
    """Tests for ColoredTextFormatter."""

    @pytest.fixture
    def formatter(self) -> ColoredTextFormatter:
        """Create a formatter instance."""
        return ColoredTextFormatter()

    def test_formats_log_message(self, formatter: ColoredTextFormatter) -> None:
        """Test that message is formatted correctly."""
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/path/to/file.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        output = formatter.format(record)

        assert "INFO" in output
        assert "test.logger" in output
        assert "Test message" in output

    def test_includes_context_in_brackets(
        self,
        formatter: ColoredTextFormatter,
    ) -> None:
        """Test that context vars are included in brackets."""
        request_id_var.set("abc12345-test")
        user_id_var.set("user6789-test")
        try:
            record = logging.LogRecord(
                name="test.logger",
                level=logging.INFO,
                pathname="/path/to/file.py",
                lineno=42,
                msg="Test message",
                args=(),
                exc_info=None,
            )

            output = formatter.format(record)

            assert "req=abc12345" in output
            assert "user=user6789" in output
        finally:
            request_id_var.set(None)
            user_id_var.set(None)


class TestLogContext:
    """Tests for LogContext context manager."""

    def test_sets_request_id(self) -> None:
        """Test that request_id is set within context."""
        assert request_id_var.get() is None

        with LogContext(request_id="test-request-123"):
            assert request_id_var.get() == "test-request-123"

        assert request_id_var.get() is None

    def test_sets_user_id(self) -> None:
        """Test that user_id is set within context."""
        assert user_id_var.get() is None

        with LogContext(user_id="test-user-456"):
            assert user_id_var.get() == "test-user-456"

        assert user_id_var.get() is None

    def test_sets_both_ids(self) -> None:
        """Test that both IDs can be set."""
        with LogContext(request_id="req-123", user_id="user-456"):
            assert request_id_var.get() == "req-123"
            assert user_id_var.get() == "user-456"

        assert request_id_var.get() is None
        assert user_id_var.get() is None

    def test_restores_previous_values(self) -> None:
        """Test that previous values are restored."""
        request_id_var.set("outer-request")

        with LogContext(request_id="inner-request"):
            assert request_id_var.get() == "inner-request"

        assert request_id_var.get() == "outer-request"
        request_id_var.set(None)


class TestGetLogger:
    """Tests for get_logger function."""

    def test_returns_logger_with_name(self) -> None:
        """Test that logger with specified name is returned."""
        logger = get_logger("my.test.logger")
        assert logger.name == "my.test.logger"

    def test_same_name_returns_same_logger(self) -> None:
        """Test that same name returns same logger instance."""
        logger1 = get_logger("same.logger")
        logger2 = get_logger("same.logger")
        assert logger1 is logger2
