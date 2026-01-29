from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Response[T](BaseModel):
    status: int = 200
    message: str = ""
    data: T | None
