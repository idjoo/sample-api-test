from typing import Annotated

from fastapi import Depends
from httpx import AsyncClient

_client: AsyncClient | None = None


async def init():
    global _client
    if _client is None:
        _client = AsyncClient(timeout=60)


async def close():
    global _client
    if _client:
        await _client.aclose()
        _client = None


async def aget_client() -> AsyncClient:
    global _client
    if _client is None:
        await init()
    return _client


HttpClient = Annotated[AsyncClient, Depends(aget_client)]
