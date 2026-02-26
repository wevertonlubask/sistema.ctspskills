"""Authentication dependencies."""

from typing import Annotated, Any
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.identity.entities.user import User
from src.infrastructure.container import get_container
from src.infrastructure.database.repositories.user_repository_impl import (
    SQLAlchemyUserRepository,
)
from src.presentation.api.v1.dependencies.database import get_db
from src.shared.constants.enums import UserRole
from src.shared.exceptions import AuthenticationException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Get current authenticated user from JWT token.

    Args:
        token: JWT access token.
        db: Database session.

    Returns:
        User entity.

    Raises:
        HTTPException: If authentication fails.
    """
    container = get_container()
    jwt_handler = container.jwt_handler

    try:
        payload = jwt_handler.verify_access_token(token)
        user_id = UUID(payload["sub"])
    except AuthenticationException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    except (KeyError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    user_repository = SQLAlchemyUserRepository(db)
    user = await user_repository.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Get current active user.

    Args:
        current_user: Current authenticated user.

    Returns:
        User entity if active.

    Raises:
        HTTPException: If user is not active.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User account is {current_user.status.value}",
        )
    return current_user


def require_role(*roles: UserRole) -> Any:
    """Dependency factory for role-based access control.

    Args:
        roles: Allowed roles.

    Returns:
        Dependency function.
    """

    async def role_checker(
        current_user: Annotated[User, Depends(get_current_active_user)],
    ) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {current_user.role.value} is not allowed. Required: {[r.value for r in roles]}",
            )
        return current_user

    return role_checker


async def require_super_admin(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """Require super admin role.

    Args:
        current_user: Current authenticated user.

    Returns:
        User if super admin.

    Raises:
        HTTPException: If user is not super admin.
    """
    if not current_user.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required",
        )
    return current_user


async def require_evaluator(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """Require evaluator or super admin role.

    Args:
        current_user: Current authenticated user.

    Returns:
        User if evaluator or super admin.

    Raises:
        HTTPException: If user is not evaluator or super admin.
    """
    if current_user.role not in (UserRole.EVALUATOR, UserRole.SUPER_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Evaluator or super admin access required",
        )
    return current_user


async def require_competitor(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """Require competitor role (or admin).

    Args:
        current_user: Current authenticated user.

    Returns:
        User if competitor or super admin.

    Raises:
        HTTPException: If user is not competitor or super admin.
    """
    if current_user.role not in (UserRole.COMPETITOR, UserRole.SUPER_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Competitor access required",
        )
    return current_user
