import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db, require_permission
from app.schemas.auth import UserContext
from app.schemas.role import RoleCreate, RoleResponse, RoleUpdate
from app.services.role_service import RoleService

router = APIRouter(prefix='/api/v1/roles', tags=['roles'])


@router.get('', response_model=dict)
async def list_roles(
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('rbac:gestionar'),
) -> dict:
    service = RoleService(session, current_user.tenant_id)
    return await service.list_roles()


@router.post('', response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    data: RoleCreate,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('rbac:gestionar'),
) -> RoleResponse:
    service = RoleService(session, current_user.tenant_id)
    return await service.create_role(data)


@router.get('/{role_id}', response_model=RoleResponse)
async def get_role(
    role_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('rbac:gestionar'),
) -> RoleResponse:
    service = RoleService(session, current_user.tenant_id)
    return await service.get_role(role_id)


@router.put('/{role_id}', response_model=RoleResponse)
async def update_role(
    role_id: uuid.UUID,
    data: RoleUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('rbac:gestionar'),
) -> RoleResponse:
    service = RoleService(session, current_user.tenant_id)
    return await service.update_role(role_id, data)


@router.delete('/{role_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('rbac:gestionar'),
) -> None:
    service = RoleService(session, current_user.tenant_id)
    await service.delete_role(role_id)
