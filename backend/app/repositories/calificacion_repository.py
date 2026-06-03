import uuid
from collections.abc import Sequence
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.calificacion import Calificacion
from app.repositories.base import BaseRepository


class CalificacionRepository(BaseRepository[Calificacion]):
    __model__ = Calificacion

    async def bulk_create(self, entries: list[dict]) -> list[Calificacion]:
        instances = []
        for data in entries:
            instance = Calificacion(
                tenant_id=self._tenant_id,
                entrada_padron_id=data['entrada_padron_id'],
                materia_id=data['materia_id'],
                cohorte_id=data['cohorte_id'],
                actividad=data['actividad'],
                nota_numerica=data.get('nota_numerica'),
                nota_textual=data.get('nota_textual'),
                origen=data.get('origen', 'Importado'),
            )
            self._session.add(instance)
            instances.append(instance)
        await self._session.flush()
        return instances

    async def get_by_materia(
        self,
        materia_id: uuid.UUID,
        cohorte_id: uuid.UUID | None = None,
        entrada_padron_id: uuid.UUID | None = None,
    ) -> Sequence[Calificacion]:
        stmt = (
            self._stmt()
            .where(Calificacion.materia_id == materia_id)
        )
        if cohorte_id is not None:
            stmt = stmt.where(Calificacion.cohorte_id == cohorte_id)
        if entrada_padron_id is not None:
            stmt = stmt.where(Calificacion.entrada_padron_id == entrada_padron_id)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_by_entrada_padron(
        self, entrada_padron_id: uuid.UUID,
    ) -> Sequence[Calificacion]:
        stmt = (
            self._stmt()
            .where(Calificacion.entrada_padron_id == entrada_padron_id)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_by_actividad(
        self,
        materia_id: uuid.UUID,
        cohorte_id: uuid.UUID,
        actividad: str,
    ) -> Sequence[Calificacion]:
        stmt = (
            self._stmt()
            .where(Calificacion.materia_id == materia_id)
            .where(Calificacion.cohorte_id == cohorte_id)
            .where(Calificacion.actividad == actividad)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def soft_delete_by_materia(
        self, materia_id: uuid.UUID, cohorte_id: uuid.UUID,
    ) -> int:
        stmt = (
            select(Calificacion)
            .where(Calificacion.materia_id == materia_id)
            .where(Calificacion.cohorte_id == cohorte_id)
            .where(Calificacion.tenant_id == self._tenant_id)
            .where(Calificacion.deleted_at.is_(None))
        )
        result = await self._session.execute(stmt)
        calificaciones = list(result.scalars().all())
        now = datetime.now(timezone.utc)
        for c in calificaciones:
            c.deleted_at = now
        await self._session.flush()
        return len(calificaciones)
