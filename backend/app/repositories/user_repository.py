import uuid

from sqlalchemy import select

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    __model__ = User

    async def get_by_email(self, email: str) -> User | None:
        stmt = self._stmt().where(self._model.email == email)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email_with_deleted(self, email: str) -> User | None:
        stmt = self._stmt_with_deleted().where(self._model.email == email)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
