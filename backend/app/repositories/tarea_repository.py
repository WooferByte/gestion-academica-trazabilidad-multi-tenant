import uuid
from collections.abc import Sequence
from datetime import datetime, timezone

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tarea import ComentarioTarea, Tarea
from app.repositories.base import BaseRepository


class TareaRepository(BaseRepository[Tarea]):
    __model__ = Tarea

    async def list_mis_tareas(
        self,
        user_id: uuid.UUID,
        materia_id: uuid.UUID | None = None,
        estado: str | None = None,
    ) -> Sequence[Tarea]:
        stmt = self._stmt().where(Tarea.asignado_a == user_id)
        if materia_id:
            stmt = stmt.where(Tarea.materia_id == materia_id)
        if estado:
            stmt = stmt.where(Tarea.estado == estado)
        stmt = stmt.order_by(Tarea.created_at.desc())
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def list_all_filters(
        self,
        materia_id: uuid.UUID | None = None,
        estado: str | None = None,
        asignado_a: uuid.UUID | None = None,
        asignado_por: uuid.UUID | None = None,
        search: str | None = None,
    ) -> Sequence[Tarea]:
        stmt = self._stmt()
        if materia_id:
            stmt = stmt.where(Tarea.materia_id == materia_id)
        if estado:
            stmt = stmt.where(Tarea.estado == estado)
        if asignado_a:
            stmt = stmt.where(Tarea.asignado_a == asignado_a)
        if asignado_por:
            stmt = stmt.where(Tarea.asignado_por == asignado_por)
        if search:
            stmt = stmt.where(Tarea.descripcion.ilike(f'%{search}%'))
        stmt = stmt.order_by(Tarea.created_at.desc())
        result = await self._session.execute(stmt)
        return result.scalars().all()


class ComentarioTareaRepository(BaseRepository[ComentarioTarea]):
    __model__ = ComentarioTarea

    async def list_by_tarea(self, tarea_id: uuid.UUID) -> Sequence[ComentarioTarea]:
        stmt = self._stmt().where(ComentarioTarea.tarea_id == tarea_id).order_by(ComentarioTarea.creado_at.asc())
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def add_comentario(
        self, tarea_id: uuid.UUID, autor_id: uuid.UUID, texto: str,
    ) -> ComentarioTarea:
        comentario = ComentarioTarea(
            tenant_id=self._tenant_id,
            tarea_id=tarea_id,
            autor_id=autor_id,
            texto=texto,
            creado_at=datetime.now(timezone.utc),
        )
        self._session.add(comentario)
        await self._session.flush()
        return comentario
