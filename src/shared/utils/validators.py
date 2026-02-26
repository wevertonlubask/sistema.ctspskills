"""Validation utility functions."""

import re
from dataclasses import dataclass


@dataclass
class PasswordStrengthResult:
    """Result of password strength validation."""

    is_valid: bool
    errors: list[str]

    @property
    def error_message(self) -> str:
        """Get combined error message."""
        return "; ".join(self.errors) if self.errors else ""


def validate_email(email: str) -> bool:
    """Validate email format using regex.

    Args:
        email: Email address to validate.

    Returns:
        True if email format is valid, False otherwise.
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_password_strength(
    password: str,
    min_length: int = 8,
    require_uppercase: bool = True,
    require_lowercase: bool = True,
    require_digit: bool = True,
    require_special: bool = True,
) -> PasswordStrengthResult:
    """Validate password strength according to RN13.

    Password requirements:
    - Minimum 8 characters (configurable)
    - At least 1 uppercase letter
    - At least 1 lowercase letter
    - At least 1 digit
    - At least 1 special character

    Args:
        password: Password to validate.
        min_length: Minimum password length.
        require_uppercase: Require at least one uppercase letter.
        require_lowercase: Require at least one lowercase letter.
        require_digit: Require at least one digit.
        require_special: Require at least one special character.

    Returns:
        PasswordStrengthResult with validation status and errors.
    """
    errors: list[str] = []

    if len(password) < min_length:
        errors.append(f"Password must be at least {min_length} characters long")

    if require_uppercase and not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter")

    if require_lowercase and not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter")

    if require_digit and not re.search(r"\d", password):
        errors.append("Password must contain at least one digit")

    if require_special and not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=\[\]\\;'/`~]", password):
        errors.append("Password must contain at least one special character")

    return PasswordStrengthResult(
        is_valid=len(errors) == 0,
        errors=errors,
    )


def validate_cpf(cpf: str) -> bool:
    """Validate Brazilian CPF number.

    Args:
        cpf: CPF number (can include dots and dash).

    Returns:
        True if CPF is valid, False otherwise.
    """
    # Remove non-digits
    cpf = re.sub(r"\D", "", cpf)

    # CPF must have 11 digits
    if len(cpf) != 11:
        return False

    # Check for known invalid CPFs
    if cpf == cpf[0] * 11:
        return False

    # Validate first check digit
    total = sum(int(cpf[i]) * (10 - i) for i in range(9))
    remainder = total % 11
    digit1 = 0 if remainder < 2 else 11 - remainder
    if int(cpf[9]) != digit1:
        return False

    # Validate second check digit
    total = sum(int(cpf[i]) * (11 - i) for i in range(10))
    remainder = total % 11
    digit2 = 0 if remainder < 2 else 11 - remainder
    if int(cpf[10]) != digit2:
        return False

    return True


def sanitize_string(value: str) -> str:
    """Sanitize string by removing potentially dangerous characters."""
    # Remove null bytes
    value = value.replace("\x00", "")
    # Strip whitespace
    value = value.strip()
    return value
