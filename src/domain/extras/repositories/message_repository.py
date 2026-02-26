"""Message and Conversation repository interfaces."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.extras.entities.message import Conversation, Message


class ConversationRepository(ABC):
    """Abstract repository for conversations."""

    @abstractmethod
    async def save(self, conversation: Conversation) -> Conversation:
        """Save a conversation."""
        ...

    @abstractmethod
    async def get_by_id(self, conversation_id: UUID) -> Conversation | None:
        """Get conversation by ID."""
        ...

    @abstractmethod
    async def get_by_participants(
        self,
        participant_1: UUID,
        participant_2: UUID,
    ) -> Conversation | None:
        """Get conversation between two participants."""
        ...

    @abstractmethod
    async def get_by_user(
        self,
        user_id: UUID,
        is_active: bool | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Conversation]:
        """Get conversations for a user."""
        ...

    @abstractmethod
    async def get_with_unread(
        self,
        user_id: UUID,
    ) -> list[Conversation]:
        """Get conversations with unread messages."""
        ...

    @abstractmethod
    async def update(self, conversation: Conversation) -> Conversation:
        """Update a conversation."""
        ...

    @abstractmethod
    async def delete(self, conversation_id: UUID) -> bool:
        """Delete a conversation."""
        ...


class MessageRepository(ABC):
    """Abstract repository for messages."""

    @abstractmethod
    async def save(self, message: Message) -> Message:
        """Save a message."""
        ...

    @abstractmethod
    async def get_by_id(self, message_id: UUID) -> Message | None:
        """Get message by ID."""
        ...

    @abstractmethod
    async def get_by_conversation(
        self,
        conversation_id: UUID,
        skip: int = 0,
        limit: int = 50,
        before_id: UUID | None = None,
    ) -> list[Message]:
        """Get messages for a conversation."""
        ...

    @abstractmethod
    async def get_unread_count(
        self,
        conversation_id: UUID,
        user_id: UUID,
    ) -> int:
        """Get unread message count for a user in a conversation."""
        ...

    @abstractmethod
    async def mark_as_read(
        self,
        message_id: UUID,
    ) -> bool:
        """Mark a message as read."""
        ...

    @abstractmethod
    async def mark_conversation_as_read(
        self,
        conversation_id: UUID,
        user_id: UUID,
    ) -> int:
        """Mark all messages in conversation as read. Returns count."""
        ...

    @abstractmethod
    async def delete(self, message_id: UUID) -> bool:
        """Delete a message."""
        ...

    @abstractmethod
    async def search(
        self,
        conversation_id: UUID,
        query: str,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Message]:
        """Search messages in a conversation."""
        ...
