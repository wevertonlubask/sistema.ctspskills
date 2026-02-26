"""Evidence DTOs."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.domain.training.entities.evidence import Evidence, EvidenceType


@dataclass
class UploadEvidenceDTO:
    """DTO for uploading evidence."""

    file_name: str
    file_content: bytes
    mime_type: str
    evidence_type: EvidenceType = EvidenceType.PHOTO
    description: str | None = None


@dataclass
class EvidenceDTO:
    """DTO for evidence data."""

    id: UUID
    training_session_id: UUID
    file_name: str
    file_path: str
    file_size: int
    mime_type: str
    evidence_type: EvidenceType
    description: str | None
    uploaded_by: UUID | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, entity: Evidence) -> "EvidenceDTO":
        """Create DTO from entity."""
        return cls(
            id=entity.id,
            training_session_id=entity.training_session_id,
            file_name=entity.file_name,
            file_path=entity.file_path,
            file_size=entity.file_size,
            mime_type=entity.mime_type,
            evidence_type=entity.evidence_type,
            description=entity.description,
            uploaded_by=entity.uploaded_by,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
