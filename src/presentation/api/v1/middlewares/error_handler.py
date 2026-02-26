"""Global exception handler middleware."""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from src.config.logging_config import get_logger
from src.shared.exceptions import (
    BaseAppException,
    ErrorCode,
)

logger = get_logger(__name__)


def get_status_code(exception: BaseAppException) -> int:
    """Map exception to HTTP status code."""
    status_map = {
        # Authentication
        ErrorCode.INVALID_CREDENTIALS: status.HTTP_401_UNAUTHORIZED,
        ErrorCode.TOKEN_EXPIRED: status.HTTP_401_UNAUTHORIZED,
        ErrorCode.TOKEN_INVALID: status.HTTP_401_UNAUTHORIZED,
        ErrorCode.TOKEN_REVOKED: status.HTTP_401_UNAUTHORIZED,
        # Authorization
        ErrorCode.PERMISSION_DENIED: status.HTTP_403_FORBIDDEN,
        ErrorCode.INSUFFICIENT_ROLE: status.HTTP_403_FORBIDDEN,
        ErrorCode.USER_INACTIVE: status.HTTP_403_FORBIDDEN,
        # Not Found
        ErrorCode.RESOURCE_NOT_FOUND: status.HTTP_404_NOT_FOUND,
        ErrorCode.ENTITY_NOT_FOUND: status.HTTP_404_NOT_FOUND,
        ErrorCode.USER_NOT_FOUND: status.HTTP_404_NOT_FOUND,
        # Conflict
        ErrorCode.RESOURCE_ALREADY_EXISTS: status.HTTP_409_CONFLICT,
        ErrorCode.RESOURCE_CONFLICT: status.HTTP_409_CONFLICT,
        ErrorCode.USER_ALREADY_EXISTS: status.HTTP_409_CONFLICT,
        # Validation
        ErrorCode.VALIDATION_ERROR: status.HTTP_422_UNPROCESSABLE_ENTITY,
        ErrorCode.INVALID_VALUE: status.HTTP_422_UNPROCESSABLE_ENTITY,
        ErrorCode.INVALID_PASSWORD: status.HTTP_422_UNPROCESSABLE_ENTITY,
        ErrorCode.BUSINESS_RULE_VIOLATION: status.HTTP_422_UNPROCESSABLE_ENTITY,
    }
    return status_map.get(exception.code, status.HTTP_500_INTERNAL_SERVER_ERROR)  # type: ignore[no-any-return]


async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler.

    Args:
        request: HTTP request.
        exc: Exception raised.

    Returns:
        JSON response with error details.
    """
    # Handle our custom exceptions
    if isinstance(exc, BaseAppException):
        logger.warning(
            f"Application exception: {exc.code.value} - {exc.message}",
            extra={"path": request.url.path, "details": exc.details},
        )
        return JSONResponse(
            status_code=get_status_code(exc),
            content=exc.to_dict(),
        )

    # Handle Pydantic validation errors
    if isinstance(exc, RequestValidationError | ValidationError):
        errors = []
        if hasattr(exc, "errors"):
            for error in exc.errors():
                errors.append(
                    {
                        "field": ".".join(str(loc) for loc in error.get("loc", [])),
                        "message": error.get("msg", "Validation error"),
                        "type": error.get("type", "unknown"),
                    }
                )

        logger.warning(
            f"Validation error: {errors}",
            extra={"path": request.url.path},
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": ErrorCode.VALIDATION_ERROR.value,
                    "message": "Validation error",
                    "details": {"errors": errors},
                }
            },
        )

    # Handle unexpected errors
    logger.error(
        f"Unexpected error: {type(exc).__name__} - {str(exc)}",
        extra={"path": request.url.path},
        exc_info=True,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": ErrorCode.UNKNOWN_ERROR.value,
                "message": "An unexpected error occurred",
                "details": {},
            }
        },
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """Setup global exception handlers for the FastAPI app.

    Args:
        app: FastAPI application instance.
    """
    app.add_exception_handler(BaseAppException, exception_handler)
    app.add_exception_handler(RequestValidationError, exception_handler)
    app.add_exception_handler(Exception, exception_handler)
