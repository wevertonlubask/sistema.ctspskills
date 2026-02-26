"""SQLAlchemy Grade Audit Log repository implementation."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.assessment.entities.grade_audit_log import GradeAuditLog
from src.domain.assessment.repositories.grade_audit_repository import (
    GradeAuditLogRepository,
)
from src.infrastructure.database.models.assessment_model import GradeAuditLogModel


class SQLAlchemyGradeAuditLogRepository(GradeAuditLogRepository):
    """SQLAlchemy implementation of GradeAuditLogRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _model_to_entity(self, model: GradeAuditLogModel) -> GradeAuditLog:
        """Convert GradeAuditLogModel to GradeAuditLog entity."""
        return GradeAuditLog(
            id=model.id,
            grade_id=model.grade_id,
            action=model.action,
            old_score=model.old_score,
            new_score=model.new_score,
            old_notes=model.old_notes,
            new_notes=model.new_notes,
            changed_by=model.changed_by,
            ip_address=model.ip_address,
            user_agent=model.user_agent,
            changed_at=model.changed_at,
        )

    def _entity_to_model(self, entity: GradeAuditLog) -> GradeAuditLogModel:
        """Convert GradeAuditLog entity to GradeAuditLogModel."""
        return GradeAuditLogModel(
            id=entity.id,
            grade_id=entity.grade_id,
            action=entity.action,
            old_score=entity.old_score,
            new_score=entity.new_score,
            old_notes=entity.old_notes,
            new_notes=entity.new_notes,
            changed_by=entity.changed_by,
            ip_address=entity.ip_address,
            user_agent=entity.user_agent,
            changed_at=entity.changed_at,
        )

    async def get_by_id(self, audit_id: UUID) -> GradeAuditLog | None:
        """Get audit log by ID."""
        stmt = select(GradeAuditLogModel).where(GradeAuditLogModel.id == audit_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def add(self, audit_log: GradeAuditLog) -> GradeAuditLog:
        """Add a new audit log entry."""
        model = self._entity_to_model(audit_log)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._model_to_entity(model)

    async def get_by_grade(
        self,
        grade_id: UUID,
        limit: int = 50,
    ) -> list[GradeAuditLog]:
        """Get audit history for a grade."""
        stmt = (
            select(GradeAuditLogModel)
            .where(GradeAuditLogModel.grade_id == grade_id)
            .order_by(GradeAuditLogModel.changed_at.desc())
            .limit(limit)
        )

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    async def get_by_user(
        self,
        user_id: UUID,
        limit: int = 100,
    ) -> list[GradeAuditLog]:
        """Get audit logs for changes made by a user."""
        stmt = (
            select(GradeAuditLogModel)
            .where(GradeAuditLogModel.changed_by == user_id)
            .order_by(GradeAuditLogModel.changed_at.desc())
            .limit(limit)
        )

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    async def get_grade_history(
        self,
        grade_id: UUID,
    ) -> list[GradeAuditLog]:
        """Get complete history for a grade."""
        stmt = (
            select(GradeAuditLogModel)
            .where(GradeAuditLogModel.grade_id == grade_id)
            .order_by(GradeAuditLogModel.changed_at.asc())
        )

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    async def count_by_grade(self, grade_id: UUID) -> int:
        """Count audit entries for a grade."""
        stmt = select(func.count(GradeAuditLogModel.id)).where(
            GradeAuditLogModel.grade_id == grade_id
        )
        result = await self._session.execute(stmt)
        return result.scalar() or 0
