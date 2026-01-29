from typing import Annotated
from uuid import UUID

from fastapi import Depends

from src.dependencies import Logger, tracer
from src.models import (
    Sample,
    SampleCreate,
    SampleUpdate,
)
from src.repositories import SampleRepository
from src.schemas import Page


class SampleService:
    sample_repository: SampleRepository
    logger: Logger

    def __init__(
        self,
        sample_repository: Annotated[SampleRepository, Depends()],
        logger: Logger,
    ) -> None:
        self.sample_repository = sample_repository
        self.logger = logger

    @tracer.observe()
    async def create(
        self,
        sample: SampleCreate,
    ) -> Sample:
        async with tracer.track(
            "logic:create_sample", attributes={"sample.name": sample.name}
        ) as span:
            try:
                self.logger.info(
                    {
                        "message": "Starting sample creation logic",
                        "sample": sample.model_dump(mode="json"),
                    }
                )
                result = await self.sample_repository.create(sample)
                span.set_attribute("sample.id", str(result.id))
                return result
            except Exception as e:
                self.logger.error(
                    {
                        "message": "Failed to create sample in logic layer",
                        "error": str(e),
                    }
                )
                span.record_exception(e)
                raise

    @tracer.observe()
    async def read_all(
        self,
    ) -> Page[Sample]:
        async with tracer.track("logic:read_all_samples") as span:
            self.logger.debug(
                {"message": "Fetching all samples from repository"}
            )
            result = await self.sample_repository.read_all()
            span.set_attribute("samples.count", len(result.items))
            return result

    @tracer.observe()
    async def read(
        self,
        id: UUID,
    ) -> Sample | None:
        self.logger.debug(
            {
                "message": "Calling repository to read sample",
                "sample_id": str(id),
            }
        )
        return await self.sample_repository.read(id=id)

    @tracer.observe()
    async def update(
        self,
        id: UUID,
        sample: SampleUpdate,
    ) -> Sample:
        self.logger.debug(
            {
                "message": "Calling repository to update sample",
                "sample_id": str(id),
                "update_data": sample.model_dump(
                    mode="json", exclude_none=True
                ),
            }
        )
        return await self.sample_repository.update(id, sample)

    @tracer.observe()
    async def delete(
        self,
        id: UUID,
    ) -> None:
        self.logger.debug(
            {
                "message": "Calling repository to delete sample",
                "sample_id": str(id),
            }
        )
        return await self.sample_repository.delete(id=id)
