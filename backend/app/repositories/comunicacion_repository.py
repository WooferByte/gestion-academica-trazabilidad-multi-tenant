import uuid
from collections.abc import Sequence
from datetime import datetime, timezone

from sqlalchemy import select, update

from app.models.comunicacion import Comunicacion, EstadoComunicacion
from app.repositories.base import BaseRepository


class ComunicacionRepository(BaseRepository[Comunicacion]):
    __model__ = Comunicacion

    async def get_pendientes(self, batch_size: int = 50) -> Sequence[Comunicacion]:
        stmt = (
            select(Comunicacion)
            .where(Comunicacion.tenant_id == self._tenant_id)
            .where(Comunicacion.deleted_at.is_(None))
            .where(Comunicacion.estado == EstadoComunicacion.PENDIENTE)
            .where(
                (Comunicacion.programada_para.is_(None))
                | (Comunicacion.programada_para <= datetime.now(timezone.utc))
            )
            .limit(batch_size)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_by_lote(self, lote_id: uuid.UUID) -> Sequence[Comunicacion]:
        stmt = self._stmt().where(Comunicacion.lote_id == lote_id)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_by_materia(self, materia_id: uuid.UUID) -> Sequence[Comunicacion]:
        stmt = self._stmt().where(Comunicacion.materia_id == materia_id)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def update_estado(self, comunicacion_id: uuid.UUID, estado: EstadoComunicacion, **extra) -> Comunicacion | None:
        values = {'estado': estado, **extra}
        stmt = (
            update(Comunicacion)
            .where(Comunicacion.id == comunicacion_id)
            .where(Comunicacion.tenant_id == self._tenant_id)
            .values(**values)
            .returning(Comunicacion)
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.scalar_one_or_none()

    async def count_by_lote(self, lote_id: uuid.UUID) -> int:
        stmt = (
            select(Comunicacion)
            .where(Comunicacion.lote_id == lote_id)
            .where(Comunicacion.tenant_id == self._tenant_id)
        )
        result = await self._session.execute(stmt)
        return len(result.scalars().all())

    async def update_estado_by_lote(self, lote_id: uuid.UUID, estado: EstadoComunicacion, **extra) -> int:
        values = {'estado': estado, **extra}
        stmt = (
            update(Comunicacion)
            .where(Comunicacion.lote_id == lote_id)
            .where(Comunicacion.tenant_id == self._tenant_id)
            .values(**values)
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.rowcount
