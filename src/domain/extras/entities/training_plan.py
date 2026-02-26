"""Training Plan entities."""

from datetime import date, datetime
from uuid import UUID, uuid4

from src.shared.constants.enums import GoalPriority, TrainingPlanStatus
from src.shared.domain.aggregate_root import AggregateRoot
from src.shared.domain.entity import Entity


class PlanItem(Entity[UUID]):
    """Individual item in a training plan."""

    def __init__(
        self,
        plan_id: UUID,
        title: str,
        description: str | None = None,
        competence_id: UUID | None = None,
        order: int = 0,
        duration_hours: float = 1.0,
        is_required: bool = True,
        is_completed: bool = False,
        completed_at: datetime | None = None,
        due_date: date | None = None,
        notes: str | None = None,
        resource_ids: list[UUID] | None = None,
        id: UUID | None = None,
    ) -> None:
        super().__init__(id=id or uuid4())
        self._plan_id = plan_id
        self._title = title
        self._description = description
        self._competence_id = competence_id
        self._order = order
        self._duration_hours = duration_hours
        self._is_required = is_required
        self._is_completed = is_completed
        self._completed_at = completed_at
        self._due_date = due_date
        self._notes = notes
        self._resource_ids = resource_ids or []

    @property
    def plan_id(self) -> UUID:
        return self._plan_id

    @property
    def title(self) -> str:
        return self._title

    @property
    def description(self) -> str | None:
        return self._description

    @property
    def competence_id(self) -> UUID | None:
        return self._competence_id

    @property
    def order(self) -> int:
        return self._order

    @property
    def duration_hours(self) -> float:
        return self._duration_hours

    @property
    def is_required(self) -> bool:
        return self._is_required

    @property
    def is_completed(self) -> bool:
        return self._is_completed

    @property
    def completed_at(self) -> datetime | None:
        return self._completed_at

    @property
    def due_date(self) -> date | None:
        return self._due_date

    @property
    def notes(self) -> str | None:
        return self._notes

    @property
    def resource_ids(self) -> list[UUID]:
        return self._resource_ids.copy()

    @property
    def is_overdue(self) -> bool:
        """Check if item is overdue."""
        if self._is_completed or self._due_date is None:
            return False
        return date.today() > self._due_date

    def complete(self) -> None:
        """Mark item as completed."""
        self._is_completed = True
        self._completed_at = datetime.utcnow()

    def uncomplete(self) -> None:
        """Mark item as not completed."""
        self._is_completed = False
        self._completed_at = None

    def add_resource(self, resource_id: UUID) -> bool:
        """Add a resource to the item."""
        if resource_id not in self._resource_ids:
            self._resource_ids.append(resource_id)
            return True
        return False

    def remove_resource(self, resource_id: UUID) -> bool:
        """Remove a resource from the item."""
        if resource_id in self._resource_ids:
            self._resource_ids.remove(resource_id)
            return True
        return False

    def update(
        self,
        title: str | None = None,
        description: str | None = None,
        duration_hours: float | None = None,
        due_date: date | None = None,
        notes: str | None = None,
    ) -> None:
        """Update item details."""
        if title is not None:
            self._title = title
        if description is not None:
            self._description = description
        if duration_hours is not None:
            self._duration_hours = duration_hours
        if due_date is not None:
            self._due_date = due_date
        if notes is not None:
            self._notes = notes


class TrainingPlan(AggregateRoot[UUID]):
    """Training plan entity with personalized suggestions."""

    def __init__(
        self,
        title: str,
        competitor_id: UUID,
        created_by: UUID,
        description: str | None = None,
        modality_id: UUID | None = None,
        status: TrainingPlanStatus = TrainingPlanStatus.DRAFT,
        priority: GoalPriority = GoalPriority.MEDIUM,
        start_date: date | None = None,
        end_date: date | None = None,
        target_hours: float = 0.0,
        is_suggested: bool = False,
        id: UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        super().__init__(id=id or uuid4())
        self._title = title
        self._description = description
        self._competitor_id = competitor_id
        self._modality_id = modality_id
        self._status = status
        self._priority = priority
        self._start_date = start_date
        self._end_date = end_date
        self._target_hours = target_hours
        self._is_suggested = is_suggested
        self._created_by = created_by
        self._created_at = created_at or datetime.utcnow()
        self._updated_at = updated_at or datetime.utcnow()
        self._items: list[PlanItem] = []

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
    def modality_id(self) -> UUID | None:
        return self._modality_id

    @property
    def status(self) -> TrainingPlanStatus:
        return self._status

    @property
    def priority(self) -> GoalPriority:
        return self._priority

    @property
    def start_date(self) -> date | None:
        return self._start_date

    @property
    def end_date(self) -> date | None:
        return self._end_date

    @property
    def target_hours(self) -> float:
        return self._target_hours

    @property
    def is_suggested(self) -> bool:
        return self._is_suggested

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
    def items(self) -> list[PlanItem]:
        return sorted(self._items, key=lambda x: x.order)

    @property
    def total_hours(self) -> float:
        """Calculate total hours from all items."""
        return sum(item.duration_hours for item in self._items)

    @property
    def completed_hours(self) -> float:
        """Calculate completed hours."""
        return sum(item.duration_hours for item in self._items if item.is_completed)

    @property
    def progress_percentage(self) -> float:
        """Calculate plan progress percentage."""
        if not self._items:
            return 0.0
        completed = sum(1 for item in self._items if item.is_completed)
        return round((completed / len(self._items)) * 100, 2)

    @property
    def required_items_completed(self) -> bool:
        """Check if all required items are completed."""
        required = [item for item in self._items if item.is_required]
        if not required:
            return True
        return all(item.is_completed for item in required)

    @property
    def is_overdue(self) -> bool:
        """Check if plan is overdue."""
        if self._status == TrainingPlanStatus.COMPLETED:
            return False
        if self._end_date is None:
            return False
        return date.today() > self._end_date

    def update(
        self,
        title: str | None = None,
        description: str | None = None,
        priority: GoalPriority | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        target_hours: float | None = None,
    ) -> None:
        """Update plan details."""
        if title is not None:
            self._title = title
        if description is not None:
            self._description = description
        if priority is not None:
            self._priority = priority
        if start_date is not None:
            self._start_date = start_date
        if end_date is not None:
            self._end_date = end_date
        if target_hours is not None:
            self._target_hours = target_hours
        self._updated_at = datetime.utcnow()

    def add_item(self, item: PlanItem) -> None:
        """Add an item to the plan."""
        if not item.order:
            item._order = len(self._items) + 1
        self._items.append(item)
        self._updated_at = datetime.utcnow()

    def remove_item(self, item_id: UUID) -> bool:
        """Remove an item from the plan."""
        for i, item in enumerate(self._items):
            if item.id == item_id:
                self._items.pop(i)
                self._updated_at = datetime.utcnow()
                return True
        return False

    def reorder_items(self, item_ids: list[UUID]) -> None:
        """Reorder items based on provided ID list."""
        id_to_item = {item.id: item for item in self._items}
        new_order = []
        for i, item_id in enumerate(item_ids):
            if item_id in id_to_item:
                item = id_to_item[item_id]
                item._order = i + 1
                new_order.append(item)
        self._items = new_order
        self._updated_at = datetime.utcnow()

    def activate(self) -> None:
        """Activate the plan."""
        self._status = TrainingPlanStatus.ACTIVE
        if self._start_date is None:
            self._start_date = date.today()
        self._updated_at = datetime.utcnow()

    def complete(self) -> None:
        """Mark plan as completed."""
        self._status = TrainingPlanStatus.COMPLETED
        self._updated_at = datetime.utcnow()

    def archive(self) -> None:
        """Archive the plan."""
        self._status = TrainingPlanStatus.ARCHIVED
        self._updated_at = datetime.utcnow()

    def get_next_item(self) -> PlanItem | None:
        """Get the next incomplete item."""
        for item in self.items:
            if not item.is_completed:
                return item
        return None

    def get_overdue_items(self) -> list[PlanItem]:
        """Get all overdue items."""
        return [item for item in self._items if item.is_overdue]

    @classmethod
    def create_suggested_plan(
        cls,
        title: str,
        competitor_id: UUID,
        created_by: UUID,
        modality_id: UUID,
        description: str | None = None,
    ) -> "TrainingPlan":
        """Create a suggested training plan."""
        return cls(
            title=title,
            competitor_id=competitor_id,
            created_by=created_by,
            modality_id=modality_id,
            description=description,
            is_suggested=True,
            status=TrainingPlanStatus.DRAFT,
        )
