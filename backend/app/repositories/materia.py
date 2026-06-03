from app.models.materia import Materia
from app.repositories.base import BaseRepository


class MateriaRepository(BaseRepository[Materia]):
    __model__ = Materia

    async def get_by_codigo(self, codigo: str) -> Materia | None:
        stmt = self._stmt().where(Materia.codigo == codigo)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
