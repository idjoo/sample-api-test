import logging
import sys
from typing import Annotated

from fastapi import Depends

from .config import Config, get_config

config: Config = get_config()


async def init():
    """Initialize the logger with structured output."""
    logger = logging.getLogger(config.service)
    logger.setLevel(config.logging.level.upper())

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(config.logging.level.upper())
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)


async def aget_logger() -> logging.Logger:
    return logging.getLogger(config.service)


def get_logger() -> logging.Logger:
    return logging.getLogger(config.service)


Logger = Annotated[logging.Logger, Depends(aget_logger)]
