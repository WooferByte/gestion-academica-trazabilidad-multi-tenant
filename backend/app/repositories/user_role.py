import uuid

from sqlalchemy import select

from app.models.user_role import UserRole
from app.repositories.base import BaseRepository


class UserRoleRepository(BaseRepository[UserRole]):
    __model__ = UserRole

    async def get_by_user_and_role(
        self, user_id: uuid.UUID, role_id: uuid.UUID,
    ) -> UserRole | None:
        stmt = (
            self._stmt()
            .where(UserRole.user_id == user_id)
            .where(UserRole.role_id == role_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user_and_role_including_deleted(
        self, user_id: uuid.UUID, role_id: uuid.UUID,
    ) -> UserRole | None:
        stmt = select(UserRole).where(
            UserRole.tenant_id == self._tenant_id,
            UserRole.user_id == user_id,
            UserRole.role_id == role_id,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: uuid.UUID) -> list[UserRole]:
        stmt = self._stmt().where(UserRole.user_id == user_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def delete_by_user_and_role(
        self, user_id: uuid.UUID, role_id: uuid.UUID,
    ) -> UserRole | None:
        ur = await self.get_by_user_and_role(user_id, role_id)
        if ur:
            return await self.soft_delete(ur)
        return None
