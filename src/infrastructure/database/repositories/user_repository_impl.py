"""SQLAlchemy User repository implementation."""

from uuid import UUID

from sqlalchemy import exists, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.identity.entities.permission import Permission
from src.domain.identity.entities.role import Role
from src.domain.identity.entities.user import User
from src.domain.identity.repositories.user_repository import UserRepository
from src.domain.identity.value_objects.email import Email
from src.domain.identity.value_objects.password import Password
from src.infrastructure.database.models.user_model import (
    RoleModel,
    UserModel,
)
from src.shared.constants.enums import UserRole, UserStatus


class SQLAlchemyUserRepository(UserRepository):
    """SQLAlchemy implementation of UserRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _model_to_entity(self, model: UserModel) -> User:
        """Convert UserModel to User entity."""
        role_entity = None
        if model.role_entity:
            permissions = [
                Permission(
                    id=p.id,
                    name=p.name,
                    description=p.description or "",
                    resource=p.resource,
                    action=p.action,
                    created_at=p.created_at,
                    updated_at=p.updated_at,
                )
                for p in model.role_entity.permissions
            ]
            role_entity = Role(
                id=model.role_entity.id,
                name=UserRole(model.role_entity.name),
                description=model.role_entity.description or "",
                permissions=permissions,
                created_at=model.role_entity.created_at,
                updated_at=model.role_entity.updated_at,
            )

        return User(
            id=model.id,
            email=Email(model.email),
            password=Password(model.password_hash),
            full_name=model.full_name,
            role=UserRole(model.role),
            status=UserStatus(model.status),
            role_entity=role_entity,
            last_login_at=model.last_login_at,
            must_change_password=model.must_change_password,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _entity_to_model(self, entity: User) -> UserModel:
        """Convert User entity to UserModel."""
        return UserModel(
            id=entity.id,
            email=entity.email.value,
            password_hash=entity.password.hashed_value,
            full_name=entity.full_name,
            role=entity.role.value,
            status=entity.status.value,
            must_change_password=entity.must_change_password,
            last_login_at=entity.last_login_at,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def get_by_id(self, id: UUID) -> User | None:
        """Get user by ID."""
        stmt = (
            select(UserModel)
            .where(UserModel.id == id)
            .options(selectinload(UserModel.role_entity).selectinload(RoleModel.permissions))
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def get_by_email(self, email: str) -> User | None:
        """Get user by email address."""
        stmt = (
            select(UserModel)
            .where(UserModel.email == email.lower())
            .options(selectinload(UserModel.role_entity).selectinload(RoleModel.permissions))
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None

    async def get_by_role(
        self,
        role: UserRole,
        skip: int = 0,
        limit: int = 100,
    ) -> list[User]:
        """Get users by role."""
        stmt = (
            select(UserModel)
            .where(UserModel.role == role.value)
            .options(selectinload(UserModel.role_entity).selectinload(RoleModel.permissions))
            .offset(skip)
            .limit(limit)
            .order_by(UserModel.created_at.desc())
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[User]:
        """Get all users with pagination."""
        stmt = (
            select(UserModel)
            .options(selectinload(UserModel.role_entity).selectinload(RoleModel.permissions))
            .offset(skip)
            .limit(limit)
            .order_by(UserModel.created_at.desc())
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

    async def add(self, entity: User) -> User:
        """Add a new user."""
        model = self._entity_to_model(entity)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._model_to_entity(model)

    async def update(self, entity: User) -> User:
        """Update an existing user."""
        stmt = select(UserModel).where(UserModel.id == entity.id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            model.email = entity.email.value
            model.password_hash = entity.password.hashed_value
            model.full_name = entity.full_name
            model.role = entity.role.value
            model.status = entity.status.value
            model.must_change_password = entity.must_change_password
            model.last_login_at = entity.last_login_at
            model.updated_at = entity.updated_at
            await self._session.flush()
            await self._session.refresh(model)
            return self._model_to_entity(model)

        raise ValueError(f"User with id {entity.id} not found")

    async def delete(self, id: UUID) -> bool:
        """Delete a user by ID."""
        stmt = select(UserModel).where(UserModel.id == id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            await self._session.delete(model)
            await self._session.flush()
            return True
        return False

    async def exists(self, id: UUID) -> bool:
        """Check if user exists."""
        stmt = select(exists().where(UserModel.id == id))
        result = await self._session.execute(stmt)
        return result.scalar() or False

    async def count(self) -> int:
        """Count total number of users."""
        stmt = select(func.count(UserModel.id))
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def email_exists(self, email: str) -> bool:
        """Check if email is already registered."""
        stmt = select(exists().where(UserModel.email == email.lower()))
        result = await self._session.execute(stmt)
        return result.scalar() or False
