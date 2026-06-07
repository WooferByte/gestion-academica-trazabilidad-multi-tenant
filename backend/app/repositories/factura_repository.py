import uuid
from collections.abc import Sequence
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.factura import Factura
from app.repositories.base import BaseRepository


class FacturaRepository(BaseRepository[Factura]):
    __model__ = Factura

    async def list(
        self,
        usuario_id: uuid.UUID | None = None,
        periodo: str | None = None,
        estado: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Factura]:
        stmt = self._stmt().order_by(Factura.cargada_at.desc())
        if usuario_id:
            stmt = stmt.where(Factura.usuario_id == usuario_id)
        if periodo:
            stmt = stmt.where(Factura.periodo == periodo)
        if estado:
            stmt = stmt.where(Factura.estado == estado)
        stmt = stmt.offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def update_estado(self, factura_id: uuid.UUID, nuevo_estado: str) -> Factura | None:
        factura = await self.get(factura_id)
        if factura is None:
            return None
        factura.estado = nuevo_estado
        if nuevo_estado == 'Abonada':
            factura.abonada_at = datetime.now(timezone.utc)
        await self._session.flush()
        await self._session.refresh(factura)
        return factura
