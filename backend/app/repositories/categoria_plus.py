from sqlalchemy import func

from app.models.categoria_plus import CategoriaPlus
from app.repositories.base import BaseRepository


class CategoriaPlusRepository(BaseRepository[CategoriaPlus]):
    __model__ = CategoriaPlus

    async def get_by_codigo(self, codigo: str) -> CategoriaPlus | None:
        stmt = self._stmt().where(func.lower(CategoriaPlus.codigo) == codigo.lower())
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
