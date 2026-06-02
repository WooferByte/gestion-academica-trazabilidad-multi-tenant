import uuid

from sqlalchemy import select

from app.models.role import Role
from app.repositories.base import BaseRepository


class RoleRepository(BaseRepository[Role]):
    __model__ = Role

    async def get_by_codigo(self, codigo: str) -> Role | None:
        stmt = self._stmt().where(Role.codigo == codigo)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_codigo_including_deleted(self, codigo: str) -> Role | None:
        stmt = select(Role).where(
            Role.tenant_id == self._tenant_id,
            Role.codigo == codigo,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
