import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db, require_permission
from app.schemas.auth import UserContext
from app.schemas.permission import PermissionCreate, PermissionResponse, PermissionUpdate
from app.services.permission_service import PermissionService

router = APIRouter(prefix='/api/v1/permisos', tags=['permisos'])


@router.get('', response_model=dict)
async def list_permisos(
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('rbac:gestionar'),
) -> dict:
    service = PermissionService(session, current_user.tenant_id)
    return await service.list_permisos()


@router.post('', response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
async def create_permiso(
    data: PermissionCreate,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('rbac:gestionar'),
) -> PermissionResponse:
    service = PermissionService(session, current_user.tenant_id)
    return await service.create_permiso(data)


@router.get('/{permiso_id}', response_model=PermissionResponse)
async def get_permiso(
    permiso_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('rbac:gestionar'),
) -> PermissionResponse:
    service = PermissionService(session, current_user.tenant_id)
    return await service.get_permiso(permiso_id)


@router.put('/{permiso_id}', response_model=PermissionResponse)
async def update_permiso(
    permiso_id: uuid.UUID,
    data: PermissionUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('rbac:gestionar'),
) -> PermissionResponse:
    service = PermissionService(session, current_user.tenant_id)
    return await service.update_permiso(permiso_id, data)


@router.delete('/{permiso_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_permiso(
    permiso_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('rbac:gestionar'),
) -> None:
    service = PermissionService(session, current_user.tenant_id)
    await service.delete_permiso(permiso_id)
