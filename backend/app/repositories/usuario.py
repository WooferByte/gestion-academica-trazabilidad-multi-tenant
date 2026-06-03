import uuid
from collections.abc import Sequence

from sqlalchemy import select

from app.models.user import User
from app.repositories.base import BaseRepository


class UsuarioRepository(BaseRepository[User]):
    __model__ = User

    async def list_with_filters(
        self, *, estado: str | None = None, skip: int = 0, limit: int = 100,
    ) -> Sequence[User]:
        stmt = self._stmt()
        if estado is not None:
            stmt = stmt.where(User.estado == estado)
        stmt = stmt.offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_by_email_hash(self, email_hash: str) -> User | None:
        stmt = self._stmt().where(User.email_hash == email_hash)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_legajo(self, legajo: str) -> User | None:
        stmt = self._stmt().where(User.legajo == legajo)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()