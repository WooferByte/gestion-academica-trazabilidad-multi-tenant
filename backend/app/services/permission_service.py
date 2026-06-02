import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.permission import PermissionRepository
from app.schemas.permission import PermissionCreate, PermissionResponse, PermissionUpdate


class PermissionService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self._repo = PermissionRepository(session, tenant_id)

    async def list_permisos(self):
        permisos = await self._repo.get_multi()
        return {
            'items': [PermissionResponse.model_validate(p) for p in permisos],
            'total': len(permisos),
        }

    async def get_permiso(self, permiso_id: uuid.UUID):
        permiso = await self._repo.get(permiso_id)
        if not permiso:
            raise HTTPException(status_code=404, detail='Permiso no encontrado')
        return PermissionResponse.model_validate(permiso)

    async def create_permiso(self, data: PermissionCreate):
        existing = await self._repo.get_by_codigo(data.codigo)
        if existing:
            raise HTTPException(status_code=409, detail='Ya existe un permiso con ese código')
        permiso = await self._repo.create(**data.model_dump())
        return PermissionResponse.model_validate(permiso)

    async def update_permiso(self, permiso_id: uuid.UUID, data: PermissionUpdate):
        permiso = await self._repo.get(permiso_id)
        if not permiso:
            raise HTTPException(status_code=404, detail='Permiso no encontrado')
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        if not update_data:
            return PermissionResponse.model_validate(permiso)
        updated = await self._repo.update(permiso, **update_data)
        return PermissionResponse.model_validate(updated)

    async def delete_permiso(self, permiso_id: uuid.UUID):
        permiso = await self._repo.get(permiso_id)
        if not permiso:
            raise HTTPException(status_code=404, detail='Permiso no encontrado')
        await self._repo.soft_delete(permiso)
