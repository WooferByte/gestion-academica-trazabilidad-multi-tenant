import uuid

from sqlalchemy import select

from app.models.role_permission import RolePermission
from app.repositories.base import BaseRepository


class RolePermissionRepository(BaseRepository[RolePermission]):
    __model__ = RolePermission

    async def get_by_role_and_permiso(
        self, role_id: uuid.UUID, permiso_id: uuid.UUID,
    ) -> RolePermission | None:
        stmt = (
            self._stmt()
            .where(RolePermission.role_id == role_id)
            .where(RolePermission.permiso_id == permiso_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_role_and_permiso_including_deleted(
        self, role_id: uuid.UUID, permiso_id: uuid.UUID,
    ) -> RolePermission | None:
        stmt = select(RolePermission).where(
            RolePermission.tenant_id == self._tenant_id,
            RolePermission.role_id == role_id,
            RolePermission.permiso_id == permiso_id,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_role(self, role_id: uuid.UUID) -> list[RolePermission]:
        stmt = self._stmt().where(RolePermission.role_id == role_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def delete_by_role_and_permiso(
        self, role_id: uuid.UUID, permiso_id: uuid.UUID,
    ) -> RolePermission | None:
        rp = await self.get_by_role_and_permiso(role_id, permiso_id)
        if rp:
            return await self.soft_delete(rp)
        return None
