"""Message and Conversation use cases."""

from uuid import UUID

from src.application.extras.dtos.message_dto import (
    ConversationDTO,
    ConversationListDTO,
    CreateConversationDTO,
    CreateMessageDTO,
    MessageDTO,
    MessageListDTO,
)
from src.domain.extras.entities.message import Conversation, Message
from src.domain.extras.exceptions import (
    ConversationNotFoundException,
    NotConversationParticipantException,
)
from src.domain.extras.repositories.message_repository import (
    ConversationRepository,
    MessageRepository,
)


class SendMessageUseCase:
    """Use case for sending messages."""

    def __init__(
        self,
        conversation_repository: ConversationRepository,
        message_repository: MessageRepository,
    ) -> None:
        self._conversation_repository = conversation_repository
        self._message_repository = message_repository

    async def execute(
        self,
        sender_id: UUID,
        dto: CreateMessageDTO,
    ) -> MessageDTO:
        """Send a message.

        Args:
            sender_id: Sender user UUID.
            dto: Message data.

        Returns:
            Created message DTO.

        Raises:
            ConversationNotFoundException: If conversation not found.
            NotConversationParticipantException: If sender not a participant.
        """
        # Get conversation
        conversation = await self._conversation_repository.get_by_id(dto.conversation_id)
        if not conversation:
            raise ConversationNotFoundException(str(dto.conversation_id))

        # Check if sender is a participant
        if not conversation.is_participant(sender_id):
            raise NotConversationParticipantException(
                str(sender_id),
                str(dto.conversation_id),
            )

        # Create message
        message = Message(
            conversation_id=dto.conversation_id,
            sender_id=sender_id,
            content=dto.content,
            message_type=dto.message_type,
            file_url=dto.file_url,
        )

        # Save message
        saved_message = await self._message_repository.save(message)

        # Update conversation
        conversation.add_message(sender_id)
        await self._conversation_repository.update(conversation)

        return MessageDTO.from_entity(saved_message)

    async def create_conversation(
        self,
        creator_id: UUID,
        dto: CreateConversationDTO,
    ) -> ConversationDTO:
        """Create a new conversation.

        Args:
            creator_id: Creator user UUID.
            dto: Conversation data.

        Returns:
            Created conversation DTO.
        """
        # Check if conversation already exists
        existing = await self._conversation_repository.get_by_participants(
            creator_id,
            dto.participant_2,
        )

        if existing:
            return ConversationDTO.from_entity(existing, creator_id)

        # Create new conversation
        conversation = Conversation(
            participant_1=creator_id,
            participant_2=dto.participant_2,
            title=dto.title,
            modality_id=dto.modality_id,
        )

        saved_conv = await self._conversation_repository.save(conversation)

        # Send initial message if provided
        if dto.initial_message:
            message = Message(
                conversation_id=saved_conv.id,
                sender_id=creator_id,
                content=dto.initial_message,
            )
            await self._message_repository.save(message)
            saved_conv.add_message(creator_id)
            await self._conversation_repository.update(saved_conv)

        return ConversationDTO.from_entity(saved_conv, creator_id)


class ListConversationsUseCase:
    """Use case for listing conversations."""

    def __init__(
        self,
        conversation_repository: ConversationRepository,
        message_repository: MessageRepository,
    ) -> None:
        self._conversation_repository = conversation_repository
        self._message_repository = message_repository

    async def execute(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> ConversationListDTO:
        """List conversations for a user.

        Args:
            user_id: User UUID.
            skip: Number of items to skip.
            limit: Maximum items to return.

        Returns:
            Conversation list DTO.
        """
        conversations = await self._conversation_repository.get_by_user(
            user_id=user_id,
            skip=skip,
            limit=limit,
        )

        total_unread = 0
        result = []
        for conv in conversations:
            unread = conv.get_unread_count(user_id)
            total_unread += unread
            result.append(ConversationDTO.from_entity(conv, user_id))

        return ConversationListDTO(
            conversations=result,
            total=len(conversations),
            total_unread=total_unread,
        )


class ListMessagesUseCase:
    """Use case for listing messages in a conversation."""

    def __init__(
        self,
        conversation_repository: ConversationRepository,
        message_repository: MessageRepository,
    ) -> None:
        self._conversation_repository = conversation_repository
        self._message_repository = message_repository

    async def execute(
        self,
        user_id: UUID,
        conversation_id: UUID,
        skip: int = 0,
        limit: int = 50,
        before_id: UUID | None = None,
    ) -> MessageListDTO:
        """List messages in a conversation.

        Args:
            user_id: User UUID (for validation).
            conversation_id: Conversation UUID.
            skip: Number of items to skip.
            limit: Maximum items to return.
            before_id: Get messages before this ID.

        Returns:
            Message list DTO.

        Raises:
            ConversationNotFoundException: If conversation not found.
            NotConversationParticipantException: If user not a participant.
        """
        # Get conversation
        conversation = await self._conversation_repository.get_by_id(conversation_id)
        if not conversation:
            raise ConversationNotFoundException(str(conversation_id))

        # Check if user is a participant
        if not conversation.is_participant(user_id):
            raise NotConversationParticipantException(str(user_id), str(conversation_id))

        # Get messages
        messages = await self._message_repository.get_by_conversation(
            conversation_id=conversation_id,
            skip=skip,
            limit=limit + 1,  # Get one extra to check if there's more
            before_id=before_id,
        )

        has_more = len(messages) > limit
        if has_more:
            messages = messages[:limit]

        # Mark as read
        await self._message_repository.mark_conversation_as_read(
            conversation_id=conversation_id,
            user_id=user_id,
        )

        # Update conversation unread count
        conversation.mark_as_read(user_id)
        await self._conversation_repository.update(conversation)

        return MessageListDTO(
            messages=[MessageDTO.from_entity(m) for m in messages],
            total=len(messages),
            has_more=has_more,
        )
