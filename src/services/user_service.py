import hashlib
import secrets
from typing import Annotated
from uuid import UUID

from fastapi import Depends

from src.dependencies import Logger, tracer
from src.exceptions.user_exception import InvalidCredentialsError
from src.models.user_model import User, UserCreate, UserPublic, UserUpdate
from src.repositories.user_repository import UserRepository
from src.schemas import Page


def hash_password(password: str) -> str:
    """Hash password using SHA-256 with salt."""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
    return f"{salt}:{password_hash}"


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against stored hash."""
    try:
        salt, stored_hash = password_hash.split(":")
        computed_hash = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
        return secrets.compare_digest(computed_hash, stored_hash)
    except ValueError:
        return False


class UserService:
    user_repository: UserRepository
    logger: Logger

    def __init__(
        self,
        user_repository: Annotated[UserRepository, Depends()],
        logger: Logger,
    ) -> None:
        self.user_repository = user_repository
        self.logger = logger

    @tracer.observe()
    async def create(self, user: UserCreate) -> User:
        async with tracer.track(
            "logic:create_user", attributes={"user.username": user.username}
        ) as span:
            try:
                self.logger.info(
                    {
                        "message": "Starting user creation",
                        "username": user.username,
                        "email": user.email,
                    }
                )
                password_hash = hash_password(user.password)
                result = await self.user_repository.create(user, password_hash)
                span.set_attribute("user.id", str(result.id))
                return result
            except Exception as e:
                self.logger.error(
                    {
                        "message": "Failed to create user",
                        "error": str(e),
                    }
                )
                span.record_exception(e)
                raise

    @tracer.observe()
    async def read_all(self) -> Page[User]:
        async with tracer.track("logic:read_all_users") as span:
            self.logger.debug({"message": "Fetching all users"})
            result = await self.user_repository.read_all()
            span.set_attribute("users.count", len(result.items))
            return result

    @tracer.observe()
    async def read(self, id: UUID) -> User:
        self.logger.debug({"message": "Reading user", "user_id": str(id)})
        return await self.user_repository.read(id=id)

    @tracer.observe()
    async def update(self, id: UUID, user: UserUpdate) -> User:
        self.logger.debug(
            {
                "message": "Updating user",
                "user_id": str(id),
                "update_data": user.model_dump(mode="json", exclude_none=True),
            }
        )
        return await self.user_repository.update(id, user)

    @tracer.observe()
    async def delete(self, id: UUID) -> None:
        self.logger.debug({"message": "Deleting user", "user_id": str(id)})
        return await self.user_repository.delete(id=id)

    @tracer.observe()
    async def authenticate(self, username: str, password: str) -> User:
        """Authenticate user by username and password."""
        self.logger.debug(
            {"message": "Authenticating user", "username": username}
        )
        user = await self.user_repository.read_by_username(username)
        if not verify_password(password, user.password_hash):
            self.logger.warning(
                {"message": "Invalid password", "username": username}
            )
            raise InvalidCredentialsError()
        return user
