"""Evidence entity for training documentation."""

from datetime import datetime
from enum import Enum
from uuid import UUID

from src.shared.domain.entity import Entity


class EvidenceType(str, Enum):
    """Type of evidence."""

    PHOTO = "photo"
    DOCUMENT = "document"
    VIDEO = "video"
    CERTIFICATE = "certificate"
    OTHER = "other"


class Evidence(Entity[UUID]):
    """Evidence entity representing documentation for a training session.

    Evidence can be photos, documents, videos, or certificates that
    prove the training activity occurred.
    """

    # Maximum file size in bytes (10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024
    # Allowed MIME types
    ALLOWED_TYPES = [
        "image/jpeg",
        "image/png",
        "image/gif",
        "application/pdf",
        "video/mp4",
        "video/webm",
    ]

    def __init__(
        self,
        training_session_id: UUID,
        file_name: str,
        file_path: str,
        file_size: int,
        mime_type: str,
        evidence_type: EvidenceType = EvidenceType.PHOTO,
        description: str | None = None,
        uploaded_by: UUID | None = None,
        id: UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        """Initialize evidence.

        Args:
            training_session_id: ID of the training session.
            file_name: Original file name.
            file_path: Storage path for the file.
            file_size: File size in bytes.
            mime_type: MIME type of the file.
            evidence_type: Type of evidence.
            description: Optional description.
            uploaded_by: User ID who uploaded.
            id: Optional UUID.
            created_at: Creation timestamp.
            updated_at: Update timestamp.
        """
        super().__init__(id=id, created_at=created_at, updated_at=updated_at)
        self._training_session_id = training_session_id
        self._file_name = file_name
        self._file_path = file_path
        self._file_size = file_size
        self._mime_type = mime_type
        self._evidence_type = evidence_type
        self._description = description
        self._uploaded_by = uploaded_by

    @property
    def training_session_id(self) -> UUID:
        """Get training session ID."""
        return self._training_session_id

    @property
    def file_name(self) -> str:
        """Get original file name."""
        return self._file_name

    @property
    def file_path(self) -> str:
        """Get storage file path."""
        return self._file_path

    @property
    def file_size(self) -> int:
        """Get file size in bytes."""
        return self._file_size

    @property
    def mime_type(self) -> str:
        """Get file MIME type."""
        return self._mime_type

    @property
    def evidence_type(self) -> EvidenceType:
        """Get evidence type."""
        return self._evidence_type

    @property
    def description(self) -> str | None:
        """Get description."""
        return self._description

    @property
    def uploaded_by(self) -> UUID | None:
        """Get uploader user ID."""
        return self._uploaded_by

    def update_description(self, description: str | None) -> None:
        """Update evidence description."""
        self._description = description
        self._touch()

    @classmethod
    def is_valid_mime_type(cls, mime_type: str) -> bool:
        """Check if MIME type is allowed."""
        return mime_type in cls.ALLOWED_TYPES

    @classmethod
    def is_valid_file_size(cls, size: int) -> bool:
        """Check if file size is within limits."""
        return 0 < size <= cls.MAX_FILE_SIZE

    def __repr__(self) -> str:
        return f"Evidence(id={self._id}, file={self._file_name}, type={self._evidence_type})"
