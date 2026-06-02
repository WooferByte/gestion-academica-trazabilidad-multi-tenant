import hashlib
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.security import (
    create_access_token,
    create_2fa_token,
    decode_token,
    decrypt,
    encrypt,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.password_reset_repository import PasswordResetTokenRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import UserContext


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode('utf-8')).hexdigest()


class AuthService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self._session = session
        self._tenant_id = tenant_id
        self._user_repo = UserRepository(session, tenant_id)
        self._refresh_repo = RefreshTokenRepository(session, tenant_id)
        self._reset_repo = PasswordResetTokenRepository(session, tenant_id)

    async def authenticate(self, email: str, password: str) -> User | None:
        user = await self._user_repo.get_by_email(email)
        if not user:
            return None
        if user.deleted_at is not None:
            return None
        if not user.is_active:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    async def create_session(self, user: User) -> dict:
        access_token = create_access_token(
            user_id=str(user.id),
            tenant_id=str(user.tenant_id),
            roles=user.roles,
        )
        settings = Settings()
        expires_in = settings.access_token_expire_minutes * 60

        refresh_token_value = str(uuid.uuid4())
        token_hash = _hash_token(refresh_token_value)
        family_id = uuid.uuid4()
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.refresh_token_expire_days,
        )

        await self._refresh_repo.create_token(
            user_id=user.id,
            token_hash=token_hash,
            family_id=family_id,
            expires_at=expires_at,
        )

        return {
            'access_token': access_token,
            'refresh_token': refresh_token_value,
            'token_type': 'bearer',
            'expires_in': expires_in,
        }

    async def refresh_session(self, refresh_token_value: str) -> dict:
        token_hash = _hash_token(refresh_token_value)
        stored = await self._refresh_repo.get_by_token_hash(token_hash)
        if not stored:
            raise ValueError('Token inválido o revocado')

        if stored.revoked_at is not None:
            await self._refresh_repo.revoke_family(stored.family_id)
            raise ValueError('Token inválido o revocado')

        if stored.expires_at < datetime.now(timezone.utc):
            raise ValueError('Token inválido o revocado')

        user = await self._user_repo.get(stored.user_id)
        if not user:
            raise ValueError('Token inválido o revocado')

        await self._refresh_repo.revoke(stored)

        family_id = stored.family_id
        new_refresh = str(uuid.uuid4())
        new_hash = _hash_token(new_refresh)
        settings = Settings()
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.refresh_token_expire_days,
        )

        await self._refresh_repo.create_token(
            user_id=user.id,
            token_hash=new_hash,
            family_id=family_id,
            expires_at=expires_at,
        )

        access_token = create_access_token(
            user_id=str(user.id),
            tenant_id=str(user.tenant_id),
            roles=user.roles,
        )
        expires_in = settings.access_token_expire_minutes * 60

        return {
            'access_token': access_token,
            'refresh_token': new_refresh,
            'token_type': 'bearer',
            'expires_in': expires_in,
        }

    async def logout(self, refresh_token_value: str) -> None:
        token_hash = _hash_token(refresh_token_value)
        stored = await self._refresh_repo.get_by_token_hash(token_hash)
        if stored and stored.revoked_at is None:
            await self._refresh_repo.revoke(stored)

    async def get_2fa_token(self, user: User) -> str:
        return create_2fa_token(
            user_id=str(user.id),
            tenant_id=str(user.tenant_id),
        )

    async def enroll_2fa(self, user: User) -> dict:
        import pyotp
        if user.totp_secret_cifrado is not None:
            raise ValueError('2FA ya está activo. Desactivelo primero para re-enrolar.')
        secret = pyotp.random_base32()
        uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user.email, issuer_name='activia-trace',
        )
        return {'secret': secret, 'uri': uri}

    async def verify_2fa_enroll(self, user: User, code: str, secret: str) -> None:
        import pyotp
        totp = pyotp.TOTP(secret)
        if not totp.verify(code):
            raise ValueError('Código TOTP inválido')
        user.totp_secret_cifrado = encrypt(secret)
        await self._session.flush()

    async def validate_2fa(self, fa2_token: str, code: str) -> dict:
        try:
            payload = decode_token(fa2_token)
        except Exception:
            raise ValueError('Token 2FA inválido o expirado')

        if payload.get('purpose') != '2fa':
            raise ValueError('Token 2FA inválido o expirado')

        user_id = uuid.UUID(payload['sub'])
        tenant_id = uuid.UUID(payload['tenant_id'])

        user_repo = UserRepository(self._session, tenant_id)
        user = await user_repo.get(user_id)
        if not user or not user.totp_secret_cifrado:
            raise ValueError('Código TOTP inválido')

        import pyotp
        secret = decrypt(user.totp_secret_cifrado)
        totp = pyotp.TOTP(secret)
        if not totp.verify(code):
            raise ValueError('Código TOTP inválido')

        return await self.create_session(user)

    async def forgot_password(self, email: str) -> dict:
        user = await self._user_repo.get_by_email(email)
        settings = Settings()

        if not user:
            detail = 'Si el email existe, recibirás un enlace de recuperación'
            if settings.debug:
                return {'detail': detail}
            return {'detail': detail}

        token_value = str(uuid.uuid4())
        token_hash = _hash_token(token_value)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

        await self._reset_repo.create_token(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        detail = 'Si el email existe, recibirás un enlace de recuperación'
        expires_in = 900

        if settings.debug:
            return {
                'detail': detail,
                'token': token_value,
                'expires_in': expires_in,
            }
        return {'detail': detail}

    async def reset_password(self, token_value: str, new_password: str) -> None:
        token_hash = _hash_token(token_value)
        stored = await self._reset_repo.get_by_token_hash(token_hash)
        if not stored:
            raise ValueError('Token inválido o expirado')
        if stored.used_at is not None:
            raise ValueError('Token inválido o expirado')
        if stored.expires_at < datetime.now(timezone.utc):
            raise ValueError('Token inválido o expirado')

        user_repo = UserRepository(self._session, self._tenant_id)
        user = await user_repo.get(stored.user_id)
        if not user:
            raise ValueError('Token inválido o expirado')

        await self._reset_repo.mark_used(stored)

        user.password_hash = hash_password(new_password)
        await self._session.flush()

        await self._refresh_repo.revoke_all_for_user(user.id)

    async def get_user_context(self, user_id: uuid.UUID) -> UserContext:
        user = await self._user_repo.get(user_id)
        if not user:
            raise ValueError('Usuario no encontrado')
        return UserContext(
            user_id=user.id,
            tenant_id=user.tenant_id,
            roles=user.roles,
        )

    @property
    def user_repo(self) -> UserRepository:
        return self._user_repo
