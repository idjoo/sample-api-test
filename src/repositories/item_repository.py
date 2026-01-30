from uuid import UUID

from fastapi_pagination.ext.sqlmodel import paginate
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlmodel import delete, insert, select, update

from src.dependencies import Database, Logger, tracer
from src.exceptions import BaseError
from src.exceptions.item_exception import ItemAlreadyExistsError, ItemNotFoundError
from src.models.item_model import Item, ItemCreate, ItemUpdate
from src.schemas import Page


class ItemRepository:
    db: Database
    logger: Logger

    def __init__(self, db: Database, logger: Logger) -> None:
        self.db = db
        self.logger = logger

    @tracer.observe()
    async def create(self, item: ItemCreate, owner_id: UUID) -> Item:
        try:
            data = Item(
                name=item.name,
                description=item.description,
                price=item.price,
                quantity=item.quantity,
                category=item.category,
                owner_id=owner_id,
            )
            result = (
                await self.db.scalars(
                    insert(Item).values(data.model_dump()).returning(Item),
                )
            ).one()
            await self.db.commit()
            self.logger.debug(
                {
                    "message": "Item created in DB",
                    "item_id": str(result.id),
                    "name": result.name,
                }
            )
            return result
        except IntegrityError as error:
            self.logger.warning(
                {
                    "message": "Item creation failed: constraint violation",
                    "name": item.name,
                    "error": str(error),
                }
            )
            raise ItemAlreadyExistsError() from error
        except Exception as error:
            self.logger.error(
                {
                    "message": "Database error during item creation",
                    "error": str(error),
                },
                exc_info=True,
            )
            raise BaseError("Database Internal Error") from error

    @tracer.observe()
    async def read_all(self, owner_id: UUID | None = None) -> Page[Item]:
        try:
            query = select(Item)
            if owner_id:
                query = query.where(Item.owner_id == owner_id)
            return await paginate(self.db, query)
        except Exception as error:
            self.logger.error(
                {
                    "message": "Database error during read_all items",
                    "error": str(error),
                },
                exc_info=True,
            )
            raise BaseError("Database Internal Error") from error

    @tracer.observe()
    async def read(self, id: UUID) -> Item:
        try:
            result = (
                await self.db.exec(select(Item).where(Item.id == id))
            ).one()
            return result
        except NoResultFound as error:
            self.logger.warning(
                {
                    "message": "Item not found",
                    "item_id": str(id),
                }
            )
            raise ItemNotFoundError() from error
        except Exception as error:
            self.logger.error(
                {
                    "message": "Database error during item read",
                    "error": str(error),
                },
                exc_info=True,
            )
            raise BaseError("Database Internal Error") from error

    @tracer.observe()
    async def update(self, id: UUID, item: ItemUpdate) -> Item:
        try:
            result = (
                await self.db.scalars(
                    update(Item)
                    .where(Item.id == id)
                    .values(item.model_dump(mode="json", exclude_none=True))
                    .returning(Item),
                )
            ).one()
            await self.db.commit()
            self.logger.debug(
                {
                    "message": "Item updated in DB",
                    "item_id": str(result.id),
                }
            )
            return result
        except NoResultFound as error:
            raise ItemNotFoundError() from error
        except Exception as error:
            self.logger.error(
                {
                    "message": "Database error during item update",
                    "error": str(error),
                },
                exc_info=True,
            )
            raise BaseError("Database Internal Error") from error

    @tracer.observe()
    async def delete(self, id: UUID) -> None:
        try:
            await self.db.exec(delete(Item).where(Item.id == id))
            await self.db.commit()
            self.logger.debug(
                {
                    "message": "Item deleted from DB",
                    "item_id": str(id),
                }
            )
        except Exception as error:
            self.logger.error(
                {
                    "message": "Database error during item delete",
                    "error": str(error),
                },
                exc_info=True,
            )
            raise BaseError("Database Internal Error") from error

    @tracer.observe()
    async def count(self) -> int:
        """Count total number of items."""
        try:
            result = await self.db.exec(select(func.count()).select_from(Item))
            return result.one()
        except Exception as error:
            self.logger.error(
                {
                    "message": "Database error during item count",
                    "error": str(error),
                },
                exc_info=True,
            )
            raise BaseError("Database Internal Error") from error
