from uuid import UUID

from fastapi_pagination.ext.sqlmodel import paginate
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlmodel import delete, insert, select, update

from src.dependencies import Database, Logger, tracer
from src.exceptions import (
    BaseError,
    SampleAlreadyExistsError,
    SampleNotFoundError,
)
from src.models import (
    Sample,
    SampleCreate,
    SampleUpdate,
)
from src.schemas import Page


class SampleRepository:
    db: Database
    logger: Logger

    def __init__(self, db: Database, logger: Logger) -> None:
        self.db = db
        self.logger = logger

    @tracer.observe()
    async def create(
        self,
        sample: SampleCreate,
    ) -> Sample:
        try:
            data = Sample.model_validate(sample)
            result = (
                await self.db.scalars(
                    insert(Sample).values(data.model_dump()).returning(Sample),
                )
            ).one()
            await self.db.commit()
            self.logger.debug(
                {
                    "message": "Sample created in DB",
                    "sample": result.model_dump(mode="json"),
                }
            )
            return result
        except IntegrityError as error:
            self.logger.warning(
                {
                    "message": "Sample creation failed: already exists",
                    "error": str(error),
                }
            )
            raise SampleAlreadyExistsError() from error
        except Exception as error:
            self.logger.error(
                {
                    "message": "Database error during creation",
                    "error": str(error),
                },
                exc_info=True,
            )
            raise BaseError("Database Internal Error") from error

    @tracer.observe()
    async def read_all(
        self,
    ) -> Page[Sample]:
        try:
            return await paginate(
                self.db,
                select(Sample),
            )
        except Exception as error:
            self.logger.error(
                {
                    "message": "Database error during read_all",
                    "error": str(error),
                },
                exc_info=True,
            )
            raise BaseError("Database Internal Error") from error

    @tracer.observe()
    async def read(
        self,
        id: UUID,
    ) -> Sample | None:
        try:
            result = (
                await self.db.exec(
                    select(Sample).where(Sample.id == id),
                )
            ).one()
            return result
        except NoResultFound as error:
            self.logger.warning(
                {
                    "message": "Sample not found",
                    "sample_id": str(id),
                }
            )
            raise SampleNotFoundError() from error
        except Exception as error:
            self.logger.error(
                {
                    "message": "Database error during read",
                    "error": str(error),
                },
                exc_info=True,
            )
            raise BaseError("Database Internal Error") from error

    @tracer.observe()
    async def update(
        self,
        id: UUID,
        sample: SampleUpdate,
    ) -> Sample:
        try:
            result = (
                await self.db.scalars(
                    update(Sample)
                    .where(Sample.id == id)
                    .values(sample.model_dump(mode="json", exclude_none=True))
                    .returning(Sample),
                )
            ).one()
            await self.db.commit()
            self.logger.debug(
                {
                    "message": "Sample updated in DB",
                    "sample": result.model_dump(mode="json"),
                }
            )
            return result
        except Exception as error:
            self.logger.error(
                {
                    "message": "Database error during update",
                    "error": str(error),
                },
                exc_info=True,
            )
            raise BaseError("Database Internal Error") from error

    @tracer.observe()
    async def delete(
        self,
        id: UUID,
    ) -> None:
        try:
            await self.db.exec(delete(Sample).where(Sample.id == id))
            await self.db.commit()
            self.logger.debug(
                {
                    "message": "Sample deleted from DB",
                    "sample_id": str(id),
                }
            )
        except Exception as error:
            self.logger.error(
                {
                    "message": "Database error during delete",
                    "error": str(error),
                },
                exc_info=True,
            )
            raise BaseError("Database Internal Error") from error
