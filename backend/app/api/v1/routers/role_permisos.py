import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db, require_permission
from app.schemas.auth import UserContext
from app.schemas.role_permission import RolePermissionAssign, RolePermissionResponse
from app.services.role_permission_service import RolePermissionService

router = APIRouter(prefix='/api/v1/roles', tags=['role-permisos'])


@router.get('/{role_id}/permisos', response_model=list[RolePermissionResponse])
async def list_role_permisos(
    role_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('rbac:gestionar'),
) -> list:
    service = RolePermissionService(session, current_user.tenant_id)
    return await service.list_by_role(role_id)


@router.post('/{role_id}/permisos', response_model=RolePermissionResponse, status_code=status.HTTP_201_CREATED)
async def assign_permiso_to_role(
    role_id: uuid.UUID,
    data: RolePermissionAssign,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('rbac:gestionar'),
) -> RolePermissionResponse:
    service = RolePermissionService(session, current_user.tenant_id)
    return await service.assign(role_id, data)


@router.delete('/{role_id}/permisos/{permiso_id}', status_code=status.HTTP_204_NO_CONTENT)
async def unassign_permiso_from_role(
    role_id: uuid.UUID,
    permiso_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('rbac:gestionar'),
) -> None:
    service = RolePermissionService(session, current_user.tenant_id)
    await service.unassign(role_id, permiso_id)
