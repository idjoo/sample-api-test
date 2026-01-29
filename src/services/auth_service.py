import secrets
from datetime import datetime, timedelta
from typing import Annotated
from uuid import UUID

from fastapi import Depends

from src.dependencies import Logger, tracer
from src.exceptions.user_exception import UnauthorizedError
from src.models.user_model import User, UserCreate
from src.services.user_service import UserService


class AuthService:
    user_service: UserService
    logger: Logger
    _tokens: dict[str, tuple[UUID, datetime]]

    def __init__(
        self,
        user_service: Annotated[UserService, Depends()],
        logger: Logger,
    ) -> None:
        self.user_service = user_service
        self.logger = logger
        self._tokens = {}

    @tracer.observe()
    async def register(self, user: UserCreate) -> User:
        """Register a new user."""
        self.logger.info(
            {"message": "Registering new user", "username": user.username}
        )
        return await self.user_service.create(user)

    @tracer.observe()
    async def login(self, username: str, password: str) -> str:
        """Authenticate user and return token."""
        self.logger.info({"message": "User login attempt", "username": username})
        user = await self.user_service.authenticate(username, password)
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=24)
        self._tokens[token] = (user.id, expires_at)
        self.logger.info(
            {"message": "User logged in successfully", "user_id": str(user.id)}
        )
        return token

    @tracer.observe()
    async def validate_token(self, token: str) -> UUID:
        """Validate token and return user ID."""
        if token not in self._tokens:
            self.logger.warning({"message": "Invalid token provided"})
            raise UnauthorizedError()
        user_id, expires_at = self._tokens[token]
        if datetime.now() > expires_at:
            del self._tokens[token]
            self.logger.warning(
                {"message": "Token expired", "user_id": str(user_id)}
            )
            raise UnauthorizedError()
        return user_id

    @tracer.observe()
    async def logout(self, token: str) -> None:
        """Invalidate token."""
        if token in self._tokens:
            user_id, _ = self._tokens[token]
            del self._tokens[token]
            self.logger.info(
                {"message": "User logged out", "user_id": str(user_id)}
            )
