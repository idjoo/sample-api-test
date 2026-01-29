from importlib import metadata
from typing import Annotated

from fastapi import Depends

from src.dependencies import Config
from src.repositories import HealthRepository
from src.schemas import HealthCheck


class HealthService:
    config: Config
    health_repository: HealthRepository

    def __init__(
        self,
        config: Config,
        health_repository: Annotated[HealthRepository, Depends()],
    ) -> None:
        self.config = config
        self.health_repository = health_repository

    async def check(
        self,
    ) -> HealthCheck:
        health_check = HealthCheck()
        health_check.status = "HANANABUBU"
        if await self.health_repository.check():
            health_check.status = "OK"
        health_check.version = metadata.version(self.config.service)
        return health_check
