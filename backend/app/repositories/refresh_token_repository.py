import uuid
from datetime import datetime, timezone

from sqlalchemy import select, update

from app.models.user import RefreshToken
from app.repositories.base import BaseRepository


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    __model__ = RefreshToken

    async def create_token(
        self, user_id: uuid.UUID, token_hash: str, family_id: uuid.UUID,
        expires_at: datetime,
    ) -> RefreshToken:
        return await self.create(
            user_id=user_id,
            token_hash=token_hash,
            family_id=family_id,
            expires_at=expires_at,
        )

    async def get_by_token_hash(self, token_hash: str) -> RefreshToken | None:
        stmt = (
            select(self._model)
            .where(self._model.token_hash == token_hash)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def revoke(self, token: RefreshToken) -> None:
        token.revoked_at = datetime.now(timezone.utc)
        await self._session.flush()

    async def revoke_family(self, family_id: uuid.UUID) -> None:
        stmt = (
            update(self._model)
            .where(self._model.family_id == family_id)
            .where(self._model.revoked_at.is_(None))
            .values(revoked_at=datetime.now(timezone.utc))
        )
        await self._session.execute(stmt)
        await self._session.flush()

    async def revoke_all_for_user(self, user_id: uuid.UUID) -> None:
        stmt = (
            update(self._model)
            .where(self._model.user_id == user_id)
            .where(self._model.revoked_at.is_(None))
            .values(revoked_at=datetime.now(timezone.utc))
        )
        await self._session.execute(stmt)
        await self._session.flush()
