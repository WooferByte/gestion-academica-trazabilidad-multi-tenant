import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db, require_permission
from app.schemas.asignacion import (
    AsignacionListResponse,
    AsignacionMasivaRequest,
    AsignacionResponse,
    ClonarEquipoRequest,
    ExportRow,
    VigenciaEquipoRequest,
    VigenciaUpdateResponse,
)
from app.schemas.auth import UserContext
from app.services.asignacion import AsignacionService

router = APIRouter(prefix='/api/v1/equipos', tags=['equipos'])


@router.get('/mis-equipos', response_model=AsignacionListResponse)
async def mis_equipos(
    materia_id: uuid.UUID | None = None,
    cohorte_id: uuid.UUID | None = None,
    solo_vigentes: bool = False,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
):
    service = AsignacionService(session, current_user.tenant_id)
    return await service.mis_equipos(
        usuario_id=current_user.user_id,
        materia_id=materia_id,
        cohorte_id=cohorte_id,
        solo_vigentes=solo_vigentes,
    )


@router.post(
    '/asignacion-masiva',
    response_model=list[AsignacionResponse],
    status_code=status.HTTP_201_CREATED,
)
async def asignacion_masiva(
    data: AsignacionMasivaRequest,
    request: Request,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('equipos:asignar'),
):
    service = AsignacionService(session, current_user.tenant_id)
    result = await service.asignacion_masiva(
        data,
        current_user,
        ip=request.client.host if request.client else 'unknown',
        user_agent=request.headers.get('user-agent', 'unknown'),
    )
    return result


@router.post(
    '/clonar',
    response_model=list[AsignacionResponse],
    status_code=status.HTTP_201_CREATED,
)
async def clonar_equipo(
    data: ClonarEquipoRequest,
    request: Request,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('equipos:asignar'),
):
    service = AsignacionService(session, current_user.tenant_id)
    result = await service.clonar_equipo(
        data,
        current_user,
        ip=request.client.host if request.client else 'unknown',
        user_agent=request.headers.get('user-agent', 'unknown'),
    )
    return result


@router.patch('/vigencia', response_model=VigenciaUpdateResponse)
async def modificar_vigencia(
    data: VigenciaEquipoRequest,
    request: Request,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('equipos:asignar'),
):
    service = AsignacionService(session, current_user.tenant_id)
    return await service.modificar_vigencia(
        data,
        current_user,
        ip=request.client.host if request.client else 'unknown',
        user_agent=request.headers.get('user-agent', 'unknown'),
    )


@router.get('/exportar')
async def exportar_equipo(
    materia_id: uuid.UUID | None = None,
    carrera_id: uuid.UUID | None = None,
    cohorte_id: uuid.UUID | None = None,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('equipos:asignar'),
):
    from fastapi.responses import StreamingResponse

    service = AsignacionService(session, current_user.tenant_id)
    csv_content = await service.exportar_equipo(
        materia_id=materia_id,
        carrera_id=carrera_id,
        cohorte_id=cohorte_id,
    )
    return StreamingResponse(
        iter([csv_content]),
        media_type='text/csv',
        headers={
            'Content-Disposition': 'attachment; filename=equipo-docente.csv',
        },
    )
