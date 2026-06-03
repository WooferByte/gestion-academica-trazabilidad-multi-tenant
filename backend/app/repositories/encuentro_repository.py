import uuid
from collections.abc import Sequence
from datetime import date

from sqlalchemy import select

from app.models.instancia_encuentro import InstanciaEncuentro
from app.models.slot_encuentro import SlotEncuentro
from app.repositories.base import BaseRepository


class SlotEncuentroRepository(BaseRepository[SlotEncuentro]):
    __model__ = SlotEncuentro

    async def list_by_materia(self, materia_id: uuid.UUID) -> Sequence[SlotEncuentro]:
        stmt = self._stmt().where(SlotEncuentro.materia_id == materia_id)
        result = await self._session.execute(stmt)
        return result.scalars().all()


class InstanciaEncuentroRepository(BaseRepository[InstanciaEncuentro]):
    __model__ = InstanciaEncuentro

    async def list_filtered(
        self,
        materia_id: uuid.UUID | None = None,
        desde: date | None = None,
        hasta: date | None = None,
        estado: str | None = None,
        slot_id: uuid.UUID | None = None,
        materia_ids: Sequence[uuid.UUID] | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[Sequence[InstanciaEncuentro], int]:
        stmt = self._stmt()

        if materia_id is not None:
            stmt = stmt.where(InstanciaEncuentro.materia_id == materia_id)
        if materia_ids is not None:
            stmt = stmt.where(InstanciaEncuentro.materia_id.in_(materia_ids))
        if desde is not None:
            stmt = stmt.where(InstanciaEncuentro.fecha >= desde)
        if hasta is not None:
            stmt = stmt.where(InstanciaEncuentro.fecha <= hasta)
        if estado is not None:
            stmt = stmt.where(InstanciaEncuentro.estado == estado)
        if slot_id is not None:
            stmt = stmt.where(InstanciaEncuentro.slot_id == slot_id)

        count_stmt = stmt
        count_result = await self._session.execute(count_stmt)
        total = len(count_result.scalars().all())

        stmt = stmt.order_by(InstanciaEncuentro.fecha.asc()).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        items = list(result.scalars().all())

        return items, total
