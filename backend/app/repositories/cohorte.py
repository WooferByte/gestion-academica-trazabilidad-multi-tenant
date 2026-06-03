import uuid

from app.models.cohorte import Cohorte
from app.repositories.base import BaseRepository


class CohorteRepository(BaseRepository[Cohorte]):
    __model__ = Cohorte

    async def get_by_nombre_and_carrera(self, nombre: str, carrera_id: uuid.UUID) -> Cohorte | None:
        stmt = self._stmt().where(
            Cohorte.nombre == nombre,
            Cohorte.carrera_id == carrera_id,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
