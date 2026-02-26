"""Custom SQLAlchemy column types for the application."""
from __future__ import annotations

from typing import Any

from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy import Text, TypeDecorator

_fernet: Fernet | None = None


def _get_fernet() -> Fernet:
    """Lazily initialize the Fernet instance from settings."""
    global _fernet
    if _fernet is None:
        from src.config.settings import get_settings

        _fernet = Fernet(get_settings().field_encryption_key.encode())
    return _fernet


class EncryptedString(TypeDecorator[str]):
    """Transparently encrypts string columns using Fernet (AES-128-CBC + HMAC-SHA256).

    Stores ciphertext as a base64 URL-safe string in a TEXT column.
    Encryption/decryption is performed automatically on read and write.
    The FIELD_ENCRYPTION_KEY environment variable must be set.
    """

    impl = Text
    cache_ok = True

    def process_bind_param(self, value: str | None, dialect: Any) -> str | None:
        """Encrypt value before storing in the database."""
        if value is None:
            return None
        return _get_fernet().encrypt(value.encode()).decode()

    def process_result_value(self, value: str | None, dialect: Any) -> str | None:
        """Decrypt value after reading from the database."""
        if value is None:
            return None
        try:
            return _get_fernet().decrypt(value.encode()).decode()
        except (InvalidToken, Exception):  # nosec B110
            # Fallback for legacy unencrypted data during migration
            return value
