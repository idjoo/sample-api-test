from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    username: str = Field(index=True, unique=True, max_length=50)
    email: str = Field(index=True, max_length=255)
    is_admin: bool = Field(default=False)


class User(UserBase, table=True):
    __tablename__: str = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    password_hash: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column_kwargs={"onupdate": datetime.now},
    )


class UserCreate(SQLModel):
    username: str = Field(max_length=50)
    email: str = Field(max_length=255)
    password: str = Field(min_length=8, max_length=100)
    is_admin: bool = Field(default=False)


class UserPublic(SQLModel):
    id: UUID
    username: str
    email: str
    is_admin: bool
    created_at: datetime


class UserUpdate(SQLModel):
    username: str | None = None
    email: str | None = None
    is_admin: bool | None = None
