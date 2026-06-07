import uuid
from collections.abc import Sequence
from datetime import date

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.salario_base import SalarioBase
from app.repositories.base import BaseRepository


class SalarioBaseRepository(BaseRepository[SalarioBase]):
    __model__ = SalarioBase

    async def get_vigente(self, rol: str, fecha: date) -> SalarioBase | None:
        stmt = (
            self._stmt()
            .where(SalarioBase.rol == rol)
            .where(SalarioBase.desde <= fecha)
            .where(
                (SalarioBase.hasta >= fecha) | (SalarioBase.hasta.is_(None)),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_vigente_sin_hasta(self, rol: str) -> SalarioBase | None:
        stmt = (
            self._stmt()
            .where(SalarioBase.rol == rol)
            .where(SalarioBase.hasta.is_(None))
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def cerrar_vigencia(self, salario_id: uuid.UUID, hasta: date) -> None:
        await self._session.execute(
            update(SalarioBase)
            .where(SalarioBase.id == salario_id)
            .where(SalarioBase.tenant_id == self._tenant_id)
            .values(hasta=hasta),
        )
        await self._session.flush()

    async def list_historicos(
        self,
        rol: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[SalarioBase]:
        stmt = self._stmt().order_by(SalarioBase.rol, SalarioBase.desde.desc())
        if rol:
            stmt = stmt.where(SalarioBase.rol == rol)
        stmt = stmt.offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all()
