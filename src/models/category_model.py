"""Category model definitions."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class CategoryBase(SQLModel):
    """Base category model with shared fields."""

    name: str = Field(max_length=100, unique=True)
    description: str | None = Field(default=None, max_length=500)
    color: str | None = Field(default=None, max_length=7)  # Hex color code
    icon: str | None = Field(default=None, max_length=50)
    is_active: bool = Field(default=True)
    sort_order: int = Field(default=0)


class Category(CategoryBase, table=True):
    """Category database model."""

    __tablename__: str = "categories"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column_kwargs={"onupdate": datetime.now},
    )
    created_by: UUID | None = Field(default=None, foreign_key="users.id")


class CategoryCreate(CategoryBase):
    """Model for creating a new category."""

    pass


class CategoryPublic(CategoryBase):
    """Public category model for API responses."""

    id: UUID
    created_at: datetime


class CategoryUpdate(SQLModel):
    """Model for updating a category."""

    name: str | None = None
    description: str | None = None
    color: str | None = None
    icon: str | None = None
    is_active: bool | None = None
    sort_order: int | None = None


class CategoryStats(SQLModel):
    """Statistics about categories."""

    total_categories: int
    active_categories: int
    inactive_categories: int
    categories_with_items: int
