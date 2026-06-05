import uuid
from collections.abc import Sequence

from sqlalchemy import select

from app.models.fecha_academica import FechaAcademica
from app.repositories.base import BaseRepository


class FechaAcademicaRepository(BaseRepository[FechaAcademica]):
    __model__ = FechaAcademica

    async def get_filtered(
        self,
        materia_id: uuid.UUID | None = None,
        cohorte_id: uuid.UUID | None = None,
        tipo: str | None = None,
        periodo: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[FechaAcademica]:
        stmt = self._stmt()
        if materia_id is not None:
            stmt = stmt.where(FechaAcademica.materia_id == materia_id)
        if cohorte_id is not None:
            stmt = stmt.where(FechaAcademica.cohorte_id == cohorte_id)
        if tipo is not None:
            stmt = stmt.where(FechaAcademica.tipo == tipo)
        if periodo is not None:
            stmt = stmt.where(FechaAcademica.periodo == periodo)
        stmt = stmt.offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all()
