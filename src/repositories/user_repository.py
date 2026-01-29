from uuid import UUID

from fastapi_pagination.ext.sqlmodel import paginate
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlmodel import delete, insert, select, update

from src.dependencies import Database, Logger, tracer
from src.exceptions import BaseError
from src.exceptions.user_exception import UserAlreadyExistsError, UserNotFoundError
from src.models.user_model import User, UserCreate, UserUpdate
from src.schemas import Page


class UserRepository:
    db: Database
    logger: Logger

    def __init__(self, db: Database, logger: Logger) -> None:
        self.db = db
        self.logger = logger

    @tracer.observe()
    async def create(self, user: UserCreate, password_hash: str) -> User:
        try:
            data = User(
                username=user.username,
                email=user.email,
                is_admin=user.is_admin,
                password_hash=password_hash,
            )
            result = (
                await self.db.scalars(
                    insert(User).values(data.model_dump()).returning(User),
                )
            ).one()
            await self.db.commit()
            self.logger.debug(
                {
                    "message": "User created in DB",
                    "user_id": str(result.id),
                    "username": result.username,
                }
            )
            return result
        except IntegrityError as error:
            self.logger.warning(
                {
                    "message": "User creation failed: already exists",
                    "username": user.username,
                    "error": str(error),
                }
            )
            raise UserAlreadyExistsError() from error
        except Exception as error:
            self.logger.error(
                {
                    "message": "Database error during user creation",
                    "error": str(error),
                },
                exc_info=True,
            )
            raise BaseError("Database Internal Error") from error

    @tracer.observe()
    async def read_all(self) -> Page[User]:
        try:
            return await paginate(self.db, select(User))
        except Exception as error:
            self.logger.error(
                {
                    "message": "Database error during read_all users",
                    "error": str(error),
                },
                exc_info=True,
            )
            raise BaseError("Database Internal Error") from error

    @tracer.observe()
    async def read(self, id: UUID) -> User:
        try:
            result = (
                await self.db.exec(select(User).where(User.id == id))
            ).one()
            return result
        except NoResultFound as error:
            self.logger.warning(
                {
                    "message": "User not found",
                    "user_id": str(id),
                }
            )
            raise UserNotFoundError() from error
        except Exception as error:
            self.logger.error(
                {
                    "message": "Database error during user read",
                    "error": str(error),
                },
                exc_info=True,
            )
            raise BaseError("Database Internal Error") from error

    @tracer.observe()
    async def read_by_username(self, username: str) -> User:
        try:
            result = (
                await self.db.exec(
                    select(User).where(User.username == username)
                )
            ).one()
            return result
        except NoResultFound as error:
            self.logger.warning(
                {
                    "message": "User not found by username",
                    "username": username,
                }
            )
            raise UserNotFoundError() from error
        except Exception as error:
            self.logger.error(
                {
                    "message": "Database error during user read by username",
                    "error": str(error),
                },
                exc_info=True,
            )
            raise BaseError("Database Internal Error") from error

    @tracer.observe()
    async def update(self, id: UUID, user: UserUpdate) -> User:
        try:
            result = (
                await self.db.scalars(
                    update(User)
                    .where(User.id == id)
                    .values(user.model_dump(mode="json", exclude_none=True))
                    .returning(User),
                )
            ).one()
            await self.db.commit()
            self.logger.debug(
                {
                    "message": "User updated in DB",
                    "user_id": str(result.id),
                }
            )
            return result
        except NoResultFound as error:
            raise UserNotFoundError() from error
        except Exception as error:
            self.logger.error(
                {
                    "message": "Database error during user update",
                    "error": str(error),
                },
                exc_info=True,
            )
            raise BaseError("Database Internal Error") from error

    @tracer.observe()
    async def delete(self, id: UUID) -> None:
        try:
            await self.db.exec(delete(User).where(User.id == id))
            await self.db.commit()
            self.logger.debug(
                {
                    "message": "User deleted from DB",
                    "user_id": str(id),
                }
            )
        except Exception as error:
            self.logger.error(
                {
                    "message": "Database error during user delete",
                    "error": str(error),
                },
                exc_info=True,
            )
            raise BaseError("Database Internal Error") from error
