"""Get current user use case."""

from uuid import UUID

from src.application.identity.dtos.user_dto import UserDTO
from src.domain.identity.exceptions import UserNotFoundException
from src.domain.identity.repositories.user_repository import UserRepository


class GetCurrentUserUseCase:
    """Use case for getting current authenticated user."""

    def __init__(
        self,
        user_repository: UserRepository,
    ) -> None:
        self._user_repository = user_repository

    async def execute(self, user_id: UUID) -> UserDTO:
        """Get current user by ID.

        Args:
            user_id: User identifier from token.

        Returns:
            User DTO.

        Raises:
            UserNotFoundException: If user is not found.
        """
        user = await self._user_repository.get_by_id(user_id)

        if not user:
            raise UserNotFoundException(identifier=str(user_id))

        return UserDTO.from_entity(user)
