import uuid

from sqlalchemy import select

from app.models.programa_materia import ProgramaMateria
from app.repositories.base import BaseRepository


class ProgramaMateriaRepository(BaseRepository[ProgramaMateria]):
    __model__ = ProgramaMateria

    async def get_by_materia_carrera_cohorte(
        self, materia_id: uuid.UUID, carrera_id: uuid.UUID, cohorte_id: uuid.UUID,
    ) -> ProgramaMateria | None:
        stmt = (
            self._stmt()
            .where(ProgramaMateria.materia_id == materia_id)
            .where(ProgramaMateria.carrera_id == carrera_id)
            .where(ProgramaMateria.cohorte_id == cohorte_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
