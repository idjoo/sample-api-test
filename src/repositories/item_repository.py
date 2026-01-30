from uuid import UUID

from fastapi_pagination.ext.sqlmodel import paginate
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlmodel import delete, insert, select, update

from src.dependencies import Database, Logger, tracer
from src.exceptions import BaseError
from src.exceptions.item_exception import ItemAlreadyExistsError, ItemNotFoundError
from src.models.item_model import Item, ItemCreate, ItemStats, ItemUpdate
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
    async def get_stats(self) -> ItemStats:
        """Get aggregate statistics about all items."""
        try:
            # Get basic counts and aggregates
            result = await self.db.exec(
                select(
                    func.count(Item.id).label("total_items"),
                    func.coalesce(func.sum(Item.quantity), 0).label("total_quantity"),
                    func.coalesce(func.sum(Item.price * Item.quantity), Decimal("0.00")).label("total_value"),
                    func.coalesce(func.avg(Item.price), Decimal("0.00")).label("average_price"),
                )
            )
            row = result.one()

            # Get category breakdown
            category_result = await self.db.exec(
                select(Item.category, func.count(Item.id))
                .group_by(Item.category)
            )
            categories = {
                cat or "uncategorized": count
                for cat, count in category_result.all()
            }

            return ItemStats(
                total_items=row.total_items or 0,
                total_quantity=row.total_quantity or 0,
                total_value=Decimal(str(row.total_value or 0)),
                categories=categories,
                average_price=Decimal(str(round(row.average_price or 0, 2))),
            )
        except Exception as error:
            self.logger.error(
                {
                    "message": "Database error during get_stats",
                    "error": str(error),
                },
                exc_info=True,
            )
            raise BaseError("Database Internal Error") from error
