"""SQLAlchemy Evidence repository implementation."""

from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.training.entities.evidence import Evidence, EvidenceType
from src.domain.training.repositories.evidence_repository import EvidenceRepository
from src.infrastructure.database.models.training_model import EvidenceModel


class SQLAlchemyEvidenceRepository(EvidenceRepository):
    """SQLAlchemy implementation of EvidenceRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _model_to_entity(self, model: EvidenceModel) -> Evidence:
        """Convert EvidenceModel to Evidence entity."""
        return Evidence(
            id=model.id,
            training_session_id=model.training_session_id,
            file_name=model.file_name,
            file_path=model.file_path,
            file_size=model.file_size,
            mime_type=model.mime_type,
            evidence_type=EvidenceType(model.evidence_type),
            description=model.description,
            uploaded_by=model.uploaded_by,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _entity_to_model(self, entity: Evidence) -> EvidenceModel:
        """Convert Evidence entity to EvidenceModel."""
        return EvidenceModel(
            id=entity.id,
            training_session_id=entity.training_session_id,
            file_name=entity.file_name,
            file_path=entity.file_path,
            file_size=entity.file_size,
            mime_type=entity.mime_type,
            evidence_type=entity.evidence_type.value,
            description=entity.description,
            uploaded_by=entity.uploaded_by,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def create(self, evidence: Evidence) -> Evidence:
        """Create a new evidence record."""
        model = self._entity_to_model(evidence)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._model_to_entity(model)

    async def get_by_id(self, evidence_id: UUID) -> Evidence | None:
        """Get evidence by ID."""
        stmt = select(EvidenceModel).where(EvidenceModel.id == evidence_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def get_by_training_session(
        self,
        training_session_id: UUID,
    ) -> list[Evidence]:
        """Get all evidences for a training session."""
        stmt = (
            select(EvidenceModel)
            .where(EvidenceModel.training_session_id == training_session_id)
            .order_by(EvidenceModel.created_at.desc())
        )

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    async def update(self, evidence: Evidence) -> Evidence:
        """Update evidence."""
        stmt = select(EvidenceModel).where(EvidenceModel.id == evidence.id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            model.description = evidence.description
            model.updated_at = evidence.updated_at
            await self._session.flush()
            await self._session.refresh(model)
            return self._model_to_entity(model)

        raise ValueError(f"Evidence with id {evidence.id} not found")

    async def delete(self, evidence_id: UUID) -> bool:
        """Delete evidence."""
        stmt = select(EvidenceModel).where(EvidenceModel.id == evidence_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False

    async def delete_by_training_session(self, training_session_id: UUID) -> int:
        """Delete all evidences for a training session."""
        stmt = delete(EvidenceModel).where(EvidenceModel.training_session_id == training_session_id)
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.rowcount  # type: ignore[attr-defined, no-any-return]

    async def count_by_training_session(self, training_session_id: UUID) -> int:
        """Count evidences for a training session."""
        stmt = select(func.count(EvidenceModel.id)).where(
            EvidenceModel.training_session_id == training_session_id
        )
        result = await self._session.execute(stmt)
        return result.scalar() or 0
