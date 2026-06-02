import uuid

from sqlalchemy import select

from app.models.permission import Permission
from app.repositories.base import BaseRepository


class PermissionRepository(BaseRepository[Permission]):
    __model__ = Permission

    async def get_by_codigo(self, codigo: str) -> Permission | None:
        stmt = self._stmt().where(Permission.codigo == codigo)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_codigo_including_deleted(self, codigo: str) -> Permission | None:
        stmt = select(Permission).where(
            Permission.tenant_id == self._tenant_id,
            Permission.codigo == codigo,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_multi_by_codigos(self, codigos: list[str]) -> list[Permission]:
        stmt = self._stmt().where(Permission.codigo.in_(codigos))
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
