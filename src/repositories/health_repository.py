from sqlalchemy import select

from src.dependencies import Database
from src.exceptions import DatabaseHealthError


class HealthRepository:
    db: Database

    def __init__(
        self,
        db: Database,
    ) -> None:
        self.db = db

    async def check(
        self,
    ) -> bool:
        try:
            await self.db.exec(select(1))
        except Exception:
            raise DatabaseHealthError()

        return True
