from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from src.dependencies import Logger, tracer
from src.models.user_model import UserCreate, UserPublic, UserUpdate
from src.schemas import Page, Response
from src.services.user_service import UserService

UserRouter = APIRouter(prefix="/api/users", tags=["Users"])


@UserRouter.post("/", response_model=Response[UserPublic])
@tracer.observe()
async def create_user(
    user: UserCreate,
    logger: Logger,
    user_service: Annotated[UserService, Depends()],
):
    """Create a new user."""
    logger.info({"message": "Creating new user", "username": user.username})
    result = await user_service.create(user)
    return Response(
        status_code=201,
        message="User created",
        data=UserPublic.model_validate(result),
    )


@UserRouter.get("/", response_model=Page[UserPublic])
@tracer.observe()
async def read_users(
    logger: Logger,
    user_service: Annotated[UserService, Depends()],
):
    """Get all users (paginated)."""
    logger.debug({"message": "Fetching all users"})
    return await user_service.read_all()


@UserRouter.get("/{user_id}", response_model=Response[UserPublic])
@tracer.observe()
async def read_user(
    user_id: UUID,
    logger: Logger,
    user_service: Annotated[UserService, Depends()],
):
    """Get a user by ID."""
    logger.debug({"message": "Fetching user", "user_id": str(user_id)})
    result = await user_service.read(user_id)
    return Response(
        status_code=200,
        message="User retrieved",
        data=UserPublic.model_validate(result),
    )


@UserRouter.patch("/{user_id}", response_model=Response[UserPublic])
@tracer.observe()
async def update_user(
    user_id: UUID,
    user: UserUpdate,
    logger: Logger,
    user_service: Annotated[UserService, Depends()],
):
    """Update a user by ID."""
    logger.info({"message": "Updating user", "user_id": str(user_id)})
    result = await user_service.update(user_id, user)
    return Response(
        status_code=200,
        message="User updated",
        data=UserPublic.model_validate(result),
    )


@UserRouter.delete("/{user_id}", response_model=Response)
@tracer.observe()
async def delete_user(
    user_id: UUID,
    logger: Logger,
    user_service: Annotated[UserService, Depends()],
):
    """Delete a user by ID."""
    logger.info({"message": "Deleting user", "user_id": str(user_id)})
    await user_service.delete(user_id)
    return Response(
        status_code=200,
        message="User deleted",
        data=None,
    )
