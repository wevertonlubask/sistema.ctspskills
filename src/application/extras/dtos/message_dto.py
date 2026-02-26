"""Message and Conversation DTOs."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.domain.extras.entities.message import Conversation, Message
from src.shared.constants.enums import MessageType


@dataclass
class CreateMessageDTO:
    """DTO for creating a message."""

    conversation_id: UUID
    content: str
    message_type: MessageType = MessageType.TEXT
    file_url: str | None = None


@dataclass
class MessageDTO:
    """DTO for message responses."""

    id: UUID
    conversation_id: UUID
    sender_id: UUID
    content: str
    message_type: str
    file_url: str | None
    is_read: bool
    read_at: datetime | None
    is_deleted: bool
    created_at: datetime

    @classmethod
    def from_entity(cls, entity: Message) -> "MessageDTO":
        return cls(
            id=entity.id,
            conversation_id=entity.conversation_id,
            sender_id=entity.sender_id,
            content=entity.content,
            message_type=entity.message_type.value,
            file_url=entity.file_url,
            is_read=entity.is_read,
            read_at=entity.read_at,
            is_deleted=entity.is_deleted,
            created_at=entity.created_at,
        )


@dataclass
class CreateConversationDTO:
    """DTO for creating a conversation."""

    participant_2: UUID
    title: str | None = None
    modality_id: UUID | None = None
    initial_message: str | None = None


@dataclass
class ConversationDTO:
    """DTO for conversation responses."""

    id: UUID
    participant_1: UUID
    participant_2: UUID
    title: str | None
    modality_id: UUID | None
    is_active: bool
    last_message_at: datetime | None
    unread_count: int
    created_at: datetime
    updated_at: datetime
    other_participant_name: str | None = None
    last_message: MessageDTO | None = None

    @classmethod
    def from_entity(
        cls,
        entity: Conversation,
        current_user_id: UUID,
        other_participant_name: str | None = None,
        last_message: Message | None = None,
    ) -> "ConversationDTO":
        return cls(
            id=entity.id,
            participant_1=entity.participant_1,
            participant_2=entity.participant_2,
            title=entity.title,
            modality_id=entity.modality_id,
            is_active=entity.is_active,
            last_message_at=entity.last_message_at,
            unread_count=entity.get_unread_count(current_user_id),
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            other_participant_name=other_participant_name,
            last_message=MessageDTO.from_entity(last_message) if last_message else None,
        )


@dataclass
class ConversationListDTO:
    """DTO for conversation list."""

    conversations: list[ConversationDTO]
    total: int
    total_unread: int


@dataclass
class MessageListDTO:
    """DTO for message list."""

    messages: list[MessageDTO]
    total: int
    has_more: bool
