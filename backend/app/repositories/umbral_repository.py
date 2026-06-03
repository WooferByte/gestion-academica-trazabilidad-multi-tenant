import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.umbral_materia import UmbralMateria
from app.repositories.base import BaseRepository


class UmbralMateriaRepository(BaseRepository[UmbralMateria]):
    __model__ = UmbralMateria

    async def get_by_asignacion(
        self, asignacion_id: uuid.UUID,
    ) -> UmbralMateria | None:
        stmt = self._stmt().where(UmbralMateria.asignacion_id == asignacion_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_materia_cohorte(
        self, materia_id: uuid.UUID, cohorte_id: uuid.UUID,
    ) -> UmbralMateria | None:
        stmt = (
            self._stmt()
            .where(UmbralMateria.materia_id == materia_id)
            .where(UmbralMateria.cohorte_id == cohorte_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert(
        self,
        asignacion_id: uuid.UUID,
        materia_id: uuid.UUID,
        cohorte_id: uuid.UUID,
        umbral_pct: int = 60,
        valores_aprobatorios: list[str] | None = None,
    ) -> UmbralMateria:
        existing = await self.get_by_asignacion(asignacion_id)
        if existing:
            existing.umbral_pct = umbral_pct
            existing.valores_aprobatorios = valores_aprobatorios
            await self._session.flush()
            await self._session.refresh(existing)
            return existing

        return await self.create(
            asignacion_id=asignacion_id,
            materia_id=materia_id,
            cohorte_id=cohorte_id,
            umbral_pct=umbral_pct,
            valores_aprobatorios=valores_aprobatorios,
        )
