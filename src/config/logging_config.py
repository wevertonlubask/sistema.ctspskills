"""Structured logging configuration."""

import json
import logging
import sys
from contextvars import ContextVar
from datetime import datetime
from typing import Any

from src.config.settings import get_settings

# Context variables for request tracking
request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)
user_id_var: ContextVar[str | None] = ContextVar("user_id", default=None)


class StructuredJsonFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def __init__(
        self,
        include_extra: bool = True,
        include_stack_info: bool = True,
    ) -> None:
        """Initialize formatter.

        Args:
            include_extra: Include extra fields in log output.
            include_stack_info: Include stack info for exceptions.
        """
        super().__init__()
        self._include_extra = include_extra
        self._include_stack_info = include_stack_info

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON.

        Args:
            record: Log record to format.

        Returns:
            JSON formatted string.
        """
        log_entry: dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add location info
        log_entry["location"] = {
            "file": record.filename,
            "line": record.lineno,
            "function": record.funcName,
        }

        # Add context variables
        if request_id := request_id_var.get():
            log_entry["request_id"] = request_id
        if user_id := user_id_var.get():
            log_entry["user_id"] = user_id

        # Add exception info
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
            }
            if self._include_stack_info:
                log_entry["exception"]["traceback"] = self.formatException(record.exc_info)

        # Add extra fields
        if self._include_extra:
            extra_fields = {
                key: value
                for key, value in record.__dict__.items()
                if key
                not in {
                    "name",
                    "msg",
                    "args",
                    "created",
                    "filename",
                    "funcName",
                    "levelname",
                    "levelno",
                    "lineno",
                    "module",
                    "msecs",
                    "pathname",
                    "process",
                    "processName",
                    "relativeCreated",
                    "stack_info",
                    "exc_info",
                    "exc_text",
                    "thread",
                    "threadName",
                    "message",
                    "taskName",
                }
                and not key.startswith("_")
            }
            if extra_fields:
                log_entry["extra"] = extra_fields

        return json.dumps(log_entry, default=str, ensure_ascii=False)


class ColoredTextFormatter(logging.Formatter):
    """Colored text formatter for development."""

    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors.

        Args:
            record: Log record to format.

        Returns:
            Colored formatted string.
        """
        color = self.COLORS.get(record.levelname, "")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Build context string
        context_parts = []
        if request_id := request_id_var.get():
            context_parts.append(f"req={request_id[:8]}")
        if user_id := user_id_var.get():
            context_parts.append(f"user={user_id[:8]}")
        context_str = f" [{', '.join(context_parts)}]" if context_parts else ""

        # Format message
        message = record.getMessage()
        formatted = (
            f"{color}{timestamp} | {record.levelname:8}{self.RESET} | "
            f"{record.name}{context_str} | {message}"
        )

        # Add exception info
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"

        return formatted


def setup_logging() -> None:
    """Configure application logging."""
    settings = get_settings()

    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level))

    # Remove existing handlers
    root_logger.handlers.clear()

    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, settings.log_level))

    # Choose formatter based on settings and environment
    formatter: logging.Formatter
    if settings.log_format == "json" or settings.is_production:
        formatter = StructuredJsonFormatter()
    else:
        formatter = ColoredTextFormatter()

    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # Configure specific loggers
    loggers_config: dict[str, int] = {
        "uvicorn": logging.INFO,
        "uvicorn.access": logging.WARNING if settings.is_production else logging.INFO,
        "uvicorn.error": logging.ERROR,
        "sqlalchemy.engine": logging.WARNING if not settings.database_echo else logging.INFO,
        "httpx": logging.WARNING,
        "httpcore": logging.WARNING,
        "asyncio": logging.WARNING,
    }

    for logger_name, level in loggers_config.items():
        logging.getLogger(logger_name).setLevel(level)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name.

    Args:
        name: Logger name.

    Returns:
        Logger instance.
    """
    return logging.getLogger(name)


class LoggerMixin:
    """Mixin class to add logging capabilities."""

    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        return get_logger(self.__class__.__name__)


class LogContext:
    """Context manager for adding logging context."""

    def __init__(
        self,
        request_id: str | None = None,
        user_id: str | None = None,
    ) -> None:
        """Initialize log context.

        Args:
            request_id: Request ID to add to logs.
            user_id: User ID to add to logs.
        """
        self._request_id = request_id
        self._user_id = user_id
        self._old_request_id: str | None = None
        self._old_user_id: str | None = None

    def __enter__(self) -> "LogContext":
        """Enter context."""
        if self._request_id:
            self._old_request_id = request_id_var.get()
            request_id_var.set(self._request_id)
        if self._user_id:
            self._old_user_id = user_id_var.get()
            user_id_var.set(self._user_id)
        return self

    def __exit__(self, *args: Any) -> None:
        """Exit context."""
        if self._request_id:
            request_id_var.set(self._old_request_id)
        if self._user_id:
            user_id_var.set(self._old_user_id)
