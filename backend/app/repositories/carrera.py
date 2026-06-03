import uuid

from sqlalchemy import select

from app.models.carrera import Carrera
from app.repositories.base import BaseRepository


class CarreraRepository(BaseRepository[Carrera]):
    __model__ = Carrera

    async def get_by_codigo(self, codigo: str) -> Carrera | None:
        stmt = self._stmt().where(Carrera.codigo == codigo)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_cohortes_abiertas(self, carrera_id: uuid.UUID) -> list:
        from app.models.cohorte import Cohorte

        stmt = select(Cohorte).where(
            Cohorte.tenant_id == self._tenant_id,
            Cohorte.carrera_id == carrera_id,
            Cohorte.deleted_at.is_(None),
            Cohorte.vig_hasta.is_(None),
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
