"""Unit tests for Extra features entities."""

from datetime import date, datetime, timedelta
from uuid import uuid4

import pytest

from src.domain.extras.entities.badge import Badge, UserPoints
from src.domain.extras.entities.event import Event
from src.domain.extras.entities.feedback import Feedback
from src.domain.extras.entities.goal import Goal, Milestone
from src.domain.extras.entities.message import Conversation
from src.domain.extras.entities.notification import Notification
from src.domain.extras.entities.resource import Resource
from src.domain.extras.entities.training_plan import PlanItem, TrainingPlan
from src.shared.constants.enums import (
    BadgeCategory,
    BadgeRarity,
    EventStatus,
    EventType,
    FeedbackType,
    GoalStatus,
    NotificationStatus,
    NotificationType,
    ResourceAccessLevel,
    ResourceType,
    TrainingPlanStatus,
)


class TestNotification:
    """Tests for Notification entity."""

    def test_create_notification(self):
        """Test creating a notification."""
        user_id = uuid4()
        notification = Notification(
            user_id=user_id,
            title="Test Notification",
            message="This is a test message",
        )

        assert notification.user_id == user_id
        assert notification.title == "Test Notification"
        assert notification.notification_type == NotificationType.INFO
        assert notification.status == NotificationStatus.PENDING
        assert not notification.is_read

    def test_mark_as_sent(self):
        """Test marking notification as sent."""
        notification = Notification(
            user_id=uuid4(),
            title="Test",
            message="Test",
        )

        notification.mark_as_sent()

        assert notification.status == NotificationStatus.SENT
        assert notification.sent_at is not None

    def test_mark_as_read(self):
        """Test marking notification as read."""
        notification = Notification(
            user_id=uuid4(),
            title="Test",
            message="Test",
        )

        notification.mark_as_read()

        assert notification.is_read
        assert notification.read_at is not None
        assert notification.status == NotificationStatus.READ

    def test_create_alert(self):
        """Test creating alert notification."""
        notification = Notification.create_alert(
            user_id=uuid4(),
            title="Alert",
            message="This is an alert",
        )

        assert notification.notification_type == NotificationType.ALERT


class TestEvent:
    """Tests for Event entity."""

    @pytest.fixture
    def valid_event(self):
        """Create a valid event."""
        now = datetime.utcnow()
        return Event(
            title="Test Event",
            start_datetime=now + timedelta(days=1),
            end_datetime=now + timedelta(days=1, hours=2),
            created_by=uuid4(),
        )

    def test_create_event(self, valid_event):
        """Test creating an event."""
        assert valid_event.title == "Test Event"
        assert valid_event.status == EventStatus.SCHEDULED
        assert valid_event.event_type == EventType.OTHER

    def test_event_duration(self, valid_event):
        """Test event duration calculation."""
        assert valid_event.duration_minutes == 120  # 2 hours

    def test_add_participant(self, valid_event):
        """Test adding participant."""
        user_id = uuid4()
        result = valid_event.add_participant(user_id)

        assert result is True
        assert user_id in valid_event.participants

    def test_add_duplicate_participant(self, valid_event):
        """Test adding duplicate participant."""
        user_id = uuid4()
        valid_event.add_participant(user_id)
        result = valid_event.add_participant(user_id)

        assert result is False

    def test_event_cancel(self, valid_event):
        """Test canceling event."""
        valid_event.cancel()

        assert valid_event.status == EventStatus.CANCELLED

    def test_event_is_upcoming(self, valid_event):
        """Test checking if event is upcoming."""
        assert valid_event.is_upcoming() is True


class TestResource:
    """Tests for Resource entity."""

    def test_create_resource(self):
        """Test creating a resource."""
        resource = Resource(
            title="Test Resource",
            resource_type=ResourceType.PDF,
            created_by=uuid4(),
            description="Test description",
        )

        assert resource.title == "Test Resource"
        assert resource.resource_type == ResourceType.PDF
        assert resource.is_active

    def test_add_tag(self):
        """Test adding tags."""
        resource = Resource(
            title="Test",
            resource_type=ResourceType.LINK,
            created_by=uuid4(),
        )

        result = resource.add_tag("python")
        assert result is True
        assert "python" in resource.tags

    def test_add_duplicate_tag(self):
        """Test adding duplicate tag."""
        resource = Resource(
            title="Test",
            resource_type=ResourceType.LINK,
            created_by=uuid4(),
        )

        resource.add_tag("python")
        result = resource.add_tag("python")
        assert result is False

    def test_can_access_public(self):
        """Test access to public resource."""
        resource = Resource(
            title="Test",
            resource_type=ResourceType.LINK,
            created_by=uuid4(),
            access_level=ResourceAccessLevel.PUBLIC,
        )

        assert resource.can_access(None, False) is True

    def test_can_access_modality(self):
        """Test access to modality-restricted resource."""
        modality_id = uuid4()
        resource = Resource(
            title="Test",
            resource_type=ResourceType.LINK,
            created_by=uuid4(),
            modality_id=modality_id,
            access_level=ResourceAccessLevel.MODALITY,
        )

        assert resource.can_access(modality_id, False) is True
        assert resource.can_access(uuid4(), False) is False
        assert resource.can_access(None, True) is True  # Admin


class TestGoal:
    """Tests for Goal entity."""

    @pytest.fixture
    def valid_goal(self):
        """Create a valid goal."""
        return Goal(
            title="Complete Training",
            competitor_id=uuid4(),
            created_by=uuid4(),
            target_value=100.0,
            due_date=date.today() + timedelta(days=30),
        )

    def test_create_goal(self, valid_goal):
        """Test creating a goal."""
        assert valid_goal.title == "Complete Training"
        assert valid_goal.status == GoalStatus.NOT_STARTED
        assert valid_goal.progress_percentage == 0.0

    def test_update_progress(self, valid_goal):
        """Test updating progress."""
        valid_goal.update_progress(50.0)

        assert valid_goal.current_value == 50.0
        assert valid_goal.progress_percentage == 50.0
        assert valid_goal.status == GoalStatus.IN_PROGRESS

    def test_complete_on_target(self, valid_goal):
        """Test automatic completion when target reached."""
        valid_goal.update_progress(100.0)

        assert valid_goal.status == GoalStatus.COMPLETED
        assert valid_goal.progress_percentage == 100.0

    def test_is_overdue(self):
        """Test overdue detection."""
        goal = Goal(
            title="Overdue Goal",
            competitor_id=uuid4(),
            created_by=uuid4(),
            due_date=date.today() - timedelta(days=1),
        )

        assert goal.is_overdue is True

    def test_days_remaining(self, valid_goal):
        """Test days remaining calculation."""
        assert valid_goal.days_remaining == 30

    def test_add_milestone(self, valid_goal):
        """Test adding milestone."""
        milestone = Milestone(
            goal_id=valid_goal.id,
            title="First Milestone",
            target_value=25.0,
        )

        valid_goal.add_milestone(milestone)

        assert len(valid_goal.milestones) == 1


class TestBadge:
    """Tests for Badge entity."""

    def test_create_badge(self):
        """Test creating a badge."""
        badge = Badge(
            name="First Steps",
            description="Complete your first training",
            category=BadgeCategory.TRAINING,
        )

        assert badge.name == "First Steps"
        assert badge.category == BadgeCategory.TRAINING
        assert badge.rarity == BadgeRarity.COMMON
        assert badge.points == 10

    def test_create_training_badge(self):
        """Test creating training badge."""
        badge = Badge.create_training_badge(
            name="50 Hours",
            description="Complete 50 hours of training",
            hours_required=50,
        )

        assert badge.category == BadgeCategory.TRAINING
        assert badge.criteria["hours_required"] == 50

    def test_create_performance_badge(self):
        """Test creating performance badge."""
        badge = Badge.create_performance_badge(
            name="High Achiever",
            description="Achieve 90% average",
            score_required=90.0,
        )

        assert badge.category == BadgeCategory.PERFORMANCE
        assert badge.criteria["score_required"] == 90.0


class TestUserPoints:
    """Tests for UserPoints entity."""

    def test_create_user_points(self):
        """Test creating user points."""
        points = UserPoints(user_id=uuid4())

        assert points.total_points == 0
        assert points.level == 1

    def test_add_points(self):
        """Test adding points."""
        points = UserPoints(user_id=uuid4())
        leveled_up = points.add_points(50)

        assert points.total_points == 50
        assert leveled_up is False

    def test_level_up(self):
        """Test leveling up."""
        points = UserPoints(user_id=uuid4())
        leveled_up = points.add_points(100)

        assert leveled_up is True
        assert points.level == 2


class TestConversation:
    """Tests for Conversation entity."""

    def test_create_conversation(self):
        """Test creating a conversation."""
        user1 = uuid4()
        user2 = uuid4()
        conv = Conversation(
            participant_1=user1,
            participant_2=user2,
        )

        assert user1 in conv.participants
        assert user2 in conv.participants
        assert conv.is_active

    def test_is_participant(self):
        """Test checking participant."""
        user1 = uuid4()
        user2 = uuid4()
        conv = Conversation(participant_1=user1, participant_2=user2)

        assert conv.is_participant(user1) is True
        assert conv.is_participant(uuid4()) is False

    def test_get_other_participant(self):
        """Test getting other participant."""
        user1 = uuid4()
        user2 = uuid4()
        conv = Conversation(participant_1=user1, participant_2=user2)

        assert conv.get_other_participant(user1) == user2
        assert conv.get_other_participant(user2) == user1

    def test_add_message_updates_unread(self):
        """Test that adding message updates unread count."""
        user1 = uuid4()
        user2 = uuid4()
        conv = Conversation(participant_1=user1, participant_2=user2)

        conv.add_message(user1)

        assert conv.get_unread_count(user2) == 1
        assert conv.get_unread_count(user1) == 0


class TestFeedback:
    """Tests for Feedback entity."""

    def test_create_feedback(self):
        """Test creating feedback."""
        feedback = Feedback(
            competitor_id=uuid4(),
            evaluator_id=uuid4(),
            content="Good progress!",
            feedback_type=FeedbackType.POSITIVE,
        )

        assert feedback.feedback_type == FeedbackType.POSITIVE
        assert feedback.is_read is False
        assert feedback.related_context == "general"

    def test_feedback_with_grade(self):
        """Test feedback with grade context."""
        feedback = Feedback(
            competitor_id=uuid4(),
            evaluator_id=uuid4(),
            content="Good work on this exam",
            grade_id=uuid4(),
        )

        assert feedback.related_context == "grade"

    def test_mark_as_read(self):
        """Test marking feedback as read."""
        feedback = Feedback(
            competitor_id=uuid4(),
            evaluator_id=uuid4(),
            content="Test",
        )

        feedback.mark_as_read()

        assert feedback.is_read is True
        assert feedback.read_at is not None

    def test_rating_validation(self):
        """Test rating validation."""
        feedback = Feedback(
            competitor_id=uuid4(),
            evaluator_id=uuid4(),
            content="Test",
            rating=10,  # Should be capped at 5
        )

        assert feedback.rating == 5


class TestTrainingPlan:
    """Tests for TrainingPlan entity."""

    @pytest.fixture
    def valid_plan(self):
        """Create a valid training plan."""
        return TrainingPlan(
            title="Weekly Training Plan",
            competitor_id=uuid4(),
            created_by=uuid4(),
            target_hours=20.0,
        )

    def test_create_plan(self, valid_plan):
        """Test creating a training plan."""
        assert valid_plan.title == "Weekly Training Plan"
        assert valid_plan.status == TrainingPlanStatus.DRAFT
        assert valid_plan.progress_percentage == 0.0

    def test_add_item(self, valid_plan):
        """Test adding item to plan."""
        item = PlanItem(
            plan_id=valid_plan.id,
            title="Practice Coding",
            duration_hours=2.0,
        )

        valid_plan.add_item(item)

        assert len(valid_plan.items) == 1
        assert valid_plan.total_hours == 2.0

    def test_progress_percentage(self, valid_plan):
        """Test progress calculation."""
        item1 = PlanItem(
            plan_id=valid_plan.id,
            title="Item 1",
            duration_hours=2.0,
        )
        item2 = PlanItem(
            plan_id=valid_plan.id,
            title="Item 2",
            duration_hours=2.0,
        )

        valid_plan.add_item(item1)
        valid_plan.add_item(item2)
        item1.complete()

        assert valid_plan.progress_percentage == 50.0

    def test_activate_plan(self, valid_plan):
        """Test activating plan."""
        valid_plan.activate()

        assert valid_plan.status == TrainingPlanStatus.ACTIVE
        assert valid_plan.start_date is not None

    def test_complete_plan(self, valid_plan):
        """Test completing plan."""
        valid_plan.complete()

        assert valid_plan.status == TrainingPlanStatus.COMPLETED

    def test_get_next_item(self, valid_plan):
        """Test getting next incomplete item."""
        item1 = PlanItem(plan_id=valid_plan.id, title="Item 1", duration_hours=1.0)
        item2 = PlanItem(plan_id=valid_plan.id, title="Item 2", duration_hours=1.0)

        valid_plan.add_item(item1)
        valid_plan.add_item(item2)
        item1.complete()

        next_item = valid_plan.get_next_item()
        assert next_item.title == "Item 2"


class TestPlanItem:
    """Tests for PlanItem entity."""

    def test_create_item(self):
        """Test creating plan item."""
        item = PlanItem(
            plan_id=uuid4(),
            title="Practice Activity",
            duration_hours=2.0,
        )

        assert item.title == "Practice Activity"
        assert item.is_completed is False
        assert item.is_required is True

    def test_complete_item(self):
        """Test completing item."""
        item = PlanItem(
            plan_id=uuid4(),
            title="Test",
            duration_hours=1.0,
        )

        item.complete()

        assert item.is_completed is True
        assert item.completed_at is not None

    def test_is_overdue(self):
        """Test overdue detection."""
        item = PlanItem(
            plan_id=uuid4(),
            title="Test",
            duration_hours=1.0,
            due_date=date.today() - timedelta(days=1),
        )

        assert item.is_overdue is True

    def test_add_resource(self):
        """Test adding resource to item."""
        item = PlanItem(
            plan_id=uuid4(),
            title="Test",
            duration_hours=1.0,
        )

        resource_id = uuid4()
        result = item.add_resource(resource_id)

        assert result is True
        assert resource_id in item.resource_ids
