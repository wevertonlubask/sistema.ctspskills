"""Upload evidence use case."""

from pathlib import Path
from uuid import UUID, uuid4

from src.application.training.dtos.evidence_dto import EvidenceDTO, UploadEvidenceDTO
from src.config.settings import get_settings
from src.domain.training.entities.evidence import Evidence
from src.domain.training.exceptions import (
    InvalidEvidenceException,
    TrainingNotFoundException,
)
from src.domain.training.repositories.evidence_repository import EvidenceRepository
from src.domain.training.repositories.training_repository import TrainingRepository


class UploadEvidenceUseCase:
    """Use case for uploading evidence to a training session."""

    def __init__(
        self,
        training_repository: TrainingRepository,
        evidence_repository: EvidenceRepository,
    ) -> None:
        self._training_repository = training_repository
        self._evidence_repository = evidence_repository
        self._settings = get_settings()

    async def execute(
        self,
        training_id: UUID,
        uploader_id: UUID,
        dto: UploadEvidenceDTO,
    ) -> EvidenceDTO:
        """Upload evidence for a training session.

        Args:
            training_id: Training session ID.
            uploader_id: ID of the user uploading.
            dto: Evidence upload data.

        Returns:
            Created evidence DTO.

        Raises:
            TrainingNotFoundException: If training not found.
            InvalidEvidenceException: If file is invalid.
        """
        # Verify training exists
        training = await self._training_repository.get_by_id(training_id)
        if not training:
            raise TrainingNotFoundException(str(training_id))

        # Validate file type
        if not Evidence.is_valid_mime_type(dto.mime_type):
            raise InvalidEvidenceException(
                f"File type '{dto.mime_type}' is not allowed. "
                f"Allowed types: {', '.join(Evidence.ALLOWED_TYPES)}"
            )

        # Validate file size
        file_size = len(dto.file_content)
        if not Evidence.is_valid_file_size(file_size):
            max_mb = Evidence.MAX_FILE_SIZE / (1024 * 1024)
            raise InvalidEvidenceException(f"File size exceeds maximum of {max_mb}MB")

        # Generate unique file path
        file_extension = self._get_extension(dto.mime_type)
        unique_filename = f"{uuid4()}{file_extension}"
        relative_path = f"evidences/{training_id}/{unique_filename}"
        full_path = Path(self._settings.upload_dir) / relative_path

        # Ensure directory exists
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        with open(full_path, "wb") as f:
            f.write(dto.file_content)

        # Create evidence entity
        evidence = Evidence(
            training_session_id=training_id,
            file_name=dto.file_name,
            file_path=relative_path,
            file_size=file_size,
            mime_type=dto.mime_type,
            evidence_type=dto.evidence_type,
            description=dto.description,
            uploaded_by=uploader_id,
        )

        # Save to database
        created = await self._evidence_repository.create(evidence)
        return EvidenceDTO.from_entity(created)

    def _get_extension(self, mime_type: str) -> str:
        """Get file extension from MIME type."""
        extensions = {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/gif": ".gif",
            "application/pdf": ".pdf",
            "video/mp4": ".mp4",
            "video/webm": ".webm",
        }
        return extensions.get(mime_type, "")
