import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.materia import MateriaRepository
from app.schemas.materia import MateriaCreate, MateriaResponse, MateriaUpdate


class MateriaService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self._repo = MateriaRepository(session, tenant_id)

    async def list_materias(self):
        materias = await self._repo.get_multi()
        return {
            'items': [MateriaResponse.model_validate(m) for m in materias],
            'total': len(materias),
        }

    async def get_materia(self, materia_id: uuid.UUID):
        materia = await self._repo.get(materia_id)
        if not materia:
            raise HTTPException(status_code=404, detail='Materia no encontrada')
        return MateriaResponse.model_validate(materia)

    async def create_materia(self, data: MateriaCreate):
        existing = await self._repo.get_by_codigo(data.codigo)
        if existing:
            raise HTTPException(status_code=409, detail='Ya existe una materia con ese código')
        materia = await self._repo.create(**data.model_dump())
        return MateriaResponse.model_validate(materia)

    async def update_materia(self, materia_id: uuid.UUID, data: MateriaUpdate):
        materia = await self._repo.get(materia_id)
        if not materia:
            raise HTTPException(status_code=404, detail='Materia no encontrada')
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        if not update_data:
            return MateriaResponse.model_validate(materia)
        if 'codigo' in update_data:
            existing = await self._repo.get_by_codigo(update_data['codigo'])
            if existing and existing.id != materia_id:
                raise HTTPException(status_code=409, detail='Ya existe una materia con ese código')
        updated = await self._repo.update(materia, **update_data)
        return MateriaResponse.model_validate(updated)

    async def delete_materia(self, materia_id: uuid.UUID):
        materia = await self._repo.get(materia_id)
        if not materia:
            raise HTTPException(status_code=404, detail='Materia no encontrada')
        await self._repo.soft_delete(materia)
