"""Domain layer exceptions."""

from typing import Any

from src.shared.exceptions.base import BaseAppException, ErrorCode


class DomainException(BaseAppException):
    """Base exception for domain layer errors."""

    pass


class EntityNotFoundException(DomainException):
    """Raised when an entity is not found in the domain."""

    def __init__(
        self,
        entity_type: str,
        entity_id: Any,
        message: str | None = None,
    ) -> None:
        self.entity_type = entity_type
        self.entity_id = entity_id
        super().__init__(
            message=message or f"{entity_type} with id '{entity_id}' not found",
            code=ErrorCode.ENTITY_NOT_FOUND,
            details={"entity_type": entity_type, "entity_id": str(entity_id)},
        )


class BusinessRuleViolationException(DomainException):
    """Raised when a business rule is violated."""

    def __init__(
        self,
        rule: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.rule = rule
        super().__init__(
            message=message,
            code=ErrorCode.BUSINESS_RULE_VIOLATION,
            details={"rule": rule, **(details or {})},
        )


class InvalidValueException(DomainException):
    """Raised when an invalid value is provided for a value object."""

    def __init__(
        self,
        field: str,
        value: Any,
        reason: str,
    ) -> None:
        self.field = field
        self.value = value
        self.reason = reason
        super().__init__(
            message=f"Invalid value for '{field}': {reason}",
            code=ErrorCode.INVALID_VALUE,
            details={"field": field, "value": str(value), "reason": reason},
        )
