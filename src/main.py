from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi_pagination import add_pagination

from src.dependencies import (
    Config,
    Environment,
    Logger,
    get_config,
    get_logger,
)
from src.exceptions import BaseError
from src.routers import (
    AuthRouter,
    HealthRouter,
    ItemRouter,
    SampleRouter,
    UserRouter,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from src.dependencies import database, http_client, logger, tracer

    await database.init()
    await tracer.init()
    await logger.init()
    await http_client.init()
    yield
    await http_client.close()
    await database.close()


config: Config = get_config()
logger: Logger = get_logger()


title = "Oracle Sample API - Swagger UI"


app = FastAPI(
    lifespan=lifespan,
    title=title,
    contact={
        "name": "Oracle Team",
        "url": "https://oracle.example.com",
        "email": "oracle@example.com",
    },
    description="Sample API for testing Oracle's API test generation capabilities",
    docs_url=None,
)


# ===============
# Middlewares
# ===============
add_pagination(app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===============
# Routers
# ===============
app.include_router(HealthRouter)
app.include_router(AuthRouter)
app.include_router(UserRouter)
app.include_router(ItemRouter)
app.include_router(SampleRouter)


# ===============
# Handlers
# ===============
@app.exception_handler(BaseError)
async def http_exception_handler(request, exception):
    logger.error(exception.message, exc_info=True)
    return JSONResponse(
        status_code=exception.status_code,
        content={
            "status_code": exception.status_code,
            "message": exception.message,
            "data": None,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exception):
    data = {}
    for error in exception.errors():
        loc, msg = error["loc"], error["msg"]
        filtered_loc = loc[1:] if loc[0] in ("body", "query", "path") else loc
        field_string = ".".join(filtered_loc)
        if field_string not in data:
            data[field_string] = []
        data[field_string].append(msg)

    return JSONResponse(
        status_code=400,
        content={
            "status_code": 400,
            "message": "Validation Error",
            "data": data,
        },
    )


# ===============
# Base Routers
# ===============
if config.environment != Environment.PRD:
    """Enable docs only for Development environment"""

    @app.get("/docs", include_in_schema=False)
    async def swagger_ui_html():
        return get_swagger_ui_html(
            openapi_url="/openapi.json",
            title=title,
            swagger_ui_parameters=app.swagger_ui_parameters,
        )

    @app.get("/", include_in_schema=False)
    async def home():
        return RedirectResponse("/docs")


# ===============
# WSGI
# ===============
def server():
    uvicorn.run(
        app="src:app",
        host="0.0.0.0",
        port=config.port,
        log_level=config.logging.level.lower(),
        reload=True if config.environment == Environment.LOCAL else False,
    )
