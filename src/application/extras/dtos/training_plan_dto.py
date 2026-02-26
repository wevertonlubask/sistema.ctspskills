"""Training Plan DTOs."""

from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID

from src.domain.extras.entities.training_plan import PlanItem, TrainingPlan
from src.shared.constants.enums import GoalPriority


@dataclass
class CreatePlanItemDTO:
    """DTO for creating a plan item."""

    title: str
    description: str | None = None
    competence_id: UUID | None = None
    duration_hours: float = 1.0
    is_required: bool = True
    due_date: date | None = None
    notes: str | None = None
    resource_ids: list[UUID] | None = None


@dataclass
class PlanItemDTO:
    """DTO for plan item responses."""

    id: UUID
    plan_id: UUID
    title: str
    description: str | None
    competence_id: UUID | None
    order: int
    duration_hours: float
    is_required: bool
    is_completed: bool
    completed_at: datetime | None
    due_date: date | None
    notes: str | None
    resource_ids: list[UUID]
    is_overdue: bool

    @classmethod
    def from_entity(cls, entity: PlanItem) -> "PlanItemDTO":
        return cls(
            id=entity.id,
            plan_id=entity.plan_id,
            title=entity.title,
            description=entity.description,
            competence_id=entity.competence_id,
            order=entity.order,
            duration_hours=entity.duration_hours,
            is_required=entity.is_required,
            is_completed=entity.is_completed,
            completed_at=entity.completed_at,
            due_date=entity.due_date,
            notes=entity.notes,
            resource_ids=entity.resource_ids,
            is_overdue=entity.is_overdue,
        )


@dataclass
class CreatePlanDTO:
    """DTO for creating a training plan."""

    title: str
    competitor_id: UUID
    description: str | None = None
    modality_id: UUID | None = None
    priority: GoalPriority = GoalPriority.MEDIUM
    start_date: date | None = None
    end_date: date | None = None
    target_hours: float = 0.0
    items: list[CreatePlanItemDTO] | None = None


@dataclass
class UpdatePlanDTO:
    """DTO for updating a training plan."""

    title: str | None = None
    description: str | None = None
    priority: GoalPriority | None = None
    start_date: date | None = None
    end_date: date | None = None
    target_hours: float | None = None


@dataclass
class TrainingPlanDTO:
    """DTO for training plan responses."""

    id: UUID
    title: str
    description: str | None
    competitor_id: UUID
    modality_id: UUID | None
    status: str
    priority: str
    start_date: date | None
    end_date: date | None
    target_hours: float
    is_suggested: bool
    total_hours: float
    completed_hours: float
    progress_percentage: float
    required_items_completed: bool
    is_overdue: bool
    items: list[PlanItemDTO]
    overdue_items_count: int
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, entity: TrainingPlan) -> "TrainingPlanDTO":
        return cls(
            id=entity.id,
            title=entity.title,
            description=entity.description,
            competitor_id=entity.competitor_id,
            modality_id=entity.modality_id,
            status=entity.status.value,
            priority=entity.priority.value,
            start_date=entity.start_date,
            end_date=entity.end_date,
            target_hours=entity.target_hours,
            is_suggested=entity.is_suggested,
            total_hours=entity.total_hours,
            completed_hours=entity.completed_hours,
            progress_percentage=entity.progress_percentage,
            required_items_completed=entity.required_items_completed,
            is_overdue=entity.is_overdue,
            items=[PlanItemDTO.from_entity(item) for item in entity.items],
            overdue_items_count=len(entity.get_overdue_items()),
            created_by=entity.created_by,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )


@dataclass
class TrainingPlanListDTO:
    """DTO for training plan list."""

    plans: list[TrainingPlanDTO]
    total: int
    active_count: int
