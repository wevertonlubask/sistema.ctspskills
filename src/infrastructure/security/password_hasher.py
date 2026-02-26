"""Password hashing implementation using bcrypt."""

import bcrypt

from src.config.settings import get_settings
from src.domain.identity.services.password_service import PasswordService

settings = get_settings()


class BcryptPasswordHasher(PasswordService):
    """Bcrypt implementation of PasswordService."""

    def __init__(self, rounds: int | None = None) -> None:
        """Initialize the password hasher.

        Args:
            rounds: Number of bcrypt rounds. Defaults to settings.bcrypt_rounds.
        """
        self._rounds = rounds or settings.bcrypt_rounds

    def hash_password(self, plain_password: str) -> str:
        """Hash a plain text password using bcrypt.

        Args:
            plain_password: The plain text password to hash.

        Returns:
            The hashed password.
        """
        # Encode password to bytes, truncate to 72 bytes (bcrypt limit)
        password_bytes = plain_password.encode("utf-8")[:72]
        salt = bcrypt.gensalt(rounds=self._rounds)
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode("utf-8")  # type: ignore[no-any-return]

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain text password against a bcrypt hash.

        Args:
            plain_password: The plain text password to verify.
            hashed_password: The hashed password to compare against.

        Returns:
            True if password matches, False otherwise.
        """
        try:
            # Encode password to bytes, truncate to 72 bytes (bcrypt limit)
            password_bytes = plain_password.encode("utf-8")[:72]
            hashed_bytes = hashed_password.encode("utf-8")
            return bcrypt.checkpw(password_bytes, hashed_bytes)  # type: ignore[no-any-return]
        except (ValueError, TypeError):
            return False
