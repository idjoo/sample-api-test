from typing import Annotated

from fastapi import APIRouter, Depends, status

from src.schemas import HealthCheck
from src.services import HealthService

HealthRouter = APIRouter(
    tags=["health"],
)


@HealthRouter.get(
    "/health",
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
)
async def health(
    health_service: Annotated[HealthService, Depends()],
) -> HealthCheck:
    """
    ## Perform a Health Check
    Endpoint to perform a healthcheck on. This endpoint can primarily be used Docker
    to ensure a robust container orchestration and management is in place. Other
    services which rely on proper functioning of the API service will not deploy if this
    endpoint returns any other HTTP status code except 200 (OK).
    Returns:
        HealthCheck: Returns a JSON response with the health status
    """
    return await health_service.check()
