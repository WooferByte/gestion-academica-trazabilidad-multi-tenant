import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.fecha_academica_repository import FechaAcademicaRepository
from app.schemas.fecha_academica import (
    FechaAcademicaCreate,
    FechaAcademicaResponse,
    FechaAcademicaUpdate,
)


class FechaAcademicaService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self._repo = FechaAcademicaRepository(session, tenant_id)

    async def list_fechas(
        self,
        materia_id: uuid.UUID | None = None,
        cohorte_id: uuid.UUID | None = None,
        tipo: str | None = None,
        periodo: str | None = None,
    ):
        fechas = await self._repo.get_filtered(
            materia_id=materia_id,
            cohorte_id=cohorte_id,
            tipo=tipo,
            periodo=periodo,
        )
        return {
            'items': [FechaAcademicaResponse.model_validate(f) for f in fechas],
            'total': len(fechas),
        }

    async def get_fecha(self, fecha_id: uuid.UUID):
        fecha = await self._repo.get(fecha_id)
        if not fecha:
            raise HTTPException(status_code=404, detail='Fecha académica no encontrada')
        return FechaAcademicaResponse.model_validate(fecha)

    async def create_fecha(self, data: FechaAcademicaCreate):
        fecha = await self._repo.create(**data.model_dump())
        return FechaAcademicaResponse.model_validate(fecha)

    async def update_fecha(self, fecha_id: uuid.UUID, data: FechaAcademicaUpdate):
        fecha = await self._repo.get(fecha_id)
        if not fecha:
            raise HTTPException(status_code=404, detail='Fecha académica no encontrada')
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        if not update_data:
            return FechaAcademicaResponse.model_validate(fecha)
        updated = await self._repo.update(fecha, **update_data)
        return FechaAcademicaResponse.model_validate(updated)

    async def delete_fecha(self, fecha_id: uuid.UUID):
        fecha = await self._repo.get(fecha_id)
        if not fecha:
            raise HTTPException(status_code=404, detail='Fecha académica no encontrada')
        await self._repo.soft_delete(fecha)
