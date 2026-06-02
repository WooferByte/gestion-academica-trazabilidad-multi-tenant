import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.user_role import UserRole


class PermissionResolver:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self._session = session
        self._tenant_id = tenant_id

    async def get_effective_permissions(self, user_id: uuid.UUID) -> list[str]:
        user_roles_stmt = (
            select(UserRole)
            .where(UserRole.user_id == user_id)
            .where(UserRole.tenant_id == self._tenant_id)
            .where(UserRole.deleted_at.is_(None))
        )
        user_roles_result = await self._session.execute(user_roles_stmt)
        user_roles = list(user_roles_result.scalars().all())

        if not user_roles:
            return []

        role_ids = [ur.role_id for ur in user_roles]

        rp_stmt = (
            select(RolePermission)
            .where(RolePermission.role_id.in_(role_ids))
            .where(RolePermission.tenant_id == self._tenant_id)
            .where(RolePermission.deleted_at.is_(None))
        )
        rp_result = await self._session.execute(rp_stmt)
        role_permisos = list(rp_result.scalars().all())

        if not role_permisos:
            return []

        permiso_ids = list({rp.permiso_id for rp in role_permisos})

        perm_stmt = (
            select(Permission)
            .where(Permission.id.in_(permiso_ids))
            .where(Permission.tenant_id == self._tenant_id)
            .where(Permission.deleted_at.is_(None))
        )
        perm_result = await self._session.execute(perm_stmt)
        permisos = list(perm_result.scalars().all())

        return list({p.codigo for p in permisos})
