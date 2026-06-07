import uuid
from collections.abc import Sequence
from datetime import date

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.salario_plus import SalarioPlus
from app.repositories.base import BaseRepository


class SalarioPlusRepository(BaseRepository[SalarioPlus]):
    __model__ = SalarioPlus

    async def get_vigente(self, grupo: str, rol: str, fecha: date) -> SalarioPlus | None:
        stmt = (
            self._stmt()
            .where(SalarioPlus.grupo == grupo)
            .where(SalarioPlus.rol == rol)
            .where(SalarioPlus.desde <= fecha)
            .where(
                (SalarioPlus.hasta >= fecha) | (SalarioPlus.hasta.is_(None)),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_vigente_sin_hasta(self, grupo: str, rol: str) -> SalarioPlus | None:
        stmt = (
            self._stmt()
            .where(SalarioPlus.grupo == grupo)
            .where(SalarioPlus.rol == rol)
            .where(SalarioPlus.hasta.is_(None))
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def cerrar_vigencia(self, salario_id: uuid.UUID, hasta: date) -> None:
        await self._session.execute(
            update(SalarioPlus)
            .where(SalarioPlus.id == salario_id)
            .where(SalarioPlus.tenant_id == self._tenant_id)
            .values(hasta=hasta),
        )
        await self._session.flush()

    async def list_por_grupo(
        self,
        grupo: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[SalarioPlus]:
        stmt = self._stmt().order_by(SalarioPlus.grupo, SalarioPlus.rol, SalarioPlus.desde.desc())
        if grupo:
            stmt = stmt.where(SalarioPlus.grupo == grupo)
        stmt = stmt.offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all()
