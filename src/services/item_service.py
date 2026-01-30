from typing import Annotated
from uuid import UUID

from fastapi import Depends

from src.dependencies import Logger, tracer
from src.exceptions.user_exception import ForbiddenError
from src.models.item_model import Item, ItemCreate, ItemStats, ItemUpdate
from src.repositories.item_repository import ItemRepository
from src.schemas import Page


class ItemService:
    item_repository: ItemRepository
    logger: Logger

    def __init__(
        self,
        item_repository: Annotated[ItemRepository, Depends()],
        logger: Logger,
    ) -> None:
        self.item_repository = item_repository
        self.logger = logger

    @tracer.observe()
    async def create(self, item: ItemCreate, owner_id: UUID) -> Item:
        async with tracer.track(
            "logic:create_item", attributes={"item.name": item.name}
        ) as span:
            try:
                self.logger.info(
                    {
                        "message": "Starting item creation",
                        "name": item.name,
                        "owner_id": str(owner_id),
                    }
                )
                result = await self.item_repository.create(item, owner_id)
                span.set_attribute("item.id", str(result.id))
                return result
            except Exception as e:
                self.logger.error(
                    {
                        "message": "Failed to create item",
                        "error": str(e),
                    }
                )
                span.record_exception(e)
                raise

    @tracer.observe()
    async def read_all(self, owner_id: UUID | None = None) -> Page[Item]:
        async with tracer.track("logic:read_all_items") as span:
            self.logger.debug(
                {"message": "Fetching items", "owner_id": str(owner_id) if owner_id else None}
            )
            result = await self.item_repository.read_all(owner_id=owner_id)
            span.set_attribute("items.count", len(result.items))
            return result

    @tracer.observe()
    async def read(self, id: UUID) -> Item:
        self.logger.debug({"message": "Reading item", "item_id": str(id)})
        return await self.item_repository.read(id=id)

    @tracer.observe()
    async def update(
        self, id: UUID, item: ItemUpdate, current_user_id: UUID
    ) -> Item:
        existing = await self.item_repository.read(id)
        if existing.owner_id != current_user_id:
            self.logger.warning(
                {
                    "message": "User attempted to update item they don't own",
                    "item_id": str(id),
                    "owner_id": str(existing.owner_id),
                    "current_user_id": str(current_user_id),
                }
            )
            raise ForbiddenError()
        self.logger.debug(
            {
                "message": "Updating item",
                "item_id": str(id),
                "update_data": item.model_dump(mode="json", exclude_none=True),
            }
        )
        return await self.item_repository.update(id, item)

    @tracer.observe()
    async def delete(self, id: UUID, current_user_id: UUID) -> None:
        existing = await self.item_repository.read(id)
        if existing.owner_id != current_user_id:
            self.logger.warning(
                {
                    "message": "User attempted to delete item they don't own",
                    "item_id": str(id),
                    "owner_id": str(existing.owner_id),
                    "current_user_id": str(current_user_id),
                }
            )
            raise ForbiddenError()
        self.logger.debug({"message": "Deleting item", "item_id": str(id)})
        return await self.item_repository.delete(id=id)

    @tracer.observe()
    async def get_stats(self) -> ItemStats:
        """Get aggregate statistics about all items."""
        self.logger.debug({"message": "Computing item statistics"})
        return await self.item_repository.get_stats()
