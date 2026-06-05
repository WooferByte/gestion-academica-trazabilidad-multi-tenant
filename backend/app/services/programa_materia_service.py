import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.programa_materia_repository import ProgramaMateriaRepository
from app.schemas.programa_materia import (
    ProgramaMateriaCreate,
    ProgramaMateriaResponse,
    ProgramaMateriaUpdate,
)
class ProgramaMateriaService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self._repo = ProgramaMateriaRepository(session, tenant_id)

    async def list_programas(self):
        programas = await self._repo.get_multi()
        return {
            'items': [ProgramaMateriaResponse.model_validate(p) for p in programas],
            'total': len(programas),
        }

    async def get_programa(self, programa_id: uuid.UUID):
        programa = await self._repo.get(programa_id)
        if not programa:
            raise HTTPException(status_code=404, detail='Programa no encontrado')
        return ProgramaMateriaResponse.model_validate(programa)

    async def create_programa(self, data: ProgramaMateriaCreate):
        existing = await self._repo.get_by_materia_carrera_cohorte(
            data.materia_id, data.carrera_id, data.cohorte_id,
        )
        if existing:
            raise HTTPException(status_code=409, detail='Ya existe un programa para esa materia/carrera/cohorte')
        programa = await self._repo.create(**data.model_dump())
        return ProgramaMateriaResponse.model_validate(programa)

    async def update_programa(self, programa_id: uuid.UUID, data: ProgramaMateriaUpdate):
        programa = await self._repo.get(programa_id)
        if not programa:
            raise HTTPException(status_code=404, detail='Programa no encontrado')
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        if not update_data:
            return ProgramaMateriaResponse.model_validate(programa)
        updated = await self._repo.update(programa, **update_data)
        return ProgramaMateriaResponse.model_validate(updated)

    async def delete_programa(self, programa_id: uuid.UUID):
        programa = await self._repo.get(programa_id)
        if not programa:
            raise HTTPException(status_code=404, detail='Programa no encontrado')
        await self._repo.soft_delete(programa)
