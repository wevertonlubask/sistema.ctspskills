"""Identity domain exceptions."""

from src.shared.exceptions import DomainException, ErrorCode


class UserInactiveException(DomainException):
    """Raised when an inactive user tries to perform an action."""

    def __init__(self, user_id: str, status: str) -> None:
        super().__init__(
            message=f"User account is {status}",
            code=ErrorCode.USER_INACTIVE,
            details={"user_id": user_id, "status": status},
        )


class InvalidPasswordException(DomainException):
    """Raised when password validation fails."""

    def __init__(self, reason: str = "Invalid password") -> None:
        super().__init__(
            message=reason,
            code=ErrorCode.INVALID_PASSWORD,
        )


class UserAlreadyExistsException(DomainException):
    """Raised when trying to create a user that already exists."""

    def __init__(self, email: str) -> None:
        super().__init__(
            message=f"User with email '{email}' already exists",
            code=ErrorCode.USER_ALREADY_EXISTS,
            details={"email": email},
        )


class UserNotFoundException(DomainException):
    """Raised when a user is not found."""

    def __init__(self, identifier: str, field: str = "id") -> None:
        super().__init__(
            message=f"User with {field} '{identifier}' not found",
            code=ErrorCode.USER_NOT_FOUND,
            details={field: identifier},
        )
