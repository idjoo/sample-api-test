"""Category router for API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query

from src.dependencies import Logger, tracer
from src.exceptions.user_exception import UnauthorizedError
from src.models.category_model import (
    CategoryCreate,
    CategoryPublic,
    CategoryStats,
    CategoryUpdate,
)
from src.schemas import Page, Response
from src.services.auth_service import AuthService
from src.services.category_service import CategoryService

CategoryRouter = APIRouter(prefix="/api/categories", tags=["Categories"])


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


async def get_optional_user_id(
    authorization: Annotated[str | None, Header()] = None,
    auth_service: AuthService = Depends(),
) -> UUID | None:
    """Optionally extract user ID from Authorization header."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization[7:]
    try:
        return await auth_service.validate_token(token)
    except Exception:
        return None


@CategoryRouter.post("/", response_model=Response[CategoryPublic])
@tracer.observe()
async def create_category(
    category: CategoryCreate,
    logger: Logger,
    category_service: Annotated[CategoryService, Depends()],
    current_user_id: Annotated[UUID | None, Depends(get_optional_user_id)] = None,
):
    """Create a new category."""
    logger.info(
        {
            "message": "Creating new category",
            "name": category.name,
            "created_by": str(current_user_id) if current_user_id else None,
        }
    )
    result = await category_service.create(category, current_user_id)
    return Response(
        status_code=201,
        message="Category created",
        data=CategoryPublic.model_validate(result),
    )


@CategoryRouter.get("/", response_model=Page[CategoryPublic])
@tracer.observe()
async def read_categories(
    logger: Logger,
    category_service: Annotated[CategoryService, Depends()],
    active_only: bool = Query(False, description="Only return active categories"),
):
    """Get all categories (paginated)."""
    logger.debug({"message": "Fetching categories", "active_only": active_only})
    return await category_service.read_all(active_only=active_only)


@CategoryRouter.get("/stats", response_model=Response[CategoryStats])
@tracer.observe()
async def get_category_stats(
    logger: Logger,
    category_service: Annotated[CategoryService, Depends()],
):
    """Get category statistics."""
    logger.debug({"message": "Getting category statistics"})
    stats = await category_service.get_stats()
    return Response(
        status_code=200,
        message="Category statistics retrieved",
        data=stats,
    )


@CategoryRouter.get("/search", response_model=Response[CategoryPublic | None])
@tracer.observe()
async def search_category_by_name(
    name: str,
    logger: Logger,
    category_service: Annotated[CategoryService, Depends()],
):
    """Search for a category by name."""
    logger.debug({"message": "Searching category by name", "name": name})
    result = await category_service.read_by_name(name)
    return Response(
        status_code=200,
        message="Category search completed",
        data=CategoryPublic.model_validate(result) if result else None,
    )


@CategoryRouter.get("/{category_id}", response_model=Response[CategoryPublic])
@tracer.observe()
async def read_category(
    category_id: UUID,
    logger: Logger,
    category_service: Annotated[CategoryService, Depends()],
):
    """Get a category by ID."""
    logger.debug({"message": "Fetching category", "category_id": str(category_id)})
    result = await category_service.read(category_id)
    return Response(
        status_code=200,
        message="Category retrieved",
        data=CategoryPublic.model_validate(result),
    )


@CategoryRouter.patch("/{category_id}", response_model=Response[CategoryPublic])
@tracer.observe()
async def update_category(
    category_id: UUID,
    category: CategoryUpdate,
    logger: Logger,
    category_service: Annotated[CategoryService, Depends()],
):
    """Update a category by ID."""
    logger.info({"message": "Updating category", "category_id": str(category_id)})
    result = await category_service.update(category_id, category)
    return Response(
        status_code=200,
        message="Category updated",
        data=CategoryPublic.model_validate(result),
    )


@CategoryRouter.post("/{category_id}/toggle", response_model=Response[CategoryPublic])
@tracer.observe()
async def toggle_category_active(
    category_id: UUID,
    logger: Logger,
    category_service: Annotated[CategoryService, Depends()],
):
    """Toggle the active status of a category."""
    logger.info({"message": "Toggling category active status", "category_id": str(category_id)})
    result = await category_service.toggle_active(category_id)
    return Response(
        status_code=200,
        message="Category status toggled",
        data=CategoryPublic.model_validate(result),
    )


@CategoryRouter.post("/{category_id}/reorder", response_model=Response[CategoryPublic])
@tracer.observe()
async def reorder_category(
    category_id: UUID,
    new_order: int,
    logger: Logger,
    category_service: Annotated[CategoryService, Depends()],
):
    """Update the sort order of a category."""
    logger.info(
        {
            "message": "Reordering category",
            "category_id": str(category_id),
            "new_order": new_order,
        }
    )
    result = await category_service.reorder(category_id, new_order)
    return Response(
        status_code=200,
        message="Category reordered",
        data=CategoryPublic.model_validate(result),
    )


@CategoryRouter.delete("/{category_id}", response_model=Response)
@tracer.observe()
async def delete_category(
    category_id: UUID,
    logger: Logger,
    category_service: Annotated[CategoryService, Depends()],
):
    """Delete a category by ID."""
    logger.info({"message": "Deleting category", "category_id": str(category_id)})
    await category_service.delete(category_id)
    return Response(
        status_code=200,
        message="Category deleted",
        data=None,
    )
