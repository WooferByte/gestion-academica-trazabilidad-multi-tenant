import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db, require_permission
from app.schemas.auth import UserContext
from app.schemas.aviso import (
    AckResponse,
    AvisoCreate,
    AvisoListResponse,
    AvisoResponse,
    AvisoUpdate,
)
from app.services.aviso_service import AvisoService

router = APIRouter(prefix='/api/v1/avisos', tags=['avisos'])


def _get_service(session: AsyncSession, current_user: UserContext) -> AvisoService:
    return AvisoService(session, current_user.tenant_id)


@router.post('', response_model=AvisoResponse, status_code=status.HTTP_201_CREATED)
async def crear_aviso(
    data: AvisoCreate,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('avisos:publicar'),
):
    service = _get_service(session, current_user)
    return await service.crear(data, current_user)


@router.get('', response_model=AvisoListResponse)
async def listar_avisos(
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
):
    service = _get_service(session, current_user)
    return await service.listar_avisos_para_usuario(current_user)


@router.get('/{aviso_id}', response_model=AvisoResponse)
async def obtener_aviso(
    aviso_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
):
    service = _get_service(session, current_user)
    return await service.obtener_aviso(aviso_id, current_user)


@router.patch('/{aviso_id}', response_model=AvisoResponse)
async def actualizar_aviso(
    aviso_id: uuid.UUID,
    data: AvisoUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('avisos:publicar'),
):
    service = _get_service(session, current_user)
    return await service.actualizar(aviso_id, data)


@router.delete('/{aviso_id}', status_code=status.HTTP_200_OK)
async def eliminar_aviso(
    aviso_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('avisos:publicar'),
):
    service = _get_service(session, current_user)
    return await service.desactivar(aviso_id)


@router.post('/{aviso_id}/ack', response_model=AckResponse, status_code=status.HTTP_201_CREATED)
async def confirmar_lectura(
    aviso_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
):
    service = _get_service(session, current_user)
    return await service.confirmar_lectura(aviso_id, current_user)
