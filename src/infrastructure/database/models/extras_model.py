"""SQLAlchemy models for extra features."""

from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    Text,
    Time,
)
from sqlalchemy.orm import relationship

from src.infrastructure.database.base import GUID, Base

# =============================================================================
# Association Tables
# =============================================================================

event_participants = Table(
    "event_participants",
    Base.metadata,
    Column("event_id", GUID, ForeignKey("events.id"), primary_key=True),
    Column("user_id", GUID, ForeignKey("users.id"), primary_key=True),
)

plan_item_resources = Table(
    "plan_item_resources",
    Base.metadata,
    Column("plan_item_id", GUID, ForeignKey("plan_items.id"), primary_key=True),
    Column("resource_id", GUID, ForeignKey("resources.id"), primary_key=True),
)


# =============================================================================
# Notification Model
# =============================================================================


class NotificationModel(Base):
    """SQLAlchemy model for notifications."""

    __tablename__ = "notifications"

    id = Column(GUID, primary_key=True)
    user_id = Column(GUID, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(20), nullable=False, default="info")
    channel = Column(String(20), nullable=False, default="in_app")
    status = Column(String(20), nullable=False, default="pending")
    related_entity_type = Column(String(50), nullable=True)
    related_entity_id = Column(GUID, nullable=True)
    action_url = Column(String(500), nullable=True)
    read_at = Column(DateTime, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    user = relationship("UserModel", back_populates="notifications")

    __table_args__ = (
        Index("ix_notifications_user_status", "user_id", "status"),
        Index("ix_notifications_user_created", "user_id", "created_at"),
    )


# =============================================================================
# Event and Schedule Models
# =============================================================================


class EventModel(Base):
    """SQLAlchemy model for events."""

    __tablename__ = "events"

    id = Column(GUID, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    event_type = Column(String(20), nullable=False, default="other")
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=False)
    location = Column(String(500), nullable=True)
    modality_id = Column(GUID, ForeignKey("modalities.id", ondelete="SET NULL"), nullable=True)
    is_all_day = Column(Boolean, default=False)
    status = Column(String(20), nullable=False, default="scheduled")
    recurrence_rule = Column(String(255), nullable=True)
    reminder_minutes = Column(Integer, nullable=True, default=30)
    created_by = Column(GUID, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    modality = relationship("ModalityModel")
    creator = relationship("UserModel", foreign_keys=[created_by])
    participants = relationship("UserModel", secondary=event_participants)

    __table_args__ = (
        Index("ix_events_start_datetime", "start_datetime"),
        Index("ix_events_modality_start", "modality_id", "start_datetime"),
    )


class ScheduleModel(Base):
    """SQLAlchemy model for schedules."""

    __tablename__ = "schedules"

    id = Column(GUID, primary_key=True)
    name = Column(String(255), nullable=False)
    user_id = Column(GUID, ForeignKey("users.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    modality_id = Column(GUID, ForeignKey("modalities.id", ondelete="SET NULL"), nullable=True)
    is_active = Column(Boolean, default=True)

    # Relationships
    user = relationship("UserModel")
    modality = relationship("ModalityModel")

    __table_args__ = (Index("ix_schedules_user_day", "user_id", "day_of_week"),)


# =============================================================================
# Resource Model
# =============================================================================


class ResourceModel(Base):
    """SQLAlchemy model for resources."""

    __tablename__ = "resources"

    id = Column(GUID, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    resource_type = Column(String(20), nullable=False)
    url = Column(String(1000), nullable=True)
    file_path = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)
    modality_id = Column(GUID, ForeignKey("modalities.id", ondelete="SET NULL"), nullable=True)
    access_level = Column(String(20), nullable=False, default="modality")
    tags = Column(JSON, nullable=True, default=list)
    is_active = Column(Boolean, default=True)
    view_count = Column(Integer, default=0)
    download_count = Column(Integer, default=0)
    created_by = Column(GUID, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    modality = relationship("ModalityModel")
    creator = relationship("UserModel")

    __table_args__ = (
        Index("ix_resources_modality_type", "modality_id", "resource_type"),
        Index("ix_resources_access_level", "access_level"),
    )


# =============================================================================
# Goal and Milestone Models
# =============================================================================


class GoalModel(Base):
    """SQLAlchemy model for goals."""

    __tablename__ = "goals"

    id = Column(GUID, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    competitor_id = Column(GUID, ForeignKey("competitors.id"), nullable=False)
    target_value = Column(Float, nullable=False, default=100.0)
    current_value = Column(Float, nullable=False, default=0.0)
    unit = Column(String(50), nullable=False, default="percent")
    priority = Column(String(20), nullable=False, default="medium")
    status = Column(String(20), nullable=False, default="not_started")
    start_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=True)
    modality_id = Column(GUID, ForeignKey("modalities.id", ondelete="SET NULL"), nullable=True)
    competence_id = Column(GUID, ForeignKey("competences.id"), nullable=True)
    created_by = Column(GUID, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    competitor = relationship("CompetitorModel")
    modality = relationship("ModalityModel")
    competence = relationship("CompetenceModel")
    creator = relationship("UserModel")
    milestones = relationship("MilestoneModel", back_populates="goal", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_goals_competitor_status", "competitor_id", "status"),
        Index("ix_goals_due_date", "due_date"),
    )


class MilestoneModel(Base):
    """SQLAlchemy model for milestones."""

    __tablename__ = "milestones"

    id = Column(GUID, primary_key=True)
    goal_id = Column(GUID, ForeignKey("goals.id"), nullable=False)
    title = Column(String(255), nullable=False)
    target_value = Column(Float, nullable=False)
    current_value = Column(Float, nullable=False, default=0.0)
    due_date = Column(Date, nullable=True)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    goal = relationship("GoalModel", back_populates="milestones")


# =============================================================================
# Badge and Achievement Models
# =============================================================================


class BadgeModel(Base):
    """SQLAlchemy model for badges."""

    __tablename__ = "badges"

    id = Column(GUID, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    category = Column(String(20), nullable=False)
    rarity = Column(String(20), nullable=False, default="common")
    icon_url = Column(String(500), nullable=True)
    points = Column(Integer, nullable=False, default=10)
    criteria = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    achievements = relationship("AchievementModel", back_populates="badge")


class AchievementModel(Base):
    """SQLAlchemy model for achievements."""

    __tablename__ = "achievements"

    id = Column(GUID, primary_key=True)
    badge_id = Column(GUID, ForeignKey("badges.id"), nullable=False)
    user_id = Column(GUID, ForeignKey("users.id"), nullable=False)
    competitor_id = Column(GUID, ForeignKey("competitors.id"), nullable=True)
    earned_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    progress = Column(Float, nullable=False, default=100.0)
    extra_data = Column("metadata", JSON, nullable=True)

    # Relationships
    badge = relationship("BadgeModel", back_populates="achievements")
    user = relationship("UserModel")
    competitor = relationship("CompetitorModel")

    __table_args__ = (Index("ix_achievements_user_badge", "user_id", "badge_id", unique=True),)


class UserPointsModel(Base):
    """SQLAlchemy model for user points."""

    __tablename__ = "user_points"

    id = Column(GUID, primary_key=True)
    user_id = Column(GUID, ForeignKey("users.id"), nullable=False, unique=True)
    total_points = Column(Integer, nullable=False, default=0)
    level = Column(Integer, nullable=False, default=1)
    badges_count = Column(Integer, nullable=False, default=0)

    # Relationships
    user = relationship("UserModel")

    __table_args__ = (Index("ix_user_points_total", "total_points"),)


# =============================================================================
# Message and Conversation Models
# =============================================================================


class ConversationModel(Base):
    """SQLAlchemy model for conversations."""

    __tablename__ = "conversations"

    id = Column(GUID, primary_key=True)
    participant_1 = Column(GUID, ForeignKey("users.id"), nullable=False)
    participant_2 = Column(GUID, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=True)
    modality_id = Column(GUID, ForeignKey("modalities.id", ondelete="SET NULL"), nullable=True)
    is_active = Column(Boolean, default=True)
    last_message_at = Column(DateTime, nullable=True)
    unread_count_1 = Column(Integer, default=0)
    unread_count_2 = Column(Integer, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user_1 = relationship("UserModel", foreign_keys=[participant_1])
    user_2 = relationship("UserModel", foreign_keys=[participant_2])
    modality = relationship("ModalityModel")
    messages = relationship(
        "MessageModel", back_populates="conversation", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_conversations_participants", "participant_1", "participant_2", unique=True),
        Index("ix_conversations_updated", "updated_at"),
    )


class MessageModel(Base):
    """SQLAlchemy model for messages."""

    __tablename__ = "messages"

    id = Column(GUID, primary_key=True)
    conversation_id = Column(GUID, ForeignKey("conversations.id"), nullable=False)
    sender_id = Column(GUID, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    message_type = Column(String(20), nullable=False, default="text")
    file_url = Column(String(500), nullable=True)
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    conversation = relationship("ConversationModel", back_populates="messages")
    sender = relationship("UserModel")

    __table_args__ = (Index("ix_messages_conversation_created", "conversation_id", "created_at"),)


# =============================================================================
# Feedback Model
# =============================================================================


class FeedbackModel(Base):
    """SQLAlchemy model for feedback."""

    __tablename__ = "feedbacks"

    id = Column(GUID, primary_key=True)
    competitor_id = Column(GUID, ForeignKey("competitors.id"), nullable=False)
    evaluator_id = Column(GUID, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    feedback_type = Column(String(20), nullable=False, default="general")
    exam_id = Column(GUID, ForeignKey("exams.id"), nullable=True)
    competence_id = Column(GUID, ForeignKey("competences.id"), nullable=True)
    grade_id = Column(GUID, ForeignKey("grades.id"), nullable=True)
    training_id = Column(GUID, ForeignKey("training_sessions.id"), nullable=True)
    rating = Column(Integer, nullable=True)
    is_private = Column(Boolean, default=False)
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    competitor = relationship("CompetitorModel")
    evaluator = relationship("UserModel")
    exam = relationship("ExamModel")
    competence = relationship("CompetenceModel")
    grade = relationship("GradeModel")
    training = relationship("TrainingSessionModel")

    __table_args__ = (
        Index("ix_feedbacks_competitor_type", "competitor_id", "feedback_type"),
        Index("ix_feedbacks_evaluator", "evaluator_id"),
    )


# =============================================================================
# Training Plan Models
# =============================================================================


class TrainingPlanModel(Base):
    """SQLAlchemy model for training plans."""

    __tablename__ = "training_plans"

    id = Column(GUID, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    competitor_id = Column(GUID, ForeignKey("competitors.id"), nullable=False)
    modality_id = Column(GUID, ForeignKey("modalities.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(20), nullable=False, default="draft")
    priority = Column(String(20), nullable=False, default="medium")
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    target_hours = Column(Float, nullable=False, default=0.0)
    is_suggested = Column(Boolean, default=False)
    created_by = Column(GUID, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    competitor = relationship("CompetitorModel")
    modality = relationship("ModalityModel")
    creator = relationship("UserModel")
    items = relationship("PlanItemModel", back_populates="plan", cascade="all, delete-orphan")

    __table_args__ = (Index("ix_training_plans_competitor_status", "competitor_id", "status"),)


class PlanItemModel(Base):
    """SQLAlchemy model for plan items."""

    __tablename__ = "plan_items"

    id = Column(GUID, primary_key=True)
    plan_id = Column(GUID, ForeignKey("training_plans.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    competence_id = Column(GUID, ForeignKey("competences.id"), nullable=True)
    order = Column(Integer, nullable=False, default=0)
    duration_hours = Column(Float, nullable=False, default=1.0)
    is_required = Column(Boolean, default=True)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    due_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    plan = relationship("TrainingPlanModel", back_populates="items")
    competence = relationship("CompetenceModel")
    resources = relationship("ResourceModel", secondary=plan_item_resources)

    __table_args__ = (Index("ix_plan_items_plan_order", "plan_id", "order"),)
