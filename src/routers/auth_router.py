from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.dependencies import Logger, tracer
from src.models.user_model import UserCreate, UserPublic
from src.schemas import Response
from src.services.auth_service import AuthService

AuthRouter = APIRouter(prefix="/api/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    token: str
    token_type: str = "bearer"
    expires_in: int = 86400


@AuthRouter.post("/register", response_model=Response[UserPublic])
@tracer.observe()
async def register(
    user: UserCreate,
    logger: Logger,
    auth_service: Annotated[AuthService, Depends()],
):
    """Register a new user account."""
    logger.info({"message": "User registration", "username": user.username})
    result = await auth_service.register(user)
    return Response(
        status_code=201,
        message="User registered successfully",
        data=UserPublic.model_validate(result),
    )


@AuthRouter.post("/login", response_model=Response[TokenResponse])
@tracer.observe()
async def login(
    credentials: LoginRequest,
    logger: Logger,
    auth_service: Annotated[AuthService, Depends()],
):
    """Login with username and password."""
    logger.info({"message": "Login attempt", "username": credentials.username})
    token = await auth_service.login(credentials.username, credentials.password)
    return Response(
        status_code=200,
        message="Login successful",
        data=TokenResponse(token=token),
    )


@AuthRouter.post("/logout", response_model=Response)
@tracer.observe()
async def logout(
    token: str,
    logger: Logger,
    auth_service: Annotated[AuthService, Depends()],
):
    """Logout and invalidate token."""
    logger.info({"message": "Logout request"})
    await auth_service.logout(token)
    return Response(
        status_code=200,
        message="Logged out successfully",
        data=None,
    )
