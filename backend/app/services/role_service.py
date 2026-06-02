import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.role import RoleRepository
from app.schemas.role import RoleCreate, RoleResponse, RoleUpdate


class RoleService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self._repo = RoleRepository(session, tenant_id)

    async def list_roles(self):
        roles = await self._repo.get_multi()
        return {
            'items': [RoleResponse.model_validate(r) for r in roles],
            'total': len(roles),
        }

    async def get_role(self, role_id: uuid.UUID):
        role = await self._repo.get(role_id)
        if not role:
            raise HTTPException(status_code=404, detail='Rol no encontrado')
        return RoleResponse.model_validate(role)

    async def create_role(self, data: RoleCreate):
        existing = await self._repo.get_by_codigo(data.codigo)
        if existing:
            raise HTTPException(status_code=409, detail='Ya existe un rol con ese código')
        role = await self._repo.create(**data.model_dump())
        return RoleResponse.model_validate(role)

    async def update_role(self, role_id: uuid.UUID, data: RoleUpdate):
        role = await self._repo.get(role_id)
        if not role:
            raise HTTPException(status_code=404, detail='Rol no encontrado')
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        if not update_data:
            return RoleResponse.model_validate(role)
        if 'codigo' in update_data:
            existing = await self._repo.get_by_codigo(update_data['codigo'])
            if existing and existing.id != role_id:
                raise HTTPException(status_code=409, detail='Ya existe un rol con ese código')
        updated = await self._repo.update(role, **update_data)
        return RoleResponse.model_validate(updated)

    async def delete_role(self, role_id: uuid.UUID):
        role = await self._repo.get(role_id)
        if not role:
            raise HTTPException(status_code=404, detail='Rol no encontrado')
        await self._repo.soft_delete(role)
