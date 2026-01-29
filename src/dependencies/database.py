from typing import Annotated
from urllib.parse import quote

from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from .config import Config, get_config
from .logger import Logger, get_logger

config: Config = get_config()
logger: Logger = get_logger()

_engine: AsyncEngine | None = None


def get_engine() -> AsyncEngine:
    global _engine

    if _engine is None:
        url = config.database.url
        if not url:
            url = (
                f"{config.database.kind}+{config.database.adapter}://"
                f"{config.database.username}:{quote(config.database.password)}@"
                f"{config.database.host}:{config.database.port}/"
                f"{config.database.name}"
            )

        logger.info(f"creating database engine: {url}")

        _engine = create_async_engine(
            url=url,
            echo=config.logging.level == "debug",
            future=True,
            pool_size=20,
            max_overflow=10,
        )

    return _engine


async def init():
    import asyncio

    from alembic import command
    from alembic.config import Config as AlembicConfig

    await asyncio.to_thread(
        command.upgrade, config=AlembicConfig("alembic.ini"), revision="head"
    )


async def close():
    global _engine
    if _engine:
        await _engine.dispose()
        _engine = None


async def aget_session() -> AsyncSession:
    engine = get_engine()
    session = sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )

    async with session() as session:
        yield session


Database = Annotated[AsyncSession, Depends(aget_session)]
