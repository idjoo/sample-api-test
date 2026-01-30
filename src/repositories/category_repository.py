"""Category repository for database operations."""

from uuid import UUID

from fastapi_pagination.ext.sqlmodel import paginate
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlmodel import delete, insert, select, update

from src.dependencies import Database, Logger, tracer
from src.exceptions import BaseError
from src.models.category_model import (
    Category,
    CategoryCreate,
    CategoryStats,
    CategoryUpdate,
)
from src.schemas import Page


class CategoryAlreadyExistsError(BaseError):
    """Raised when a category with the same name already exists."""

    def __init__(self):
        super().__init__("Category with this name already exists")
        self.status_code = 409


class CategoryNotFoundError(BaseError):
    """Raised when a category is not found."""

    def __init__(self):
        super().__init__("Category not found")
        self.status_code = 404


class CategoryRepository:
    """Repository for category database operations."""

    db: Database
    logger: Logger

    def __init__(self, db: Database, logger: Logger) -> None:
        self.db = db
        self.logger = logger

    @tracer.observe()
    async def create(self, category: CategoryCreate, created_by: UUID | None = None) -> Category:
        """Create a new category."""
        try:
            data = Category(
                name=category.name,
                description=category.description,
                color=category.color,
                icon=category.icon,
                is_active=category.is_active,
                sort_order=category.sort_order,
                created_by=created_by,
            )
            result = (
                await self.db.scalars(
                    insert(Category).values(data.model_dump()).returning(Category),
                )
            ).one()
            await self.db.commit()
            self.logger.debug(
                {
                    "message": "Category created in DB",
                    "category_id": str(result.id),
                    "name": result.name,
                }
            )
            return result
        except IntegrityError as error:
            self.logger.warning(
                {
                    "message": "Category creation failed: constraint violation",
                    "name": category.name,
                    "error": str(error),
                }
            )
            raise CategoryAlreadyExistsError() from error
        except Exception as error:
            self.logger.error(
                {
                    "message": "Database error during category creation",
                    "error": str(error),
                },
                exc_info=True,
            )
            raise BaseError("Database Internal Error") from error

    @tracer.observe()
    async def read_all(self, active_only: bool = False) -> Page[Category]:
        """Read all categories with optional filtering."""
        try:
            query = select(Category).order_by(Category.sort_order, Category.name)
            if active_only:
                query = query.where(Category.is_active == True)
            return await paginate(self.db, query)
        except Exception as error:
            self.logger.error(
                {
                    "message": "Database error during read_all categories",
                    "error": str(error),
                },
                exc_info=True,
            )
            raise BaseError("Database Internal Error") from error

    @tracer.observe()
    async def read(self, id: UUID) -> Category:
        """Read a single category by ID."""
        try:
            result = (
                await self.db.exec(select(Category).where(Category.id == id))
            ).one()
            return result
        except NoResultFound as error:
            self.logger.warning(
                {
                    "message": "Category not found",
                    "category_id": str(id),
                }
            )
            raise CategoryNotFoundError() from error
        except Exception as error:
            self.logger.error(
                {
                    "message": "Database error during category read",
                    "error": str(error),
                },
                exc_info=True,
            )
            raise BaseError("Database Internal Error") from error

    @tracer.observe()
    async def read_by_name(self, name: str) -> Category | None:
        """Read a category by name."""
        try:
            result = await self.db.exec(
                select(Category).where(Category.name == name)
            )
            return result.one_or_none()
        except Exception as error:
            self.logger.error(
                {
                    "message": "Database error during category read by name",
                    "error": str(error),
                },
                exc_info=True,
            )
            raise BaseError("Database Internal Error") from error

    @tracer.observe()
    async def update(self, id: UUID, category: CategoryUpdate) -> Category:
        """Update a category."""
        try:
            result = (
                await self.db.scalars(
                    update(Category)
                    .where(Category.id == id)
                    .values(category.model_dump(mode="json", exclude_none=True))
                    .returning(Category),
                )
            ).one()
            await self.db.commit()
            self.logger.debug(
                {
                    "message": "Category updated in DB",
                    "category_id": str(result.id),
                }
            )
            return result
        except NoResultFound as error:
            raise CategoryNotFoundError() from error
        except IntegrityError as error:
            self.logger.warning(
                {
                    "message": "Category update failed: constraint violation",
                    "category_id": str(id),
                    "error": str(error),
                }
            )
            raise CategoryAlreadyExistsError() from error
        except Exception as error:
            self.logger.error(
                {
                    "message": "Database error during category update",
                    "error": str(error),
                },
                exc_info=True,
            )
            raise BaseError("Database Internal Error") from error

    @tracer.observe()
    async def delete(self, id: UUID) -> None:
        """Delete a category."""
        try:
            await self.db.exec(delete(Category).where(Category.id == id))
            await self.db.commit()
            self.logger.debug(
                {
                    "message": "Category deleted from DB",
                    "category_id": str(id),
                }
            )
        except Exception as error:
            self.logger.error(
                {
                    "message": "Database error during category delete",
                    "error": str(error),
                },
                exc_info=True,
            )
            raise BaseError("Database Internal Error") from error

    @tracer.observe()
    async def get_stats(self) -> CategoryStats:
        """Get category statistics."""
        try:
            # Get total and active counts
            result = await self.db.exec(
                select(
                    func.count(Category.id).label("total"),
                    func.sum(func.cast(Category.is_active, int)).label("active"),
                )
            )
            row = result.one()
            total = row.total or 0
            active = row.active or 0

            return CategoryStats(
                total_categories=total,
                active_categories=active,
                inactive_categories=total - active,
                categories_with_items=0,  # Would need join with items table
            )
        except Exception as error:
            self.logger.error(
                {
                    "message": "Database error during category stats",
                    "error": str(error),
                },
                exc_info=True,
            )
            raise BaseError("Database Internal Error") from error
