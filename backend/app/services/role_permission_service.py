import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.permission import PermissionRepository
from app.repositories.role import RoleRepository
from app.repositories.role_permission import RolePermissionRepository
from app.schemas.role_permission import RolePermissionAssign


class RolePermissionService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self._session = session
        self._tenant_id = tenant_id
        self._rp_repo = RolePermissionRepository(session, tenant_id)
        self._role_repo = RoleRepository(session, tenant_id)
        self._perm_repo = PermissionRepository(session, tenant_id)

    async def list_by_role(self, role_id: uuid.UUID):
        role = await self._role_repo.get(role_id)
        if not role:
            raise HTTPException(status_code=404, detail='Rol no encontrado')
        return await self._rp_repo.list_by_role(role_id)

    async def assign(self, role_id: uuid.UUID, data: RolePermissionAssign):
        role = await self._role_repo.get(role_id)
        if not role:
            raise HTTPException(status_code=404, detail='Rol no encontrado')
        permiso = await self._perm_repo.get(data.permiso_id)
        if not permiso:
            raise HTTPException(status_code=404, detail='Permiso no encontrado')
        existing = await self._rp_repo.get_by_role_and_permiso_including_deleted(
            role_id, data.permiso_id,
        )
        if existing:
            if existing.deleted_at is not None:
                from datetime import datetime, timezone
                existing.deleted_at = None
                existing.propio = data.propio
                await self._session.flush()
                return existing
            raise HTTPException(status_code=409, detail='El permiso ya está asignado a este rol')
        return await self._rp_repo.create(
            role_id=role_id, permiso_id=data.permiso_id, propio=data.propio,
        )

    async def unassign(self, role_id: uuid.UUID, permiso_id: uuid.UUID):
        role = await self._role_repo.get(role_id)
        if not role:
            raise HTTPException(status_code=404, detail='Rol no encontrado')
        permiso = await self._perm_repo.get(permiso_id)
        if not permiso:
            raise HTTPException(status_code=404, detail='Permiso no encontrado')
        deleted = await self._rp_repo.delete_by_role_and_permiso(role_id, permiso_id)
        if not deleted:
            raise HTTPException(status_code=404, detail='Asignación no encontrada')
