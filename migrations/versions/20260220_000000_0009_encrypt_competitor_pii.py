"""Encrypt sensitive PII fields in the competitors table.

Encrypts: document_number, phone, emergency_contact, emergency_phone
using Fernet symmetric encryption (AES-128-CBC + HMAC-SHA256).

Requires FIELD_ENCRYPTION_KEY environment variable to be set before running.

Revision ID: 0009
Revises: 0008
Create Date: 2026-02-20 00:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0009"
down_revision: str = "0008"
branch_labels: None = None
depends_on: None = None

_ENCRYPTED_COLUMNS = [
    "document_number",
    "phone",
    "emergency_contact",
    "emergency_phone",
]


def _get_fernet() -> "Fernet":  # type: ignore[name-defined]
    """Load Fernet instance from application settings (.env via pydantic-settings)."""
    from cryptography.fernet import Fernet  # noqa: PLC0415
    from src.config.settings import get_settings  # noqa: PLC0415

    key = get_settings().field_encryption_key
    if not key:
        raise RuntimeError(
            "FIELD_ENCRYPTION_KEY must be set in the .env file before running this migration.\n"
            "Generate a key with: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
        )
    return Fernet(key.encode())


def upgrade() -> None:
    """Change column types to Text and encrypt existing plaintext data."""
    # Step 1: Widen columns to Text to accommodate ciphertext (~3x longer than plaintext)
    with op.batch_alter_table("competitors") as batch_op:
        batch_op.alter_column(
            "document_number",
            existing_type=sa.String(20),
            type_=sa.Text(),
            existing_nullable=True,
        )
        batch_op.alter_column(
            "phone",
            existing_type=sa.String(20),
            type_=sa.Text(),
            existing_nullable=True,
        )
        batch_op.alter_column(
            "emergency_contact",
            existing_type=sa.String(255),
            type_=sa.Text(),
            existing_nullable=True,
        )
        batch_op.alter_column(
            "emergency_phone",
            existing_type=sa.String(20),
            type_=sa.Text(),
            existing_nullable=True,
        )

    # Step 2: Encrypt existing plaintext values row by row
    fernet = _get_fernet()
    conn = op.get_bind()

    rows = conn.execute(
        sa.text(
            "SELECT id, document_number, phone, emergency_contact, emergency_phone"
            " FROM competitors"
        )
    ).fetchall()

    for row in rows:
        row_id = str(row.id)
        for col in _ENCRYPTED_COLUMNS:
            val: str | None = getattr(row, col)
            if val:
                encrypted = fernet.encrypt(val.encode()).decode()
                conn.execute(
                    sa.text(f"UPDATE competitors SET {col} = :v WHERE id = :id"),  # nosec B608
                    {"v": encrypted, "id": row_id},
                )


def downgrade() -> None:
    """Decrypt data and revert column types to original String lengths."""
    # Step 1: Decrypt existing ciphertext values row by row
    fernet = _get_fernet()
    conn = op.get_bind()

    rows = conn.execute(
        sa.text(
            "SELECT id, document_number, phone, emergency_contact, emergency_phone"
            " FROM competitors"
        )
    ).fetchall()

    for row in rows:
        row_id = str(row.id)
        for col in _ENCRYPTED_COLUMNS:
            val: str | None = getattr(row, col)
            if val:
                try:
                    from cryptography.fernet import InvalidToken  # noqa: PLC0415

                    decrypted = fernet.decrypt(val.encode()).decode()
                    conn.execute(
                        sa.text(f"UPDATE competitors SET {col} = :v WHERE id = :id"),  # nosec B608
                        {"v": decrypted, "id": row_id},
                    )
                except (InvalidToken, Exception):  # nosec B110
                    pass  # already plaintext or unrecoverable

    # Step 2: Narrow columns back to original String lengths
    with op.batch_alter_table("competitors") as batch_op:
        batch_op.alter_column(
            "document_number",
            existing_type=sa.Text(),
            type_=sa.String(20),
            existing_nullable=True,
        )
        batch_op.alter_column(
            "phone",
            existing_type=sa.Text(),
            type_=sa.String(20),
            existing_nullable=True,
        )
        batch_op.alter_column(
            "emergency_contact",
            existing_type=sa.Text(),
            type_=sa.String(255),
            existing_nullable=True,
        )
        batch_op.alter_column(
            "emergency_phone",
            existing_type=sa.Text(),
            type_=sa.String(20),
            existing_nullable=True,
        )
