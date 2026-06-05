import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db, require_permission
from app.schemas.auth import UserContext
from app.schemas.carrera import CarreraCreate, CarreraResponse, CarreraUpdate
from app.services.carrera_service import CarreraService

router = APIRouter(prefix='/api/v1/admin/carreras', tags=['carreras'])


@router.get('', response_model=dict)
async def list_carreras(
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('estructura:gestionar'),
) -> dict:
    service = CarreraService(session, current_user.tenant_id)
    return await service.list_carreras()


@router.post('', response_model=CarreraResponse, status_code=status.HTTP_201_CREATED)
async def create_carrera(
    data: CarreraCreate,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('estructura:gestionar'),
) -> CarreraResponse:
    service = CarreraService(session, current_user.tenant_id)
    return await service.create_carrera(data)


@router.get('/{carrera_id}', response_model=CarreraResponse)
async def get_carrera(
    carrera_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('estructura:gestionar'),
) -> CarreraResponse:
    service = CarreraService(session, current_user.tenant_id)
    return await service.get_carrera(carrera_id)


@router.put('/{carrera_id}', response_model=CarreraResponse)
async def update_carrera(
    carrera_id: uuid.UUID,
    data: CarreraUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('estructura:gestionar'),
) -> CarreraResponse:
    service = CarreraService(session, current_user.tenant_id)
    return await service.update_carrera(carrera_id, data)


@router.delete('/{carrera_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_carrera(
    carrera_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('estructura:gestionar'),
) -> None:
    service = CarreraService(session, current_user.tenant_id)
    await service.delete_carrera(carrera_id)
