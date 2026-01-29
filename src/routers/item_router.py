from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header

from src.dependencies import Logger, tracer
from src.exceptions.user_exception import UnauthorizedError
from src.models.item_model import ItemCreate, ItemPublic, ItemUpdate
from src.schemas import Page, Response
from src.services.auth_service import AuthService
from src.services.item_service import ItemService

ItemRouter = APIRouter(prefix="/api/items", tags=["Items"])


async def get_current_user_id(
    authorization: Annotated[str | None, Header()] = None,
    auth_service: AuthService = Depends(),
) -> UUID:
    """Extract and validate the current user from Authorization header."""
    if not authorization:
        raise UnauthorizedError()
    if not authorization.startswith("Bearer "):
        raise UnauthorizedError()
    token = authorization[7:]
    return await auth_service.validate_token(token)


@ItemRouter.post("/", response_model=Response[ItemPublic])
@tracer.observe()
async def create_item(
    item: ItemCreate,
    logger: Logger,
    item_service: Annotated[ItemService, Depends()],
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
):
    """Create a new item (requires authentication)."""
    logger.info(
        {
            "message": "Creating new item",
            "name": item.name,
            "owner_id": str(current_user_id),
        }
    )
    result = await item_service.create(item, current_user_id)
    return Response(
        status_code=201,
        message="Item created",
        data=ItemPublic.model_validate(result),
    )


@ItemRouter.get("/", response_model=Page[ItemPublic])
@tracer.observe()
async def read_items(
    logger: Logger,
    item_service: Annotated[ItemService, Depends()],
    owner_id: UUID | None = None,
):
    """Get all items (paginated). Optionally filter by owner."""
    logger.debug(
        {"message": "Fetching items", "owner_id": str(owner_id) if owner_id else None}
    )
    return await item_service.read_all(owner_id=owner_id)


@ItemRouter.get("/{item_id}", response_model=Response[ItemPublic])
@tracer.observe()
async def read_item(
    item_id: UUID,
    logger: Logger,
    item_service: Annotated[ItemService, Depends()],
):
    """Get an item by ID."""
    logger.debug({"message": "Fetching item", "item_id": str(item_id)})
    result = await item_service.read(item_id)
    return Response(
        status_code=200,
        message="Item retrieved",
        data=ItemPublic.model_validate(result),
    )


@ItemRouter.patch("/{item_id}", response_model=Response[ItemPublic])
@tracer.observe()
async def update_item(
    item_id: UUID,
    item: ItemUpdate,
    logger: Logger,
    item_service: Annotated[ItemService, Depends()],
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
):
    """Update an item by ID (only owner can update)."""
    logger.info({"message": "Updating item", "item_id": str(item_id)})
    result = await item_service.update(item_id, item, current_user_id)
    return Response(
        status_code=200,
        message="Item updated",
        data=ItemPublic.model_validate(result),
    )


@ItemRouter.delete("/{item_id}", response_model=Response)
@tracer.observe()
async def delete_item(
    item_id: UUID,
    logger: Logger,
    item_service: Annotated[ItemService, Depends()],
    current_user_id: Annotated[UUID, Depends(get_current_user_id)],
):
    """Delete an item by ID (only owner can delete)."""
    logger.info({"message": "Deleting item", "item_id": str(item_id)})
    await item_service.delete(item_id, current_user_id)
    return Response(
        status_code=200,
        message="Item deleted",
        data=None,
    )
