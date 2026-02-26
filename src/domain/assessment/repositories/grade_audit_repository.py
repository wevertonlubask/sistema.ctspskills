"""Grade audit log repository interface."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.assessment.entities.grade_audit_log import GradeAuditLog


class GradeAuditLogRepository(ABC):
    """Abstract repository interface for GradeAuditLog entity."""

    @abstractmethod
    async def get_by_id(self, audit_id: UUID) -> GradeAuditLog | None:
        """Get audit log by ID.

        Args:
            audit_id: Audit log UUID.

        Returns:
            GradeAuditLog entity or None if not found.
        """
        ...

    @abstractmethod
    async def add(self, audit_log: GradeAuditLog) -> GradeAuditLog:
        """Add a new audit log entry.

        Args:
            audit_log: GradeAuditLog entity to add.

        Returns:
            Added audit log with generated ID.
        """
        ...

    @abstractmethod
    async def get_by_grade(
        self,
        grade_id: UUID,
        limit: int = 50,
    ) -> list[GradeAuditLog]:
        """Get audit history for a grade.

        Args:
            grade_id: Grade UUID.
            limit: Maximum records to return.

        Returns:
            List of audit logs ordered by changed_at descending.
        """
        ...

    @abstractmethod
    async def get_by_user(
        self,
        user_id: UUID,
        limit: int = 100,
    ) -> list[GradeAuditLog]:
        """Get audit logs for changes made by a user.

        Args:
            user_id: User UUID who made the changes.
            limit: Maximum records to return.

        Returns:
            List of audit logs ordered by changed_at descending.
        """
        ...

    @abstractmethod
    async def get_grade_history(
        self,
        grade_id: UUID,
    ) -> list[GradeAuditLog]:
        """Get complete history for a grade.

        Args:
            grade_id: Grade UUID.

        Returns:
            Complete list of audit logs for the grade.
        """
        ...

    @abstractmethod
    async def count_by_grade(self, grade_id: UUID) -> int:
        """Count audit entries for a grade.

        Args:
            grade_id: Grade UUID.

        Returns:
            Number of audit entries.
        """
        ...
