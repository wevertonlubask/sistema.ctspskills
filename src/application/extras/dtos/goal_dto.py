"""Goal DTOs."""

from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID

from src.domain.extras.entities.goal import Goal, Milestone
from src.shared.constants.enums import GoalPriority


@dataclass
class CreateMilestoneDTO:
    """DTO for creating a milestone."""

    title: str
    target_value: float
    due_date: date | None = None


@dataclass
class MilestoneDTO:
    """DTO for milestone responses."""

    id: UUID
    goal_id: UUID
    title: str
    target_value: float
    current_value: float
    due_date: date | None
    is_completed: bool
    completed_at: datetime | None
    progress_percentage: float
    is_overdue: bool

    @classmethod
    def from_entity(cls, entity: Milestone) -> "MilestoneDTO":
        return cls(
            id=entity.id,
            goal_id=entity.goal_id,
            title=entity.title,
            target_value=entity.target_value,
            current_value=entity.current_value,
            due_date=entity.due_date,
            is_completed=entity.is_completed,
            completed_at=entity.completed_at,
            progress_percentage=entity.progress_percentage,
            is_overdue=entity.is_overdue,
        )


@dataclass
class CreateGoalDTO:
    """DTO for creating a goal."""

    title: str
    competitor_id: UUID
    description: str | None = None
    target_value: float = 100.0
    unit: str = "percent"
    priority: GoalPriority = GoalPriority.MEDIUM
    start_date: date | None = None
    due_date: date | None = None
    modality_id: UUID | None = None
    competence_id: UUID | None = None
    milestones: list[CreateMilestoneDTO] | None = None


@dataclass
class UpdateGoalDTO:
    """DTO for updating a goal."""

    title: str | None = None
    description: str | None = None
    target_value: float | None = None
    priority: GoalPriority | None = None
    due_date: date | None = None


@dataclass
class GoalDTO:
    """DTO for goal responses."""

    id: UUID
    title: str
    description: str | None
    competitor_id: UUID
    target_value: float
    current_value: float
    unit: str
    priority: str
    status: str
    start_date: date
    due_date: date | None
    modality_id: UUID | None
    competence_id: UUID | None
    progress_percentage: float
    is_overdue: bool
    days_remaining: int | None
    needs_alert: bool
    milestones: list[MilestoneDTO]
    completed_milestones: int
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, entity: Goal) -> "GoalDTO":
        return cls(
            id=entity.id,
            title=entity.title,
            description=entity.description,
            competitor_id=entity.competitor_id,
            target_value=entity.target_value,
            current_value=entity.current_value,
            unit=entity.unit,
            priority=entity.priority.value,
            status=entity.status.value,
            start_date=entity.start_date,
            due_date=entity.due_date,
            modality_id=entity.modality_id,
            competence_id=entity.competence_id,
            progress_percentage=entity.progress_percentage,
            is_overdue=entity.is_overdue,
            days_remaining=entity.days_remaining,
            needs_alert=entity.needs_alert(),
            milestones=[MilestoneDTO.from_entity(m) for m in entity.milestones],
            completed_milestones=entity.completed_milestones,
            created_by=entity.created_by,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )


@dataclass
class GoalListDTO:
    """DTO for goal list."""

    goals: list[GoalDTO]
    total: int
    overdue_count: int
