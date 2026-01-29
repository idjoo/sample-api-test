from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class ItemBase(SQLModel):
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    price: Decimal = Field(default=Decimal("0.00"), decimal_places=2)
    quantity: int = Field(default=0, ge=0)
    category: str | None = Field(default=None, max_length=100)


class Item(ItemBase, table=True):
    __tablename__: str = "items"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    owner_id: UUID = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column_kwargs={"onupdate": datetime.now},
    )


class ItemCreate(ItemBase):
    pass


class ItemPublic(ItemBase):
    id: UUID
    owner_id: UUID
    created_at: datetime


class ItemUpdate(SQLModel):
    name: str | None = None
    description: str | None = None
    price: Decimal | None = None
    quantity: int | None = None
    category: str | None = None
