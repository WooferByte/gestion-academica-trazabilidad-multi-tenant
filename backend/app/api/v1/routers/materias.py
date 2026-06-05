import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db, require_permission
from app.schemas.auth import UserContext
from app.schemas.materia import MateriaCreate, MateriaResponse, MateriaUpdate
from app.services.materia_service import MateriaService

router = APIRouter(prefix='/api/v1/admin/materias', tags=['materias'])


@router.get('', response_model=dict)
async def list_materias(
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('estructura:gestionar'),
) -> dict:
    service = MateriaService(session, current_user.tenant_id)
    return await service.list_materias()


@router.post('', response_model=MateriaResponse, status_code=status.HTTP_201_CREATED)
async def create_materia(
    data: MateriaCreate,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('estructura:gestionar'),
) -> MateriaResponse:
    service = MateriaService(session, current_user.tenant_id)
    return await service.create_materia(data)


@router.get('/{materia_id}', response_model=MateriaResponse)
async def get_materia(
    materia_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('estructura:gestionar'),
) -> MateriaResponse:
    service = MateriaService(session, current_user.tenant_id)
    return await service.get_materia(materia_id)


@router.put('/{materia_id}', response_model=MateriaResponse)
async def update_materia(
    materia_id: uuid.UUID,
    data: MateriaUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('estructura:gestionar'),
) -> MateriaResponse:
    service = MateriaService(session, current_user.tenant_id)
    return await service.update_materia(materia_id, data)


@router.delete('/{materia_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_materia(
    materia_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('estructura:gestionar'),
) -> None:
    service = MateriaService(session, current_user.tenant_id)
    await service.delete_materia(materia_id)
