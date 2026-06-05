import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db, require_permission
from app.schemas.auth import UserContext
from app.schemas.user_role import UserRoleAssign, UserRoleResponse
from app.services.user_role_service import UserRoleService

router = APIRouter(prefix='/api/v1/users', tags=['user-roles'])


@router.get('/{user_id}/roles', response_model=list[UserRoleResponse])
async def list_user_roles(
    user_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('rbac:gestionar'),
) -> list:
    service = UserRoleService(session, current_user.tenant_id)
    return await service.list_by_user(user_id)


@router.post('/{user_id}/roles', response_model=UserRoleResponse, status_code=status.HTTP_201_CREATED)
async def assign_role_to_user(
    user_id: uuid.UUID,
    data: UserRoleAssign,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('rbac:gestionar'),
) -> UserRoleResponse:
    service = UserRoleService(session, current_user.tenant_id)
    return await service.assign(user_id, data)


@router.delete('/{user_id}/roles/{role_id}', status_code=status.HTTP_204_NO_CONTENT)
async def unassign_role_from_user(
    user_id: uuid.UUID,
    role_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('rbac:gestionar'),
) -> None:
    service = UserRoleService(session, current_user.tenant_id)
    await service.unassign(user_id, role_id)
