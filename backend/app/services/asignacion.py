"""
# Transición user_roles ↔ asignacion

Durante la coexistencia (C-07 a C-08), `user_roles` y `asignaciones` conviven:
- `user_roles` (C-04) mantiene el vínculo legacy usuario ↔ rol para claims JWT rápidos.
- `asignaciones` (C-07) es el nuevo modelo que agrega contexto académico (materia, carrera,
  cohorte, comisiones, responsable) con vigencia temporal.

**C-08 incluirá migración donde `asignacion` prevalece como fuente única** y `user_roles`
se depreca. Hasta entonces, ambos sistemas coexisten y deben mantenerse sincronizados
cuando se creen/modifiquen asignaciones que impliquen un cambio de rol.
"""
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.asignacion import AsignacionRepository
from app.schemas.asignacion import (
    AsignacionCreate,
    AsignacionListResponse,
    AsignacionResponse,
    AsignacionUpdate,
)


class AsignacionService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self._repo = AsignacionRepository(session, tenant_id)

    async def list_asignaciones(
        self,
        *,
        usuario_id: uuid.UUID | None = None,
        rol: str | None = None,
        materia_id: uuid.UUID | None = None,
        carrera_id: uuid.UUID | None = None,
        cohorte_id: uuid.UUID | None = None,
        responsable_id: uuid.UUID | None = None,
        solo_vigentes: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> dict:
        asignaciones = await self._repo.list_with_filters(
            usuario_id=usuario_id,
            rol=rol,
            materia_id=materia_id,
            carrera_id=carrera_id,
            cohorte_id=cohorte_id,
            responsable_id=responsable_id,
            solo_vigentes=solo_vigentes,
            skip=skip,
            limit=limit,
        )
        return {
            'items': [self._to_response(a) for a in asignaciones],
            'total': len(asignaciones),
        }

    async def get_asignacion(self, asignacion_id: uuid.UUID) -> dict:
        asignacion = await self._repo.get(asignacion_id)
        if not asignacion:
            raise HTTPException(status_code=404, detail='Asignacion no encontrada')
        return self._to_response(asignacion)

    async def create_asignacion(self, data: AsignacionCreate) -> dict:
        asignacion = await self._repo.create(**data.model_dump())
        return self._to_response(asignacion)

    async def update_asignacion(
        self, asignacion_id: uuid.UUID, data: AsignacionUpdate,
    ) -> dict:
        asignacion = await self._repo.get(asignacion_id)
        if not asignacion:
            raise HTTPException(status_code=404, detail='Asignacion no encontrada')
        update_data = {k: v for k, v in data.model_dump().items() if v is not None}
        if not update_data:
            return self._to_response(asignacion)
        updated = await self._repo.update(asignacion, **update_data)
        return self._to_response(updated)

    async def delete_asignacion(self, asignacion_id: uuid.UUID) -> None:
        asignacion = await self._repo.get(asignacion_id)
        if not asignacion:
            raise HTTPException(status_code=404, detail='Asignacion no encontrada')
        await self._repo.soft_delete(asignacion)

    def _to_response(self, asignacion) -> dict:
        return AsignacionResponse(
            id=asignacion.id,
            tenant_id=asignacion.tenant_id,
            usuario_id=asignacion.usuario_id,
            rol=asignacion.rol,
            materia_id=asignacion.materia_id,
            carrera_id=asignacion.carrera_id,
            cohorte_id=asignacion.cohorte_id,
            comisiones=asignacion.comisiones,
            responsable_id=asignacion.responsable_id,
            desde=asignacion.desde,
            hasta=asignacion.hasta,
            created_at=asignacion.created_at,
            updated_at=asignacion.updated_at,
            deleted_at=asignacion.deleted_at,
        )