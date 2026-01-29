from decimal import Decimal
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.dependencies.database import get_session
from src.exceptions.item_exception import ItemNotFoundError
from src.models.product_model import Product


class ProductRepository:
    """Repository for Product database operations."""

    def __init__(self, session: Annotated[AsyncSession, Depends(get_session)]):
        self.session = session

    async def create(self, product: Product) -> Product:
        """Create a new product."""
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        return product

    async def get_by_id(self, product_id: UUID) -> Product:
        """Get a product by ID."""
        result = await self.session.get(Product, product_id)
        if not result:
            raise ItemNotFoundError(f"Product {product_id} not found")
        return result

    async def list_filtered(
        self,
        category: str | None = None,
        is_active: bool | None = None,
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
    ) -> list[Product]:
        """List products with optional filters."""
        query = select(Product)

        if category:
            query = query.where(Product.category == category)
        if is_active is not None:
            query = query.where(Product.is_active == is_active)
        if min_price is not None:
            query = query.where(Product.price >= min_price)
        if max_price is not None:
            query = query.where(Product.price <= max_price)

        result = await self.session.exec(query)
        return list(result.all())

    async def update(self, product: Product) -> Product:
        """Update a product."""
        self.session.add(product)
        await self.session.commit()
        await self.session.refresh(product)
        return product

    async def delete(self, product: Product) -> None:
        """Delete a product."""
        await self.session.delete(product)
        await self.session.commit()
