"""Grade audit log entity for tracking grade changes."""

from datetime import datetime
from uuid import UUID

from src.shared.domain.entity import Entity
from src.shared.utils.date_utils import utc_now


class GradeAuditLog(Entity[UUID]):
    """Audit log entity for tracking grade modifications.

    Records all changes made to grades including who made the change,
    what was changed (old/new values), and when.
    """

    ACTION_CREATED = "created"
    ACTION_UPDATED = "updated"
    ACTION_DELETED = "deleted"

    def __init__(
        self,
        grade_id: UUID,
        action: str,
        changed_by: UUID,
        old_score: float | None = None,
        new_score: float | None = None,
        old_notes: str | None = None,
        new_notes: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        id: UUID | None = None,
        changed_at: datetime | None = None,
    ) -> None:
        """Initialize GradeAuditLog entity.

        Args:
            grade_id: ID of the grade being audited.
            action: Type of action (created, updated, deleted).
            changed_by: ID of the user who made the change.
            old_score: Previous score value (for updates).
            new_score: New score value (for creates/updates).
            old_notes: Previous notes (for updates).
            new_notes: New notes (for creates/updates).
            ip_address: IP address of the user (optional).
            user_agent: User agent string (optional).
            id: Optional ID (auto-generated if not provided).
            changed_at: Timestamp of the change.
        """
        super().__init__(
            id=id,
            created_at=changed_at or utc_now(),
            updated_at=changed_at or utc_now(),
        )
        self._grade_id = grade_id
        self._action = action
        self._changed_by = changed_by
        self._old_score = old_score
        self._new_score = new_score
        self._old_notes = old_notes
        self._new_notes = new_notes
        self._ip_address = ip_address
        self._user_agent = user_agent
        self._changed_at = changed_at or utc_now()

    @property
    def grade_id(self) -> UUID:
        """Get the audited grade ID."""
        return self._grade_id

    @property
    def action(self) -> str:
        """Get the action type."""
        return self._action

    @property
    def changed_by(self) -> UUID:
        """Get the ID of the user who made the change."""
        return self._changed_by

    @property
    def old_score(self) -> float | None:
        """Get the previous score value."""
        return self._old_score

    @property
    def new_score(self) -> float | None:
        """Get the new score value."""
        return self._new_score

    @property
    def old_notes(self) -> str | None:
        """Get the previous notes."""
        return self._old_notes

    @property
    def new_notes(self) -> str | None:
        """Get the new notes."""
        return self._new_notes

    @property
    def ip_address(self) -> str | None:
        """Get the IP address."""
        return self._ip_address

    @property
    def user_agent(self) -> str | None:
        """Get the user agent."""
        return self._user_agent

    @property
    def changed_at(self) -> datetime:
        """Get the timestamp of the change."""
        return self._changed_at

    @classmethod
    def create_for_new_grade(
        cls,
        grade_id: UUID,
        score: float,
        notes: str | None,
        created_by: UUID,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> "GradeAuditLog":
        """Factory method to create audit log for a new grade.

        Args:
            grade_id: ID of the newly created grade.
            score: Initial score value.
            notes: Initial notes.
            created_by: ID of the user who created the grade.
            ip_address: Optional IP address.
            user_agent: Optional user agent.

        Returns:
            New GradeAuditLog instance.
        """
        return cls(
            grade_id=grade_id,
            action=cls.ACTION_CREATED,
            changed_by=created_by,
            old_score=None,
            new_score=score,
            old_notes=None,
            new_notes=notes,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    @classmethod
    def create_for_update(
        cls,
        grade_id: UUID,
        old_score: float | None,
        new_score: float | None,
        old_notes: str | None,
        new_notes: str | None,
        updated_by: UUID,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> "GradeAuditLog":
        """Factory method to create audit log for a grade update.

        Args:
            grade_id: ID of the updated grade.
            old_score: Previous score value.
            new_score: New score value.
            old_notes: Previous notes.
            new_notes: New notes.
            updated_by: ID of the user who made the update.
            ip_address: Optional IP address.
            user_agent: Optional user agent.

        Returns:
            New GradeAuditLog instance.
        """
        return cls(
            grade_id=grade_id,
            action=cls.ACTION_UPDATED,
            changed_by=updated_by,
            old_score=old_score,
            new_score=new_score,
            old_notes=old_notes,
            new_notes=new_notes,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    def __repr__(self) -> str:
        return (
            f"GradeAuditLog(id={self._id}, grade_id={self._grade_id}, "
            f"action={self._action}, changed_by={self._changed_by})"
        )
