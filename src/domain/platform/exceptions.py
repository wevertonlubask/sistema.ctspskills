"""Platform domain exceptions."""

from src.shared.exceptions import DomainException


class InvalidLogoException(DomainException):
    """Raised when logo file is invalid."""

    def __init__(self, reason: str) -> None:
        super().__init__(message=f"Invalid logo: {reason}")
        self.reason = reason


class InvalidFaviconException(DomainException):
    """Raised when favicon file is invalid."""

    def __init__(self, reason: str) -> None:
        super().__init__(message=f"Invalid favicon: {reason}")
        self.reason = reason
