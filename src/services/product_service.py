from decimal import Decimal
from typing import Annotated
from uuid import UUID

from fastapi import Depends

from src.models.product_model import Product, ProductCreate, ProductUpdate
from src.repositories.product_repository import ProductRepository
from src.schemas import Page


class ProductService:
    """Service layer for Product operations."""

    def __init__(
        self,
        product_repo: Annotated[ProductRepository, Depends()],
    ):
        self.product_repo = product_repo

    async def create(self, product_data: ProductCreate) -> Product:
        """Create a new product."""
        product = Product(**product_data.model_dump())
        return await self.product_repo.create(product)

    async def get(self, product_id: UUID) -> Product:
        """Get a product by ID."""
        return await self.product_repo.get_by_id(product_id)

    async def list_all(
        self,
        category: str | None = None,
        is_active: bool | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
    ) -> Page[Product]:
        """List all products with optional filters."""
        products = await self.product_repo.list_filtered(
            category=category,
            is_active=is_active,
            min_price=Decimal(str(min_price)) if min_price else None,
            max_price=Decimal(str(max_price)) if max_price else None,
        )
        return Page(
            items=products,
            total=len(products),
            page=1,
            size=len(products),
            pages=1,
        )

    async def update(self, product_id: UUID, product_data: ProductUpdate) -> Product:
        """Update a product."""
        product = await self.product_repo.get_by_id(product_id)
        update_data = product_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)
        return await self.product_repo.update(product)

    async def delete(self, product_id: UUID) -> None:
        """Delete a product."""
        product = await self.product_repo.get_by_id(product_id)
        await self.product_repo.delete(product)

    async def update_stock(self, product_id: UUID, quantity: int) -> Product:
        """Update product stock by adding/subtracting quantity."""
        product = await self.product_repo.get_by_id(product_id)
        new_stock = product.stock + quantity
        if new_stock < 0:
            raise ValueError("Stock cannot be negative")
        product.stock = new_stock
        return await self.product_repo.update(product)
