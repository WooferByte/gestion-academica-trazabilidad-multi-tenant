import uuid

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db, require_permission
from app.schemas.auth import UserContext
from app.schemas.cohorte import CohorteCreate, CohorteResponse, CohorteUpdate
from app.services.cohorte_service import CohorteService


class CohorteFilterParams(BaseModel):
    model_config = ConfigDict(extra='forbid')
    carrera_id: uuid.UUID | None = None


router = APIRouter(prefix='/api/v1/admin/cohortes', tags=['cohortes'])


@router.get('', response_model=dict)
async def list_cohortes(
    params: CohorteFilterParams = Depends(),
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('estructura:gestionar'),
) -> dict:
    service = CohorteService(session, current_user.tenant_id)
    return await service.list_cohortes(carrera_id=params.carrera_id)


@router.post('', response_model=CohorteResponse, status_code=status.HTTP_201_CREATED)
async def create_cohorte(
    data: CohorteCreate,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('estructura:gestionar'),
) -> CohorteResponse:
    service = CohorteService(session, current_user.tenant_id)
    return await service.create_cohorte(data)


@router.get('/{cohorte_id}', response_model=CohorteResponse)
async def get_cohorte(
    cohorte_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('estructura:gestionar'),
) -> CohorteResponse:
    service = CohorteService(session, current_user.tenant_id)
    return await service.get_cohorte(cohorte_id)


@router.put('/{cohorte_id}', response_model=CohorteResponse)
async def update_cohorte(
    cohorte_id: uuid.UUID,
    data: CohorteUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('estructura:gestionar'),
) -> CohorteResponse:
    service = CohorteService(session, current_user.tenant_id)
    return await service.update_cohorte(cohorte_id, data)


@router.delete('/{cohorte_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_cohorte(
    cohorte_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('estructura:gestionar'),
) -> None:
    service = CohorteService(session, current_user.tenant_id)
    await service.delete_cohorte(cohorte_id)
