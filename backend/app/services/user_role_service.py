import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.role import RoleRepository
from app.repositories.user_role import UserRoleRepository
from app.schemas.user_role import UserRoleAssign
from app.models.user import User
from sqlalchemy import select


class UserRoleService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self._session = session
        self._tenant_id = tenant_id
        self._ur_repo = UserRoleRepository(session, tenant_id)
        self._role_repo = RoleRepository(session, tenant_id)

    async def _get_user_or_404(self, user_id: uuid.UUID) -> User:
        stmt = (
            select(User)
            .where(User.id == user_id)
            .where(User.tenant_id == self._tenant_id)
            .where(User.deleted_at.is_(None))
        )
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail='Usuario no encontrado')
        return user

    async def list_by_user(self, user_id: uuid.UUID):
        await self._get_user_or_404(user_id)
        return await self._ur_repo.list_by_user(user_id)

    async def assign(self, user_id: uuid.UUID, data: UserRoleAssign):
        user = await self._get_user_or_404(user_id)
        role = await self._role_repo.get(data.role_id)
        if not role:
            raise HTTPException(status_code=404, detail='Rol no encontrado')
        existing = await self._ur_repo.get_by_user_and_role_including_deleted(
            user_id, data.role_id,
        )
        if existing:
            if existing.deleted_at is not None:
                from datetime import datetime, timezone
                existing.deleted_at = None
                await self._session.flush()
                return existing
            raise HTTPException(status_code=409, detail='El rol ya está asignado a este usuario')
        return await self._ur_repo.create(user_id=user_id, role_id=data.role_id)

    async def unassign(self, user_id: uuid.UUID, role_id: uuid.UUID):
        await self._get_user_or_404(user_id)
        role = await self._role_repo.get(role_id)
        if not role:
            raise HTTPException(status_code=404, detail='Rol no encontrado')
        deleted = await self._ur_repo.delete_by_user_and_role(user_id, role_id)
        if not deleted:
            raise HTTPException(status_code=404, detail='Asignación no encontrada')
