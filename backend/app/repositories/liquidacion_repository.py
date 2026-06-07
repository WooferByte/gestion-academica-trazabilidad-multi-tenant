import uuid
from collections.abc import Sequence

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.models.liquidacion import Liquidacion
from app.repositories.base import BaseRepository


class LiquidacionRepository(BaseRepository[Liquidacion]):
    __model__ = Liquidacion

    def _stmt_abiertas(self):
        return self._stmt().where(Liquidacion.estado == 'Abierta')

    async def get_by_cohorte_periodo(
        self,
        cohorte_id: uuid.UUID,
        periodo: str,
    ) -> Sequence[Liquidacion]:
        stmt = (
            self._stmt()
            .where(Liquidacion.cohorte_id == cohorte_id)
            .where(Liquidacion.periodo == periodo)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def list(
        self,
        cohorte_id: uuid.UUID | None = None,
        periodo: str | None = None,
        usuario_id: uuid.UUID | None = None,
        estado: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Liquidacion]:
        stmt = self._stmt()
        if cohorte_id:
            stmt = stmt.where(Liquidacion.cohorte_id == cohorte_id)
        if periodo:
            stmt = stmt.where(Liquidacion.periodo == periodo)
        if usuario_id:
            stmt = stmt.where(Liquidacion.usuario_id == usuario_id)
        if estado:
            stmt = stmt.where(Liquidacion.estado == estado)
        stmt = stmt.offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def cerrar_lote(
        self,
        cohorte_id: uuid.UUID,
        periodo: str,
    ) -> int:
        stmt = (
            update(Liquidacion)
            .where(Liquidacion.tenant_id == self._tenant_id)
            .where(Liquidacion.cohorte_id == cohorte_id)
            .where(Liquidacion.periodo == periodo)
            .where(Liquidacion.estado == 'Abierta')
            .values(estado='Cerrada')
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.rowcount

    async def update_estado(self, liquidacion_id: uuid.UUID, nuevo_estado: str) -> Liquidacion | None:
        liqui = await self.get(liquidacion_id)
        if liqui is None:
            return None
        if liqui.estado == 'Cerrada' and nuevo_estado != 'Cerrada':
            raise AppException(status_code=409, detail='Liquidación cerrada no puede modificarse')
        liqui.estado = nuevo_estado
        await self._session.flush()
        await self._session.refresh(liqui)
        return liqui

    async def reject_if_closed(self, liquidacion_id: uuid.UUID) -> None:
        liqui = await self.get(liquidacion_id)
        if liqui and liqui.estado == 'Cerrada':
            raise AppException(status_code=409, detail='Liquidación cerrada no puede modificarse')
