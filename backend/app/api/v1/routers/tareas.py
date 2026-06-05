import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db, require_permission
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
from app.services.tarea_service import TareaService

router = APIRouter(prefix='/api/v1/tareas', tags=['tareas'])
admin_router = APIRouter(prefix='/api/v1/admin', tags=['admin'])


def _get_service(session: AsyncSession, current_user: UserContext) -> TareaService:
    return TareaService(session, current_user.tenant_id)


@router.get('/mis-tareas', response_model=TareaListResponse)
async def listar_mis_tareas(
    materia_id: Annotated[uuid.UUID | None, Query()] = None,
    estado: Annotated[str | None, Query()] = None,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
) -> TareaListResponse:
    service = _get_service(session, current_user)
    return await service.listar_mis_tareas(current_user, materia_id=materia_id, estado=estado)


@router.post('', response_model=TareaResponse, status_code=status.HTTP_201_CREATED)
async def crear_tarea(
    data: TareaCreate,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('tareas:gestionar'),
) -> TareaResponse:
    service = _get_service(session, current_user)
    return await service.crear_tarea(data, current_user)


@router.get('/{tarea_id}', response_model=TareaResponse)
async def obtener_tarea(
    tarea_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('tareas:gestionar'),
) -> TareaResponse:
    service = _get_service(session, current_user)
    return await service.obtener_tarea(tarea_id)


@router.patch('/{tarea_id}', response_model=TareaResponse)
async def actualizar_tarea(
    tarea_id: uuid.UUID,
    data: TareaUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('tareas:gestionar'),
) -> TareaResponse:
    service = _get_service(session, current_user)
    return await service.actualizar_tarea(tarea_id, data)


@router.patch('/{tarea_id}/estado', response_model=TareaResponse)
async def cambiar_estado(
    tarea_id: uuid.UUID,
    data: TareaEstadoUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('tareas:gestionar'),
) -> TareaResponse:
    service = _get_service(session, current_user)
    return await service.cambiar_estado(tarea_id, data)


@router.delete('/{tarea_id}', status_code=status.HTTP_200_OK)
async def eliminar_tarea(
    tarea_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('tareas:gestionar'),
) -> dict:
    service = _get_service(session, current_user)
    return await service.eliminar_tarea(tarea_id)


@router.post('/{tarea_id}/comentarios', response_model=ComentarioResponse, status_code=status.HTTP_201_CREATED)
async def agregar_comentario(
    tarea_id: uuid.UUID,
    data: ComentarioCreate,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('tareas:gestionar'),
) -> ComentarioResponse:
    service = _get_service(session, current_user)
    return await service.agregar_comentario(tarea_id, data, current_user)


@admin_router.get('/tareas', response_model=TareaListResponse)
async def listar_todas_las_tareas(
    materia_id: Annotated[uuid.UUID | None, Query()] = None,
    estado: Annotated[str | None, Query()] = None,
    asignado_a: Annotated[uuid.UUID | None, Query()] = None,
    asignado_por: Annotated[uuid.UUID | None, Query()] = None,
    search: Annotated[str | None, Query()] = None,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('tareas:gestionar'),
) -> TareaListResponse:
    service = _get_service(session, current_user)
    return await service.listar_todas(
        materia_id=materia_id,
        estado=estado,
        asignado_a=asignado_a,
        asignado_por=asignado_por,
        search=search,
    )
