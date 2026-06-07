import uuid
from collections.abc import Sequence

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.factura import Factura
from app.repositories.factura_repository import FacturaRepository

ESTADOS_VALIDOS = frozenset({'Pendiente', 'Abonada'})


class FacturaService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self._session = session
        self._tenant_id = tenant_id
        self._factura_repo = FacturaRepository(session, tenant_id)

    async def listar(
        self,
        usuario_id: uuid.UUID | None = None,
        periodo: str | None = None,
        estado: str | None = None,
    ) -> Sequence[Factura]:
        return await self._factura_repo.list(
            usuario_id=usuario_id, periodo=periodo, estado=estado,
        )

    async def crear(
        self,
        usuario_id: uuid.UUID,
        periodo: str,
        detalle: str,
        referencia_archivo: str | None = None,
        tamano_kb: float | None = None,
    ) -> Factura:
        return await self._factura_repo.create(
            usuario_id=usuario_id,
            periodo=periodo,
            detalle=detalle,
            referencia_archivo=referencia_archivo,
            tamano_kb=tamano_kb,
            estado='Pendiente',
        )

    async def obtener(self, factura_id: uuid.UUID) -> Factura | None:
        return await self._factura_repo.get(factura_id)

    async def cambiar_estado(self, factura_id: uuid.UUID, nuevo_estado: str) -> Factura:
        if nuevo_estado not in ESTADOS_VALIDOS:
            raise HTTPException(
                status_code=422,
                detail=f'Estado inválido: {nuevo_estado}. Valores permitidos: Pendiente, Abonada',
            )

        factura = await self._factura_repo.get(factura_id)
        if factura is None:
            raise HTTPException(status_code=404, detail='Factura no encontrada')

        if factura.estado == 'Abonada':
            raise HTTPException(status_code=409, detail='Factura ya está abonada')

        updated = await self._factura_repo.update_estado(factura_id, nuevo_estado)
        if updated is None:
            raise HTTPException(status_code=404, detail='Factura no encontrada')
        return updated
