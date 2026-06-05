import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db, require_permission
from app.schemas.asignacion import (
    AsignacionCreate,
    AsignacionListResponse,
    AsignacionResponse,
    AsignacionUpdate,
)
from app.schemas.auth import UserContext
from app.services.asignacion import AsignacionService

router = APIRouter(prefix='/api/v1/asignaciones', tags=['asignaciones'])


@router.get('', response_model=AsignacionListResponse)
async def list_asignaciones(
    usuario_id: uuid.UUID | None = None,
    rol: str | None = None,
    materia_id: uuid.UUID | None = None,
    carrera_id: uuid.UUID | None = None,
    cohorte_id: uuid.UUID | None = None,
    responsable_id: uuid.UUID | None = None,
    solo_vigentes: bool = False,
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('equipos:asignar'),
) -> AsignacionListResponse:
    service = AsignacionService(session, current_user.tenant_id)
    return await service.list_asignaciones(
        usuario_id=usuario_id,
        rol=rol,
        materia_id=materia_id,
        carrera_id=carrera_id,
        cohorte_id=cohorte_id,
        responsable_id=responsable_id,
        solo_vigentes=solo_vigentes,
        skip=skip,
        limit=limit,
    )


@router.post('', response_model=AsignacionResponse, status_code=status.HTTP_201_CREATED)
async def create_asignacion(
    data: AsignacionCreate,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('equipos:asignar'),
) -> AsignacionResponse:
    service = AsignacionService(session, current_user.tenant_id)
    return await service.create_asignacion(data)


@router.get('/{asignacion_id}', response_model=AsignacionResponse)
async def get_asignacion(
    asignacion_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('equipos:asignar'),
) -> AsignacionResponse:
    service = AsignacionService(session, current_user.tenant_id)
    return await service.get_asignacion(asignacion_id)


@router.patch('/{asignacion_id}', response_model=AsignacionResponse)
async def update_asignacion(
    asignacion_id: uuid.UUID,
    data: AsignacionUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('equipos:asignar'),
) -> AsignacionResponse:
    service = AsignacionService(session, current_user.tenant_id)
    return await service.update_asignacion(asignacion_id, data)


@router.delete('/{asignacion_id}', status_code=status.HTTP_200_OK)
async def delete_asignacion(
    asignacion_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('equipos:asignar'),
) -> dict:
    service = AsignacionService(session, current_user.tenant_id)
    await service.delete_asignacion(asignacion_id)
    return {'detail': 'Asignacion eliminada'}