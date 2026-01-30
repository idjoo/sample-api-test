"""Category service for business logic."""

from typing import Annotated
from uuid import UUID

from fastapi import Depends

from src.dependencies import Logger, tracer
from src.models.category_model import (
    Category,
    CategoryCreate,
    CategoryStats,
    CategoryUpdate,
)
from src.repositories.category_repository import CategoryRepository
from src.schemas import Page


class CategoryService:
    """Service for category business operations."""

    category_repository: CategoryRepository
    logger: Logger

    def __init__(
        self,
        category_repository: Annotated[CategoryRepository, Depends()],
        logger: Logger,
    ) -> None:
        self.category_repository = category_repository
        self.logger = logger

    @tracer.observe()
    async def create(self, category: CategoryCreate, created_by: UUID | None = None) -> Category:
        """Create a new category."""
        async with tracer.track(
            "logic:create_category", attributes={"category.name": category.name}
        ) as span:
            try:
                self.logger.info(
                    {
                        "message": "Starting category creation",
                        "name": category.name,
                        "created_by": str(created_by) if created_by else None,
                    }
                )
                result = await self.category_repository.create(category, created_by)
                span.set_attribute("category.id", str(result.id))
                return result
            except Exception as e:
                self.logger.error(
                    {
                        "message": "Failed to create category",
                        "error": str(e),
                    }
                )
                span.record_exception(e)
                raise

    @tracer.observe()
    async def read_all(self, active_only: bool = False) -> Page[Category]:
        """Read all categories."""
        async with tracer.track("logic:read_all_categories") as span:
            self.logger.debug(
                {"message": "Fetching categories", "active_only": active_only}
            )
            result = await self.category_repository.read_all(active_only=active_only)
            span.set_attribute("categories.count", len(result.items))
            return result

    @tracer.observe()
    async def read(self, id: UUID) -> Category:
        """Read a single category by ID."""
        self.logger.debug({"message": "Reading category", "category_id": str(id)})
        return await self.category_repository.read(id=id)

    @tracer.observe()
    async def read_by_name(self, name: str) -> Category | None:
        """Read a category by name."""
        self.logger.debug({"message": "Reading category by name", "name": name})
        return await self.category_repository.read_by_name(name=name)

    @tracer.observe()
    async def update(self, id: UUID, category: CategoryUpdate) -> Category:
        """Update a category."""
        self.logger.debug(
            {
                "message": "Updating category",
                "category_id": str(id),
                "update_data": category.model_dump(mode="json", exclude_none=True),
            }
        )
        return await self.category_repository.update(id, category)

    @tracer.observe()
    async def delete(self, id: UUID) -> None:
        """Delete a category."""
        self.logger.debug({"message": "Deleting category", "category_id": str(id)})
        return await self.category_repository.delete(id=id)

    @tracer.observe()
    async def get_stats(self) -> CategoryStats:
        """Get category statistics."""
        self.logger.debug({"message": "Getting category statistics"})
        return await self.category_repository.get_stats()

    @tracer.observe()
    async def toggle_active(self, id: UUID) -> Category:
        """Toggle the active status of a category."""
        category = await self.category_repository.read(id)
        update_data = CategoryUpdate(is_active=not category.is_active)
        self.logger.info(
            {
                "message": "Toggling category active status",
                "category_id": str(id),
                "old_status": category.is_active,
                "new_status": not category.is_active,
            }
        )
        return await self.category_repository.update(id, update_data)

    @tracer.observe()
    async def reorder(self, id: UUID, new_order: int) -> Category:
        """Update the sort order of a category."""
        self.logger.info(
            {
                "message": "Reordering category",
                "category_id": str(id),
                "new_order": new_order,
            }
        )
        update_data = CategoryUpdate(sort_order=new_order)
        return await self.category_repository.update(id, update_data)
