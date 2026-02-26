"""Message and Conversation entities for chat functionality."""

from datetime import datetime
from uuid import UUID, uuid4

from src.shared.constants.enums import MessageType
from src.shared.domain.aggregate_root import AggregateRoot
from src.shared.domain.entity import Entity


class Message(Entity[UUID]):
    """Message entity for chat."""

    def __init__(
        self,
        conversation_id: UUID,
        sender_id: UUID,
        content: str,
        message_type: MessageType = MessageType.TEXT,
        file_url: str | None = None,
        is_read: bool = False,
        read_at: datetime | None = None,
        id: UUID | None = None,
        created_at: datetime | None = None,
    ) -> None:
        super().__init__(id=id or uuid4())
        self._conversation_id = conversation_id
        self._sender_id = sender_id
        self._content = content
        self._message_type = message_type
        self._file_url = file_url
        self._is_read = is_read
        self._read_at = read_at
        self._created_at = created_at or datetime.utcnow()
        self._is_deleted = False

    @property
    def conversation_id(self) -> UUID:
        return self._conversation_id

    @property
    def sender_id(self) -> UUID:
        return self._sender_id

    @property
    def content(self) -> str:
        return self._content

    @property
    def message_type(self) -> MessageType:
        return self._message_type

    @property
    def file_url(self) -> str | None:
        return self._file_url

    @property
    def is_read(self) -> bool:
        return self._is_read

    @property
    def read_at(self) -> datetime | None:
        return self._read_at

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def is_deleted(self) -> bool:
        return self._is_deleted

    def mark_as_read(self) -> None:
        """Mark message as read."""
        if not self._is_read:
            self._is_read = True
            self._read_at = datetime.utcnow()

    def delete(self) -> None:
        """Soft delete the message."""
        self._is_deleted = True
        self._content = "[Mensagem removida]"

    @classmethod
    def create_system_message(
        cls,
        conversation_id: UUID,
        content: str,
    ) -> "Message":
        """Create a system message."""
        return cls(
            conversation_id=conversation_id,
            sender_id=UUID("00000000-0000-0000-0000-000000000000"),  # System user
            content=content,
            message_type=MessageType.SYSTEM,
        )


class Conversation(AggregateRoot[UUID]):
    """Conversation entity for 1-on-1 chat."""

    def __init__(
        self,
        participant_1: UUID,
        participant_2: UUID,
        title: str | None = None,
        modality_id: UUID | None = None,
        is_active: bool = True,
        id: UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        super().__init__(id=id or uuid4())
        self._participant_1 = participant_1
        self._participant_2 = participant_2
        self._title = title
        self._modality_id = modality_id
        self._is_active = is_active
        self._created_at = created_at or datetime.utcnow()
        self._updated_at = updated_at or datetime.utcnow()
        self._last_message_at: datetime | None = None
        self._unread_count_1 = 0  # Unread for participant 1
        self._unread_count_2 = 0  # Unread for participant 2

    @property
    def participant_1(self) -> UUID:
        return self._participant_1

    @property
    def participant_2(self) -> UUID:
        return self._participant_2

    @property
    def participants(self) -> tuple[UUID, UUID]:
        return (self._participant_1, self._participant_2)

    @property
    def title(self) -> str | None:
        return self._title

    @property
    def modality_id(self) -> UUID | None:
        return self._modality_id

    @property
    def is_active(self) -> bool:
        return self._is_active

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    @property
    def last_message_at(self) -> datetime | None:
        return self._last_message_at

    def get_unread_count(self, user_id: UUID) -> int:
        """Get unread message count for a user."""
        if user_id == self._participant_1:
            return self._unread_count_1
        elif user_id == self._participant_2:
            return self._unread_count_2
        return 0

    def is_participant(self, user_id: UUID) -> bool:
        """Check if user is a participant."""
        return user_id in (self._participant_1, self._participant_2)

    def get_other_participant(self, user_id: UUID) -> UUID | None:
        """Get the other participant in the conversation."""
        if user_id == self._participant_1:
            return self._participant_2
        elif user_id == self._participant_2:
            return self._participant_1
        return None

    def add_message(self, sender_id: UUID) -> None:
        """Register that a new message was added."""
        self._last_message_at = datetime.utcnow()
        self._updated_at = datetime.utcnow()

        # Increment unread for the other participant
        if sender_id == self._participant_1:
            self._unread_count_2 += 1
        elif sender_id == self._participant_2:
            self._unread_count_1 += 1

    def mark_as_read(self, user_id: UUID) -> None:
        """Mark all messages as read for a user."""
        if user_id == self._participant_1:
            self._unread_count_1 = 0
        elif user_id == self._participant_2:
            self._unread_count_2 = 0

    def close(self) -> None:
        """Close the conversation."""
        self._is_active = False
        self._updated_at = datetime.utcnow()

    def reopen(self) -> None:
        """Reopen the conversation."""
        self._is_active = True
        self._updated_at = datetime.utcnow()

    @classmethod
    def create_evaluator_competitor_chat(
        cls,
        evaluator_id: UUID,
        competitor_id: UUID,
        modality_id: UUID | None = None,
    ) -> "Conversation":
        """Create a conversation between evaluator and competitor."""
        return cls(
            participant_1=evaluator_id,
            participant_2=competitor_id,
            modality_id=modality_id,
        )
