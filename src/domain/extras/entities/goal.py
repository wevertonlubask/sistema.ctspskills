"""Goal and Milestone entities."""

from datetime import date, datetime
from uuid import UUID, uuid4

from src.shared.constants.enums import GoalPriority, GoalStatus
from src.shared.domain.aggregate_root import AggregateRoot
from src.shared.domain.entity import Entity


class Milestone(Entity[UUID]):
    """Milestone entity for goal tracking."""

    def __init__(
        self,
        goal_id: UUID,
        title: str,
        target_value: float,
        current_value: float = 0.0,
        due_date: date | None = None,
        is_completed: bool = False,
        completed_at: datetime | None = None,
        id: UUID | None = None,
    ) -> None:
        super().__init__(id=id or uuid4())
        self._goal_id = goal_id
        self._title = title
        self._target_value = target_value
        self._current_value = current_value
        self._due_date = due_date
        self._is_completed = is_completed
        self._completed_at = completed_at

    @property
    def goal_id(self) -> UUID:
        return self._goal_id

    @property
    def title(self) -> str:
        return self._title

    @property
    def target_value(self) -> float:
        return self._target_value

    @property
    def current_value(self) -> float:
        return self._current_value

    @property
    def due_date(self) -> date | None:
        return self._due_date

    @property
    def is_completed(self) -> bool:
        return self._is_completed

    @property
    def completed_at(self) -> datetime | None:
        return self._completed_at

    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage."""
        if self._target_value == 0:
            return 100.0 if self._is_completed else 0.0
        return min(100.0, (self._current_value / self._target_value) * 100)

    @property
    def is_overdue(self) -> bool:
        """Check if milestone is overdue."""
        if self._is_completed or self._due_date is None:
            return False
        return date.today() > self._due_date

    def update_progress(self, value: float) -> None:
        """Update current progress value."""
        self._current_value = value
        if self._current_value >= self._target_value:
            self.complete()

    def complete(self) -> None:
        """Mark milestone as completed."""
        self._is_completed = True
        self._completed_at = datetime.utcnow()


class Goal(AggregateRoot[UUID]):
    """Goal entity for tracking objectives (RN10)."""

    def __init__(
        self,
        title: str,
        competitor_id: UUID,
        created_by: UUID,
        description: str | None = None,
        target_value: float = 100.0,
        current_value: float = 0.0,
        unit: str = "percent",
        priority: GoalPriority = GoalPriority.MEDIUM,
        status: GoalStatus = GoalStatus.NOT_STARTED,
        start_date: date | None = None,
        due_date: date | None = None,
        modality_id: UUID | None = None,
        competence_id: UUID | None = None,
        id: UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        super().__init__(id=id or uuid4())
        self._title = title
        self._description = description
        self._competitor_id = competitor_id
        self._target_value = target_value
        self._current_value = current_value
        self._unit = unit
        self._priority = priority
        self._status = status
        self._start_date = start_date or date.today()
        self._due_date = due_date
        self._modality_id = modality_id
        self._competence_id = competence_id
        self._created_by = created_by
        self._created_at = created_at or datetime.utcnow()
        self._updated_at = updated_at or datetime.utcnow()
        self._milestones: list[Milestone] = []

    @property
    def title(self) -> str:
        return self._title

    @property
    def description(self) -> str | None:
        return self._description

    @property
    def competitor_id(self) -> UUID:
        return self._competitor_id

    @property
    def target_value(self) -> float:
        return self._target_value

    @property
    def current_value(self) -> float:
        return self._current_value

    @property
    def unit(self) -> str:
        return self._unit

    @property
    def priority(self) -> GoalPriority:
        return self._priority

    @property
    def status(self) -> GoalStatus:
        return self._status

    @property
    def start_date(self) -> date:
        return self._start_date

    @property
    def due_date(self) -> date | None:
        return self._due_date

    @property
    def modality_id(self) -> UUID | None:
        return self._modality_id

    @property
    def competence_id(self) -> UUID | None:
        return self._competence_id

    @property
    def created_by(self) -> UUID:
        return self._created_by

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    @property
    def milestones(self) -> list[Milestone]:
        return self._milestones.copy()

    @property
    def progress_percentage(self) -> float:
        """Calculate goal progress percentage."""
        if self._target_value == 0:
            return 100.0 if self._status == GoalStatus.COMPLETED else 0.0
        return min(100.0, round((self._current_value / self._target_value) * 100, 2))

    @property
    def is_overdue(self) -> bool:
        """Check if goal is overdue (RN10 - automatic alerts)."""
        if self._status == GoalStatus.COMPLETED:
            return False
        if self._due_date is None:
            return False
        return date.today() > self._due_date

    @property
    def days_remaining(self) -> int | None:
        """Get days remaining until due date."""
        if self._due_date is None:
            return None
        delta = self._due_date - date.today()
        return delta.days

    @property
    def completed_milestones(self) -> int:
        """Count completed milestones."""
        return sum(1 for m in self._milestones if m.is_completed)

    def update(
        self,
        title: str | None = None,
        description: str | None = None,
        target_value: float | None = None,
        priority: GoalPriority | None = None,
        due_date: date | None = None,
    ) -> None:
        """Update goal details."""
        if title is not None:
            self._title = title
        if description is not None:
            self._description = description
        if target_value is not None:
            self._target_value = target_value
        if priority is not None:
            self._priority = priority
        if due_date is not None:
            self._due_date = due_date
        self._updated_at = datetime.utcnow()

    def update_progress(self, value: float) -> None:
        """Update current progress value."""
        self._current_value = value
        self._updated_at = datetime.utcnow()

        # Update status based on progress
        if self._current_value >= self._target_value:
            self._status = GoalStatus.COMPLETED
        elif self._current_value > 0:
            self._status = GoalStatus.IN_PROGRESS

        # Check for overdue
        if self.is_overdue and self._status != GoalStatus.COMPLETED:
            self._status = GoalStatus.OVERDUE

    def start(self) -> None:
        """Start working on the goal."""
        self._status = GoalStatus.IN_PROGRESS
        self._updated_at = datetime.utcnow()

    def complete(self) -> None:
        """Mark goal as completed."""
        self._status = GoalStatus.COMPLETED
        self._current_value = self._target_value
        self._updated_at = datetime.utcnow()

    def cancel(self) -> None:
        """Cancel the goal."""
        self._status = GoalStatus.CANCELLED
        self._updated_at = datetime.utcnow()

    def add_milestone(self, milestone: Milestone) -> None:
        """Add a milestone to the goal."""
        self._milestones.append(milestone)
        self._updated_at = datetime.utcnow()

    def remove_milestone(self, milestone_id: UUID) -> bool:
        """Remove a milestone from the goal."""
        for i, m in enumerate(self._milestones):
            if m.id == milestone_id:
                self._milestones.pop(i)
                self._updated_at = datetime.utcnow()
                return True
        return False

    def needs_alert(self, days_threshold: int = 7) -> bool:
        """Check if goal needs an alert (RN10).

        Returns True if:
        - Goal is overdue
        - Goal is approaching deadline (within threshold days)
        - Progress is significantly behind schedule
        """
        if self._status == GoalStatus.COMPLETED:
            return False

        # Already overdue
        if self.is_overdue:
            return True

        # Approaching deadline
        if self._due_date and self.days_remaining is not None:
            if self.days_remaining <= days_threshold:
                return True

        # Behind schedule (less than 50% progress with less than 50% time remaining)
        if self._due_date:
            total_days = (self._due_date - self._start_date).days
            if total_days > 0:
                elapsed_days = (date.today() - self._start_date).days
                time_progress = elapsed_days / total_days
                if time_progress > 0.5 and self.progress_percentage < 50:
                    return True

        return False
