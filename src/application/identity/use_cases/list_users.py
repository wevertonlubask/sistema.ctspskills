"""List users use case."""

from src.application.identity.dtos.user_dto import UserDTO, UserListDTO
from src.domain.identity.repositories.user_repository import UserRepository
from src.shared.constants.enums import UserRole


class ListUsersUseCase:
    """Use case for listing users."""

    def __init__(
        self,
        user_repository: UserRepository,
    ) -> None:
        self._user_repository = user_repository

    async def execute(
        self,
        skip: int = 0,
        limit: int = 100,
        role: UserRole | None = None,
    ) -> UserListDTO:
        """List users with pagination.

        Args:
            skip: Number of records to skip.
            limit: Maximum number of records to return.
            role: Optional role filter.

        Returns:
            User list DTO with pagination info.
        """
        if role:
            users = await self._user_repository.get_by_role(role, skip=skip, limit=limit)
        else:
            users = await self._user_repository.get_all(skip=skip, limit=limit)

        total = await self._user_repository.count()

        return UserListDTO(
            users=[UserDTO.from_entity(user) for user in users],
            total=total,
            skip=skip,
            limit=limit,
        )
