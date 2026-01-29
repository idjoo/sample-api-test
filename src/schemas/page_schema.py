from typing import TypeVar

from fastapi import Query
from fastapi_pagination import Page as BasePage
from fastapi_pagination.customization import CustomizedPage, UseParamsFields

T = TypeVar("T")


Page = CustomizedPage[
    BasePage[T],
    UseParamsFields(
        size=Query(100, ge=1, le=500),
    ),
]
