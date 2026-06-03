import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.carrera import CarreraRepository
from app.schemas.carrera import CarreraCreate, CarreraResponse, CarreraUpdate


class CarreraService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self._repo = CarreraRepository(session, tenant_id)

    async def list_carreras(self):
        carreras = await self._repo.get_multi()
        return {
            'items': [CarreraResponse.model_validate(c) for c in carreras],
            'total': len(carreras),
        }

    async def get_carrera(self, carrera_id: uuid.UUID):
        carrera = await self._repo.get(carrera_id)
        if not carrera:
            raise HTTPException(status_code=404, detail='Carrera no encontrada')
        return CarreraResponse.model_validate(carrera)

    async def create_carrera(self, data: CarreraCreate):
        existing = await self._repo.get_by_codigo(data.codigo)
        if existing:
            raise HTTPException(status_code=409, detail='Ya existe una carrera con ese código')
        carrera = await self._repo.create(**data.model_dump())
        return CarreraResponse.model_validate(carrera)

    async def update_carrera(self, carrera_id: uuid.UUID, data: CarreraUpdate):
        carrera = await self._repo.get(carrera_id)
        if not carrera:
            raise HTTPException(status_code=404, detail='Carrera no encontrada')
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        if not update_data:
            return CarreraResponse.model_validate(carrera)
        if 'codigo' in update_data:
            existing = await self._repo.get_by_codigo(update_data['codigo'])
            if existing and existing.id != carrera_id:
                raise HTTPException(status_code=409, detail='Ya existe una carrera con ese código')
        if update_data.get('estado') == 'Inactiva':
            cohortes_abiertas = await self._repo.get_cohortes_abiertas(carrera_id)
            if cohortes_abiertas:
                raise HTTPException(
                    status_code=422,
                    detail='No se puede inactivar una carrera con cohortes abiertas',
                )
        updated = await self._repo.update(carrera, **update_data)
        return CarreraResponse.model_validate(updated)

    async def delete_carrera(self, carrera_id: uuid.UUID):
        carrera = await self._repo.get(carrera_id)
        if not carrera:
            raise HTTPException(status_code=404, detail='Carrera no encontrada')
        await self._repo.soft_delete(carrera)
