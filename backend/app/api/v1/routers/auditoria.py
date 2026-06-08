import uuid
from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db, require_permission
from app.repositories.audit_repository import AuditLogFiltros
from app.schemas.auth import UserContext
from app.schemas.auditoria import (
    AccionPorDiaResponse,
    AccionesPorDiaQuery,
    AuditoriaLogQuery,
    ComunicacionesDocenteResponse,
    ComunicacionesQuery,
    InteraccionesDocenteMateriaResponse,
    InteraccionesQuery,
    LogEntryResponse,
)
from app.services.auditoria_service import AuditoriaService

router = APIRouter(prefix='/api/v1/auditoria', tags=['auditoria'])


@router.get(
    '/acciones-por-dia',
    response_model=list[AccionPorDiaResponse],
)
async def acciones_por_dia(
    params: AccionesPorDiaQuery = Depends(),
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('auditoria:ver'),
) -> list[AccionPorDiaResponse]:
    service = AuditoriaService(session, current_user)
    return await service.acciones_por_dia(
        fecha_desde=params.fecha_desde,
        fecha_hasta=params.fecha_hasta,
    )


@router.get(
    '/comunicaciones-por-docente',
    response_model=list[ComunicacionesDocenteResponse],
)
async def comunicaciones_por_docente(
    params: ComunicacionesQuery = Depends(),
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('auditoria:ver'),
) -> list[ComunicacionesDocenteResponse]:
    service = AuditoriaService(session, current_user)
    return await service.comunicaciones_por_docente(
        fecha_desde=params.fecha_desde,
        fecha_hasta=params.fecha_hasta,
        materia_id=params.materia_id,
        usuario_id=params.usuario_id,
    )


@router.get(
    '/interacciones-por-docente-materia',
    response_model=list[InteraccionesDocenteMateriaResponse],
)
async def interacciones_por_docente_materia(
    params: InteraccionesQuery = Depends(),
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('auditoria:ver'),
) -> list[InteraccionesDocenteMateriaResponse]:
    service = AuditoriaService(session, current_user)
    return await service.interacciones_por_docente_materia(
        fecha_desde=params.fecha_desde,
        fecha_hasta=params.fecha_hasta,
        materia_id=params.materia_id,
        usuario_id=params.usuario_id,
    )


@router.get(
    '/log',
    response_model=list[LogEntryResponse],
)
async def list_log(
    params: AuditoriaLogQuery = Depends(),
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('auditoria:ver'),
) -> list[LogEntryResponse]:
    service = AuditoriaService(session, current_user)
    filtros = AuditLogFiltros(
        fecha_desde=params.fecha_desde,
        fecha_hasta=params.fecha_hasta,
        materia_id=params.materia_id,
        usuario_id=params.usuario_id,
        accion=params.accion,
        max_records=params.max_records,
    )
    return await service.list_log(filtros)
