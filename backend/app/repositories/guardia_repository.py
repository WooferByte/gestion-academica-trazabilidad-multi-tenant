import uuid
from collections.abc import Sequence

from sqlalchemy import select

from app.models.guardia import Guardia
from app.repositories.base import BaseRepository


class GuardiaRepository(BaseRepository[Guardia]):
    __model__ = Guardia

    async def list_filtered(
        self,
        materia_id: uuid.UUID | None = None,
        carrera_id: uuid.UUID | None = None,
        cohorte_id: uuid.UUID | None = None,
        estado: str | None = None,
        asignacion_ids: Sequence[uuid.UUID] | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[Sequence[Guardia], int]:
        stmt = self._stmt()

        if materia_id is not None:
            stmt = stmt.where(Guardia.materia_id == materia_id)
        if carrera_id is not None:
            stmt = stmt.where(Guardia.carrera_id == carrera_id)
        if cohorte_id is not None:
            stmt = stmt.where(Guardia.cohorte_id == cohorte_id)
        if estado is not None:
            stmt = stmt.where(Guardia.estado == estado)
        if asignacion_ids is not None:
            stmt = stmt.where(Guardia.asignacion_id.in_(asignacion_ids))

        count_stmt = stmt
        count_result = await self._session.execute(count_stmt)
        total = len(count_result.scalars().all())

        stmt = stmt.order_by(Guardia.creada_at.desc()).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        items = list(result.scalars().all())

        return items, total

    async def list_all_for_export(
        self,
        materia_id: uuid.UUID | None = None,
        carrera_id: uuid.UUID | None = None,
        cohorte_id: uuid.UUID | None = None,
        estado: str | None = None,
        asignacion_ids: Sequence[uuid.UUID] | None = None,
    ) -> Sequence[Guardia]:
        stmt = self._stmt()

        if materia_id is not None:
            stmt = stmt.where(Guardia.materia_id == materia_id)
        if carrera_id is not None:
            stmt = stmt.where(Guardia.carrera_id == carrera_id)
        if cohorte_id is not None:
            stmt = stmt.where(Guardia.cohorte_id == cohorte_id)
        if estado is not None:
            stmt = stmt.where(Guardia.estado == estado)
        if asignacion_ids is not None:
            stmt = stmt.where(Guardia.asignacion_id.in_(asignacion_ids))

        stmt = stmt.order_by(Guardia.creada_at.desc())
        result = await self._session.execute(stmt)
        return result.scalars().all()
