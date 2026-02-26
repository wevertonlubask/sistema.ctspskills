"""Exceptions module."""

from src.shared.exceptions.application_exception import (
    ApplicationException,
    AuthenticationException,
    AuthorizationException,
    ConflictException,
    ResourceNotFoundException,
    ValidationException,
)
from src.shared.exceptions.base import (
    BaseAppException,
    ErrorCode,
)
from src.shared.exceptions.domain_exception import (
    BusinessRuleViolationException,
    DomainException,
    EntityNotFoundException,
    InvalidValueException,
)

__all__ = [
    # Base
    "BaseAppException",
    "ErrorCode",
    # Domain
    "DomainException",
    "EntityNotFoundException",
    "BusinessRuleViolationException",
    "InvalidValueException",
    # Application
    "ApplicationException",
    "AuthenticationException",
    "AuthorizationException",
    "ValidationException",
    "ResourceNotFoundException",
    "ConflictException",
]
