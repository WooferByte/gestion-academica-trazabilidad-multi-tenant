import uuid

from fastapi import APIRouter, Depends, Header, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db, require_permission
from app.schemas.auth import UserContext
from app.schemas.comunicacion import (
    AprobarLoteRequest,
    CancelarRequest,
    ComunicacionBulkCreate,
    ComunicacionCreate,
    ComunicacionListResponse,
    ComunicacionPreviewRequest,
    ComunicacionPreviewResponse,
    ComunicacionResponse,
)
from app.services.comunicacion_service import ComunicacionService

router = APIRouter(prefix='/api/v1/comunicaciones', tags=['comunicaciones'])


def _get_service(session: AsyncSession, current_user: UserContext) -> ComunicacionService:
    return ComunicacionService(session, current_user.tenant_id)


def _extract_meta(request: Request) -> tuple[str, str]:
    ip = request.client.host if request.client else 'unknown'
    ua = request.headers.get('user-agent', 'unknown')
    return ip, ua


@router.post('/preview', response_model=ComunicacionPreviewResponse)
async def preview(
    data: ComunicacionPreviewRequest,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('comunicacion:enviar'),
) -> ComunicacionPreviewResponse:
    service = _get_service(session, current_user)
    return await service.preview(data)


@router.post('', response_model=ComunicacionResponse, status_code=status.HTTP_201_CREATED)
async def encolar(
    data: ComunicacionCreate,
    request: Request,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('comunicacion:enviar'),
) -> ComunicacionResponse:
    service = _get_service(session, current_user)
    ip, ua = _extract_meta(request)
    return await service.encolar(data, current_user, ip, ua)


@router.post('/lote', response_model=list[ComunicacionResponse], status_code=status.HTTP_201_CREATED)
async def encolar_lote(
    data: ComunicacionBulkCreate,
    request: Request,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('comunicacion:enviar'),
) -> list[ComunicacionResponse]:
    service = _get_service(session, current_user)
    ip, ua = _extract_meta(request)
    return await service.encolar_lote(data, current_user, ip, ua)


@router.post('/aprobar-lote')
async def aprobar_lote(
    data: AprobarLoteRequest,
    request: Request,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('comunicacion:aprobar'),
) -> dict:
    service = _get_service(session, current_user)
    ip, ua = _extract_meta(request)
    if data.accion == 'aprobar':
        return await service.aprobar_lote(data.lote_id, current_user, ip, ua)
    return await service.rechazar_lote(data.lote_id, current_user, ip, ua)


@router.post('/{comunicacion_id}/cancelar')
async def cancelar(
    comunicacion_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('comunicacion:enviar'),
) -> dict:
    service = _get_service(session, current_user)
    ip, ua = _extract_meta(request)
    return await service.cancelar(comunicacion_id, current_user, ip, ua)


@router.get('', response_model=ComunicacionListResponse)
async def listar(
    lote_id: uuid.UUID | None = Query(None),
    materia_id: uuid.UUID | None = Query(None),
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('comunicacion:enviar'),
) -> ComunicacionListResponse:
    service = _get_service(session, current_user)
    if lote_id is not None:
        return await service.listar_por_lote(lote_id, current_user)
    if materia_id is not None:
        return await service.listar_por_materia(materia_id, current_user)
    return ComunicacionListResponse(items=[], total=0)
