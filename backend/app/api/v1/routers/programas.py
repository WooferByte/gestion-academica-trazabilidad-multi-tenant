import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db, require_permission
from app.schemas.auth import UserContext
from app.schemas.programa_materia import (
    ProgramaMateriaCreate,
    ProgramaMateriaResponse,
    ProgramaMateriaUpdate,
)
from app.services.programa_materia_service import ProgramaMateriaService

router = APIRouter(prefix='/api/v1/admin/programas', tags=['programas'])


@router.get('', response_model=dict)
async def list_programas(
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('estructura:gestionar'),
) -> dict:
    service = ProgramaMateriaService(session, current_user.tenant_id)
    return await service.list_programas()


@router.post('', response_model=ProgramaMateriaResponse, status_code=status.HTTP_201_CREATED)
async def create_programa(
    data: ProgramaMateriaCreate,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('estructura:gestionar'),
) -> ProgramaMateriaResponse:
    service = ProgramaMateriaService(session, current_user.tenant_id)
    return await service.create_programa(data)


@router.get('/{programa_id}', response_model=ProgramaMateriaResponse)
async def get_programa(
    programa_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('estructura:gestionar'),
) -> ProgramaMateriaResponse:
    service = ProgramaMateriaService(session, current_user.tenant_id)
    return await service.get_programa(programa_id)


@router.put('/{programa_id}', response_model=ProgramaMateriaResponse)
async def update_programa(
    programa_id: uuid.UUID,
    data: ProgramaMateriaUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('estructura:gestionar'),
) -> ProgramaMateriaResponse:
    service = ProgramaMateriaService(session, current_user.tenant_id)
    return await service.update_programa(programa_id, data)


@router.delete('/{programa_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_programa(
    programa_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('estructura:gestionar'),
) -> None:
    service = ProgramaMateriaService(session, current_user.tenant_id)
    await service.delete_programa(programa_id)
