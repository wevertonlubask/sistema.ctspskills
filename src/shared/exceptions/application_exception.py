"""Application layer exceptions."""

from typing import Any

from src.shared.exceptions.base import BaseAppException, ErrorCode


class ApplicationException(BaseAppException):
    """Base exception for application layer errors."""

    pass


class AuthenticationException(ApplicationException):
    """Raised when authentication fails."""

    def __init__(
        self,
        message: str = "Authentication failed",
        code: ErrorCode = ErrorCode.INVALID_CREDENTIALS,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message=message, code=code, details=details)


class AuthorizationException(ApplicationException):
    """Raised when authorization fails."""

    def __init__(
        self,
        message: str = "Permission denied",
        required_role: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        extra_details = {}
        if required_role:
            extra_details["required_role"] = required_role
        super().__init__(
            message=message,
            code=ErrorCode.PERMISSION_DENIED,
            details={**extra_details, **(details or {})},
        )


class ValidationException(ApplicationException):
    """Raised when input validation fails."""

    def __init__(
        self,
        message: str = "Validation error",
        errors: list[dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code=ErrorCode.VALIDATION_ERROR,
            details={"errors": errors or []},
        )


class ResourceNotFoundException(ApplicationException):
    """Raised when a requested resource is not found."""

    def __init__(
        self,
        resource_type: str,
        resource_id: Any,
        message: str | None = None,
    ) -> None:
        self.resource_type = resource_type
        self.resource_id = resource_id
        super().__init__(
            message=message or f"{resource_type} with id '{resource_id}' not found",
            code=ErrorCode.RESOURCE_NOT_FOUND,
            details={"resource_type": resource_type, "resource_id": str(resource_id)},
        )


class ConflictException(ApplicationException):
    """Raised when there's a conflict with existing resource."""

    def __init__(
        self,
        message: str,
        resource_type: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        extra_details = {}
        if resource_type:
            extra_details["resource_type"] = resource_type
        super().__init__(
            message=message,
            code=ErrorCode.RESOURCE_CONFLICT,
            details={**extra_details, **(details or {})},
        )
