import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.carrera import CarreraRepository
from app.repositories.cohorte import CohorteRepository
from app.schemas.cohorte import CohorteCreate, CohorteResponse, CohorteUpdate


class CohorteService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self._repo = CohorteRepository(session, tenant_id)
        self._carrera_repo = CarreraRepository(session, tenant_id)

    async def list_cohortes(self):
        cohortes = await self._repo.get_multi()
        return {
            'items': [CohorteResponse.model_validate(c) for c in cohortes],
            'total': len(cohortes),
        }

    async def get_cohorte(self, cohorte_id: uuid.UUID):
        cohorte = await self._repo.get(cohorte_id)
        if not cohorte:
            raise HTTPException(status_code=404, detail='Cohorte no encontrada')
        return CohorteResponse.model_validate(cohorte)

    async def create_cohorte(self, data: CohorteCreate):
        carrera = await self._carrera_repo.get(data.carrera_id)
        if not carrera:
            raise HTTPException(status_code=404, detail='Carrera no encontrada')
        if carrera.estado != 'Activa':
            raise HTTPException(status_code=422, detail='La carrera no está activa')
        existing = await self._repo.get_by_nombre_and_carrera(data.nombre, data.carrera_id)
        if existing:
            raise HTTPException(
                status_code=409, detail='Ya existe una cohorte con ese nombre en la misma carrera',
            )
        cohorte = await self._repo.create(**data.model_dump())
        return CohorteResponse.model_validate(cohorte)

    async def update_cohorte(self, cohorte_id: uuid.UUID, data: CohorteUpdate):
        cohorte = await self._repo.get(cohorte_id)
        if not cohorte:
            raise HTTPException(status_code=404, detail='Cohorte no encontrada')
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        if not update_data:
            return CohorteResponse.model_validate(cohorte)
        updated = await self._repo.update(cohorte, **update_data)
        return CohorteResponse.model_validate(updated)

    async def delete_cohorte(self, cohorte_id: uuid.UUID):
        cohorte = await self._repo.get(cohorte_id)
        if not cohorte:
            raise HTTPException(status_code=404, detail='Cohorte no encontrada')
        await self._repo.soft_delete(cohorte)
