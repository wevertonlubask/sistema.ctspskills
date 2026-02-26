"""Application settings using Pydantic Settings."""

from functools import lru_cache
from typing import Literal

from cryptography.fernet import Fernet
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="CT-SPSkills")
    app_version: str = Field(default="0.1.0")
    app_env: Literal["development", "staging", "production"] = Field(default="development")
    debug: bool = Field(default=False)

    # Server
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    reload: bool = Field(default=False)

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/ct_spskills"
    )
    database_echo: bool = Field(default=False)

    # JWT
    jwt_secret_key: str = Field(default="your-super-secret-key-change-in-production-min-32-chars")
    jwt_algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=15)
    refresh_token_expire_days: int = Field(default=7)

    # Security - stored as string to avoid Pydantic JSON parsing issues
    allowed_origins_str: str = Field(
        default="http://localhost:3000,http://localhost:8000",
        validation_alias="ALLOWED_ORIGINS",
    )
    bcrypt_rounds: int = Field(default=12)

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(default="INFO")
    log_format: Literal["json", "text"] = Field(default="json")

    # File Storage
    upload_dir: str = Field(default="./uploads")
    max_upload_size_mb: int = Field(default=10)

    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True)
    rate_limit_requests: int = Field(default=500)
    rate_limit_period_seconds: int = Field(default=60)

    # Field-level encryption
    field_encryption_key: str = Field(
        default="",
        description='Fernet key for encrypting sensitive PII fields (base64 URL-safe, generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")',
    )

    @property
    def allowed_origins(self) -> list[str]:
        """Parse allowed origins from comma-separated string."""
        return [origin.strip() for origin in self.allowed_origins_str.split(",") if origin.strip()]

    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret_key(cls, v: str) -> str:
        """Validate JWT secret key length."""
        if len(v) < 32:
            raise ValueError("JWT secret key must be at least 32 characters long")
        return v

    @field_validator("field_encryption_key")
    @classmethod
    def validate_encryption_key(cls, v: str) -> str:
        """Validate Fernet encryption key format."""
        if not v:
            raise ValueError(
                "FIELD_ENCRYPTION_KEY must be set. "
                'Generate one with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"'
            )
        try:
            Fernet(v.encode())
        except Exception as exc:
            raise ValueError(
                "FIELD_ENCRYPTION_KEY must be a valid Fernet key (base64 URL-safe, 32 bytes)"
            ) from exc
        return v

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.app_env == "production"

    @property
    def max_upload_size_bytes(self) -> int:
        """Get max upload size in bytes."""
        return self.max_upload_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
