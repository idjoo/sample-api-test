from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class ProductBase(SQLModel):
    """Base fields for Product."""

    name: str = Field(max_length=255, index=True)
    description: str | None = Field(default=None, max_length=1000)
    price: Decimal = Field(default=Decimal("0.00"), ge=0, decimal_places=2)
    stock: int = Field(default=0, ge=0)
    category: str | None = Field(default=None, max_length=100)
    is_active: bool = Field(default=True)


class Product(ProductBase, table=True):
    """Product database model."""

    __tablename__: str = "products"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class ProductCreate(ProductBase):
    """Schema for creating a product."""

    pass


class ProductUpdate(SQLModel):
    """Schema for updating a product."""

    name: str | None = None
    description: str | None = None
    price: Decimal | None = None
    stock: int | None = None
    category: str | None = None
    is_active: bool | None = None


class ProductPublic(ProductBase):
    """Public product response schema."""

    id: UUID
    created_at: datetime
