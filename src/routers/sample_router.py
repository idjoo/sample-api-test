from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.dependencies import Logger, tracer
from src.models import (
    SampleCreate,
    SamplePublic,
    SampleUpdate,
)
from src.schemas import Page, Response
from src.services import SampleService

SampleRouter = APIRouter(
    prefix="/samples",
    tags=["sample"],
)


@SampleRouter.post("/")
@tracer.observe()
async def create(
    logger: Logger,
    sample_service: Annotated[SampleService, Depends()],
    sample: SampleCreate,
) -> Response[SamplePublic]:
    logger.info(
        {
            "message": "Creating a new sample",
            "sample": sample.model_dump(mode="json"),
        }
    )
    data = await sample_service.create(sample)
    logger.info(
        {
            "message": "Sample created successfully",
            "sample": data.model_dump(mode="json"),
        }
    )
    return Response(
        status=status.HTTP_200_OK,
        message="Sample created successfully",
        data=data,
    )


@SampleRouter.get("/")
@tracer.observe()
async def read_all(
    logger: Logger,
    sample_service: Annotated[SampleService, Depends()],
) -> Page[SamplePublic]:
    logger.info({"message": "Reading all samples"})
    data = await sample_service.read_all()
    return data


@SampleRouter.get("/{id}")
@tracer.observe()
async def read(
    logger: Logger,
    sample_service: Annotated[SampleService, Depends()],
    id: UUID,
) -> Response[SamplePublic]:
    logger.info(
        {
            "message": "Reading sample by ID",
            "sample_id": str(id),
        }
    )
    data = await sample_service.read(id)
    return Response(
        status=status.HTTP_200_OK,
        message="Success",
        data=data,
    )


@SampleRouter.patch("/{id}")
@tracer.observe()
async def update(
    logger: Logger,
    sample_service: Annotated[SampleService, Depends()],
    id: UUID,
    sample: SampleUpdate,
) -> Response[SamplePublic]:
    logger.info(
        {
            "message": "Updating sample",
            "sample_id": str(id),
            "update_data": sample.model_dump(exclude_none=True),
        }
    )
    data = await sample_service.update(id, sample)
    logger.info(
        {
            "message": "Sample updated successfully",
            "sample": data.model_dump(mode="json"),
        }
    )
    return Response(
        status=status.HTTP_200_OK,
        message="Successfully updated",
        data=data,
    )


@SampleRouter.delete("/{id}")
@tracer.observe()
async def delete(
    logger: Logger,
    sample_service: Annotated[SampleService, Depends()],
    id: UUID,
) -> Response:
    logger.info(
        {
            "message": "Deleting sample",
            "sample_id": str(id),
        }
    )
    await sample_service.delete(id)
    logger.info(
        {
            "message": "Sample deleted successfully",
            "sample_id": str(id),
        }
    )
    return Response(
        status=status.HTTP_200_OK,
        message="Successfully deleted",
        data=None,
    )
