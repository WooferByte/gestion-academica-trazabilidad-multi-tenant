import uuid

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decrypt
from app.models.tarea import ComentarioTarea, EstadoTarea, Tarea
from app.models.user import User
from app.repositories.tarea_repository import ComentarioTareaRepository, TareaRepository
from app.schemas.auth import UserContext
from app.schemas.tarea import (
    ComentarioCreate,
    ComentarioResponse,
    TareaCreate,
    TareaEstadoUpdate,
    TareaListResponse,
    TareaResponse,
    TareaUpdate,
)

ESTADO_TRANSITIONS: dict[EstadoTarea, list[EstadoTarea]] = {
    EstadoTarea.PENDIENTE: [EstadoTarea.EN_PROGRESO, EstadoTarea.CANCELADA],
    EstadoTarea.EN_PROGRESO: [EstadoTarea.RESUELTA, EstadoTarea.CANCELADA],
    EstadoTarea.RESUELTA: [],
    EstadoTarea.CANCELADA: [],
}


class TareaService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self._session = session
        self._repo = TareaRepository(session, tenant_id)
        self._comentario_repo = ComentarioTareaRepository(session, tenant_id)

    async def crear_tarea(self, data: TareaCreate, current_user: UserContext) -> TareaResponse:
        asignado_exists = await self._session.execute(
            select(User).where(User.id == data.asignado_a)
            .where(User.tenant_id == current_user.tenant_id)
            .where(User.deleted_at.is_(None))
        )
        if not asignado_exists.scalar_one_or_none():
            raise HTTPException(status_code=400, detail='Usuario asignado no encontrado en el tenant')

        tarea = await self._repo.create(
            materia_id=data.materia_id,
            asignado_a=data.asignado_a,
            asignado_por=current_user.user_id,
            estado=EstadoTarea.PENDIENTE.value,
            descripcion=data.descripcion,
            contexto_id=data.contexto_id,
        )
        return await self._build_response(tarea)

    async def actualizar_tarea(self, tarea_id: uuid.UUID, data: TareaUpdate) -> TareaResponse:
        tarea = await self._repo.get(tarea_id)
        if not tarea:
            raise HTTPException(status_code=404, detail='Tarea no encontrada')

        update_kwargs = data.model_dump(exclude_unset=True)
        if not update_kwargs:
            raise HTTPException(status_code=400, detail='No hay campos para actualizar')

        if 'asignado_a' in update_kwargs:
            asignado_exists = await self._session.execute(
                select(User).where(User.id == update_kwargs['asignado_a'])
                .where(User.deleted_at.is_(None))
            )
            if not asignado_exists.scalar_one_or_none():
                raise HTTPException(status_code=400, detail='Usuario asignado no encontrado')

        tarea = await self._repo.update(tarea, **update_kwargs)
        return await self._build_response(tarea)

    async def cambiar_estado(self, tarea_id: uuid.UUID, data: TareaEstadoUpdate) -> TareaResponse:
        tarea = await self._repo.get(tarea_id)
        if not tarea:
            raise HTTPException(status_code=404, detail='Tarea no encontrada')

        try:
            nuevo = EstadoTarea(data.estado)
        except ValueError:
            raise HTTPException(status_code=400, detail=f'Estado inválido: {data.estado}')

        actual = EstadoTarea(tarea.estado)
        allowed = ESTADO_TRANSITIONS.get(actual, [])
        if nuevo not in allowed:
            raise HTTPException(
                status_code=400,
                detail=f'Transición no permitida: {actual.value} → {nuevo.value}. '
                       f'Transiciones permitidas: {[e.value for e in allowed]}',
            )

        tarea = await self._repo.update(tarea, estado=nuevo.value)
        return await self._build_response(tarea)

    async def listar_mis_tareas(
        self,
        current_user: UserContext,
        materia_id: uuid.UUID | None = None,
        estado: str | None = None,
    ) -> TareaListResponse:
        tareas = await self._repo.list_mis_tareas(
            user_id=current_user.user_id,
            materia_id=materia_id,
            estado=estado,
        )
        items = [await self._build_response(t) for t in tareas]
        return TareaListResponse(items=items, total=len(items))

    async def listar_todas(
        self,
        materia_id: uuid.UUID | None = None,
        estado: str | None = None,
        asignado_a: uuid.UUID | None = None,
        asignado_por: uuid.UUID | None = None,
        search: str | None = None,
    ) -> TareaListResponse:
        tareas = await self._repo.list_all_filters(
            materia_id=materia_id,
            estado=estado,
            asignado_a=asignado_a,
            asignado_por=asignado_por,
            search=search,
        )
        items = [await self._build_response(t) for t in tareas]
        return TareaListResponse(items=items, total=len(items))

    async def obtener_tarea(self, tarea_id: uuid.UUID) -> TareaResponse:
        tarea = await self._repo.get(tarea_id)
        if not tarea:
            raise HTTPException(status_code=404, detail='Tarea no encontrada')
        return await self._build_response(tarea)

    async def eliminar_tarea(self, tarea_id: uuid.UUID) -> dict:
        tarea = await self._repo.get(tarea_id)
        if not tarea:
            raise HTTPException(status_code=404, detail='Tarea no encontrada')
        await self._repo.soft_delete(tarea)
        return {'detalle': 'Tarea eliminada'}

    async def agregar_comentario(
        self, tarea_id: uuid.UUID, data: ComentarioCreate, current_user: UserContext,
    ) -> ComentarioResponse:
        tarea = await self._repo.get(tarea_id)
        if not tarea:
            raise HTTPException(status_code=404, detail='Tarea no encontrada')

        comentario = await self._comentario_repo.add_comentario(
            tarea_id=tarea_id,
            autor_id=current_user.user_id,
            texto=data.texto,
        )
        return ComentarioResponse(
            id=comentario.id,
            tarea_id=comentario.tarea_id,
            autor_id=comentario.autor_id,
            texto=comentario.texto,
            creado_at=comentario.creado_at,
        )

    async def _build_response(self, tarea: Tarea) -> TareaResponse:
        comentarios = await self._comentario_repo.list_by_tarea(tarea.id)
        comentarios_resp = [
            ComentarioResponse(
                id=c.id,
                tarea_id=c.tarea_id,
                autor_id=c.autor_id,
                texto=c.texto,
                creado_at=c.creado_at,
            )
            for c in comentarios
        ]
        # Resolve user names (use email as fallback since names are encrypted)
        def _get_user_name(user: User | None) -> str:
            if user and hasattr(user, 'email') and user.email:
                return user.email.split('@')[0]
            return ''
        a_asignado = await self._session.execute(select(User).where(User.id == tarea.asignado_a))
        u_asignado = a_asignado.scalar_one_or_none()
        a_por = await self._session.execute(select(User).where(User.id == tarea.asignado_por))
        u_por = a_por.scalar_one_or_none()

        return TareaResponse(
            id=tarea.id,
            tenant_id=tarea.tenant_id,
            materia_id=tarea.materia_id,
            asignado_a=tarea.asignado_a,
            asignado_a_nombre=_get_user_name(u_asignado),
            asignado_por=tarea.asignado_por,
            asignado_por_nombre=_get_user_name(u_por),
            estado=tarea.estado.value if hasattr(tarea.estado, 'value') else str(tarea.estado),
            descripcion=tarea.descripcion,
            contexto_id=tarea.contexto_id,
            comentarios=comentarios_resp,
            created_at=tarea.created_at,
            updated_at=tarea.updated_at,
        )
