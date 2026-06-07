import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db, require_permission
from app.schemas.auth import UserContext
from app.schemas.categoria_plus import (AsignacionMasivaRequest,
                                         CategoriaPlusCreate,
                                         CategoriaPlusResponse,
                                         CategoriaPlusUpdate)
from app.services.categoria_plus_service import CategoriaPlusService

router = APIRouter(prefix='/api/v1/admin/categorias-plus', tags=['categorias-plus'])


def _get_service(session: AsyncSession, current_user: UserContext) -> CategoriaPlusService:
    return CategoriaPlusService(session, current_user.tenant_id)


@router.get('', response_model=dict)
async def list_categorias(
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('estructura:gestionar'),
) -> dict:
    service = _get_service(session, current_user)
    return await service.list()


@router.post('', response_model=CategoriaPlusResponse, status_code=status.HTTP_201_CREATED)
async def create_categoria(
    data: CategoriaPlusCreate,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('estructura:gestionar'),
) -> CategoriaPlusResponse:
    service = _get_service(session, current_user)
    return await service.create(data)


@router.get('/{categoria_id}', response_model=CategoriaPlusResponse)
async def get_categoria(
    categoria_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('estructura:gestionar'),
) -> CategoriaPlusResponse:
    service = _get_service(session, current_user)
    return await service.get(categoria_id)


@router.put('/{categoria_id}', response_model=CategoriaPlusResponse)
async def update_categoria(
    categoria_id: uuid.UUID,
    data: CategoriaPlusUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('estructura:gestionar'),
) -> CategoriaPlusResponse:
    service = _get_service(session, current_user)
    return await service.update(categoria_id, data)


@router.delete('/{categoria_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_categoria(
    categoria_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('estructura:gestionar'),
) -> None:
    service = _get_service(session, current_user)
    await service.delete(categoria_id)


@router.patch('/{categoria_id}/toggle', response_model=CategoriaPlusResponse)
async def toggle_categoria(
    categoria_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('estructura:gestionar'),
) -> CategoriaPlusResponse:
    service = _get_service(session, current_user)
    return await service.toggle(categoria_id)


@router.get('/{categoria_id}/materias', response_model=dict)
async def list_materias_de_categoria(
    categoria_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('estructura:gestionar'),
) -> dict:
    service = _get_service(session, current_user)
    return await service.listar_materias(categoria_id)


@router.post('/asignacion-masiva', response_model=dict)
async def asignacion_masiva(
    data: AsignacionMasivaRequest,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('estructura:gestionar'),
) -> dict:
    service = _get_service(session, current_user)
    return await service.asignacion_masiva(data.categoria_plus_id, data.materia_ids)
