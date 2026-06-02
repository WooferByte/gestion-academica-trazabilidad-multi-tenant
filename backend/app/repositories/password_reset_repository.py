import uuid
from datetime import datetime, timezone

from sqlalchemy import select

from app.models.user import PasswordResetToken
from app.repositories.base import BaseRepository


class PasswordResetTokenRepository(BaseRepository[PasswordResetToken]):
    __model__ = PasswordResetToken

    async def create_token(
        self, user_id: uuid.UUID, token_hash: str, expires_at: datetime,
    ) -> PasswordResetToken:
        return await self.create(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )

    async def get_by_token_hash(self, token_hash: str) -> PasswordResetToken | None:
        stmt = (
            select(self._model)
            .where(self._model.token_hash == token_hash)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def mark_used(self, token: PasswordResetToken) -> None:
        token.used_at = datetime.now(timezone.utc)
        await self._session.flush()
