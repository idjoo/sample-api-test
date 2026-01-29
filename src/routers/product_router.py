from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.dependencies import Logger, tracer
from src.models.product_model import ProductCreate, ProductPublic, ProductUpdate
from src.schemas import Page, Response
from src.services.product_service import ProductService

ProductRouter = APIRouter(prefix="/api/products", tags=["Products"])


@ProductRouter.post("/", response_model=Response[ProductPublic], status_code=201)
@tracer.observe()
async def create_product(
    product: ProductCreate,
    logger: Logger,
    product_service: Annotated[ProductService, Depends()],
):
    """Create a new product."""
    logger.info({"message": "Creating new product", "name": product.name})
    result = await product_service.create(product)
    return Response(
        status_code=201,
        message="Product created",
        data=ProductPublic.model_validate(result),
    )


@ProductRouter.get("/", response_model=Page[ProductPublic])
@tracer.observe()
async def list_products(
    logger: Logger,
    product_service: Annotated[ProductService, Depends()],
    category: str | None = Query(None, description="Filter by category"),
    is_active: bool | None = Query(None, description="Filter by active status"),
    min_price: float | None = Query(None, ge=0, description="Minimum price"),
    max_price: float | None = Query(None, ge=0, description="Maximum price"),
):
    """List all products with optional filters."""
    logger.debug({"message": "Listing products", "category": category})
    return await product_service.list_all(
        category=category,
        is_active=is_active,
        min_price=min_price,
        max_price=max_price,
    )


@ProductRouter.get("/{product_id}", response_model=Response[ProductPublic])
@tracer.observe()
async def get_product(
    product_id: UUID,
    logger: Logger,
    product_service: Annotated[ProductService, Depends()],
):
    """Get a product by ID."""
    logger.debug({"message": "Fetching product", "product_id": str(product_id)})
    result = await product_service.get(product_id)
    return Response(
        status_code=200,
        message="Product retrieved",
        data=ProductPublic.model_validate(result),
    )


@ProductRouter.patch("/{product_id}", response_model=Response[ProductPublic])
@tracer.observe()
async def update_product(
    product_id: UUID,
    product: ProductUpdate,
    logger: Logger,
    product_service: Annotated[ProductService, Depends()],
):
    """Update a product by ID."""
    logger.info({"message": "Updating product", "product_id": str(product_id)})
    result = await product_service.update(product_id, product)
    return Response(
        status_code=200,
        message="Product updated",
        data=ProductPublic.model_validate(result),
    )


@ProductRouter.delete("/{product_id}", response_model=Response)
@tracer.observe()
async def delete_product(
    product_id: UUID,
    logger: Logger,
    product_service: Annotated[ProductService, Depends()],
):
    """Delete a product by ID."""
    logger.info({"message": "Deleting product", "product_id": str(product_id)})
    await product_service.delete(product_id)
    return Response(
        status_code=200,
        message="Product deleted",
        data=None,
    )


@ProductRouter.post("/{product_id}/stock", response_model=Response[ProductPublic])
@tracer.observe()
async def update_stock(
    product_id: UUID,
    quantity: int,
    logger: Logger,
    product_service: Annotated[ProductService, Depends()],
):
    """Update product stock (add or subtract)."""
    logger.info({
        "message": "Updating product stock",
        "product_id": str(product_id),
        "quantity": quantity,
    })
    result = await product_service.update_stock(product_id, quantity)
    return Response(
        status_code=200,
        message="Stock updated",
        data=ProductPublic.model_validate(result),
    )
# Product API Test
