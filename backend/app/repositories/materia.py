import uuid
from collections.abc import Sequence

from sqlalchemy import func, select, update

from app.models.materia import Materia
from app.repositories.base import BaseRepository


class MateriaRepository(BaseRepository[Materia]):
    __model__ = Materia

    async def get_by_codigo(self, codigo: str) -> Materia | None:
        stmt = self._stmt().where(Materia.codigo == codigo)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_categoria(self, categoria_id: uuid.UUID) -> Sequence[Materia]:
        stmt = self._stmt().where(Materia.categoria_plus_id == categoria_id)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def count_by_categoria(self, categoria_id: uuid.UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(Materia)
            .where(Materia.tenant_id == self._tenant_id)
            .where(Materia.deleted_at.is_(None))
            .where(Materia.categoria_plus_id == categoria_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def nullify_categoria(self, categoria_id: uuid.UUID) -> None:
        stmt = (
            update(Materia)
            .where(Materia.tenant_id == self._tenant_id)
            .where(Materia.categoria_plus_id == categoria_id)
            .where(Materia.deleted_at.is_(None))
            .values(categoria_plus_id=None)
        )
        await self._session.execute(stmt)
