import hashlib
import logging
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.dependencies import get_current_user, get_db
from app.core.rate_limiter import LoginRateLimiter
from app.core.security import create_access_token, decode_token
from app.models.tenant import Tenant
from app.models.user import PasswordResetToken, RefreshToken
from app.repositories.password_reset_repository import PasswordResetTokenRepository
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.schemas.auth import (
    ForgotRequest,
    ForgotResponse,
    Login2FARequired,
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    RefreshRequest,
    RefreshResponse,
    ResetRequest,
    ResetResponse,
    TOTPEnrollResponse,
    TOTPValidateRequest,
    TOTPVerifyRequest,
    UserContext,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix='/api/v1/auth')
logger = logging.getLogger(__name__)

rate_limiter = LoginRateLimiter()


def reset_rate_limiter() -> None:
    rate_limiter._attempts.clear()


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode('utf-8')).hexdigest()


async def _authenticate_across_tenants(
    db: AsyncSession, email: str, password: str,
) -> tuple[object, uuid.UUID] | None:
    result = await db.execute(select(Tenant))
    tenants = result.scalars().all()
    for tenant in tenants:
        svc = AuthService(db, tenant.id)
        user = await svc.authenticate(email, password)
        if user:
            return user, tenant.id
    return None


async def _find_tenant_for_user(db: AsyncSession, email: str) -> uuid.UUID | None:
    result = await db.execute(select(Tenant))
    tenants = result.scalars().all()
    for tenant in tenants:
        svc = AuthService(db, tenant.id)
        user = await svc.user_repo.get_by_email(email)
        if user:
            return tenant.id
    return None


@router.post('/login')
async def login(
    body: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> LoginResponse | dict:
    ip = request.client.host if request.client else 'unknown'
    if not rate_limiter.check(ip, body.email):
        raise HTTPException(
            status_code=429,
            detail='Demasiados intentos. Intente nuevamente en 1 minuto.',
        )
    rate_limiter.record(ip, body.email)

    auth_result = await _authenticate_across_tenants(db, body.email, body.password)
    if not auth_result:
        raise HTTPException(status_code=401, detail='Credenciales inválidas')

    user, tenant_id = auth_result
    svc = AuthService(db, tenant_id)

    if user.totp_secret_cifrado is not None:
        fa2_token = await svc.get_2fa_token(user)
        return {'2fa_required': True, '2fa_token': fa2_token}

    session = await svc.create_session(user)
    return LoginResponse(**session)


@router.post('/refresh')
async def refresh(
    body: RefreshRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> RefreshResponse:
    token_hash = _hash_token(body.refresh_token)
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash),
    )
    stored = result.scalar_one_or_none()

    if not stored:
        raise HTTPException(status_code=401, detail='Token inválido o revocado')

    if stored.revoked_at is not None:
        repo = RefreshTokenRepository(db, stored.tenant_id)
        await repo.revoke_family(stored.family_id)
        raise HTTPException(status_code=401, detail='Token inválido o revocado')

    settings = Settings()
    if stored.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail='Token inválido o revocado')

    repo = RefreshTokenRepository(db, stored.tenant_id)
    svc = AuthService(db, stored.tenant_id)
    await repo.revoke(stored)

    new_refresh = str(uuid.uuid4())
    new_hash = _hash_token(new_refresh)
    family_id = stored.family_id
    expires_at = datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_expire_days,
    )

    user = await svc.user_repo.get(stored.user_id)
    if not user:
        raise HTTPException(status_code=401, detail='Token inválido o revocado')

    await repo.create_token(
        user_id=user.id,
        token_hash=new_hash,
        family_id=family_id,
        expires_at=expires_at,
    )

    auth_header = request.headers.get('authorization', '')
    impersonator_id: str | None = None
    if auth_header.startswith('Bearer '):
        try:
            payload = decode_token(auth_header[7:])
            impersonator_id = payload.get('impersonator_id')
        except Exception:
            pass

    access_token = create_access_token(
        user_id=str(user.id),
        tenant_id=str(user.tenant_id),
        roles=user.roles,
        impersonator_id=impersonator_id,
    )
    expires_in = settings.access_token_expire_minutes * 60

    return RefreshResponse(
        access_token=access_token,
        refresh_token=new_refresh,
        token_type='bearer',
        expires_in=expires_in,
    )


@router.post('/logout')
async def logout(
    body: LogoutRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
) -> dict:
    svc = AuthService(db, current_user.tenant_id)
    await svc.logout(body.refresh_token)
    return {'detail': 'Sesión cerrada exitosamente'}


@router.post('/2fa/enroll', response_model=TOTPEnrollResponse)
async def enroll_2fa(
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
) -> TOTPEnrollResponse:
    svc = AuthService(db, current_user.tenant_id)
    user = await svc.user_repo.get(current_user.user_id)
    if not user:
        raise HTTPException(status_code=401, detail='Usuario no encontrado')
    try:
        result = await svc.enroll_2fa(user)
        return TOTPEnrollResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post('/2fa/verify')
async def verify_2fa(
    body: TOTPVerifyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
) -> dict:
    svc = AuthService(db, current_user.tenant_id)
    user = await svc.user_repo.get(current_user.user_id)
    if not user:
        raise HTTPException(status_code=401, detail='Usuario no encontrado')
    try:
        await svc.verify_2fa_enroll(user, body.code, body.secret)
        return {'detail': '2FA activado exitosamente'}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post('/2fa/validate')
async def validate_2fa(
    body: TOTPValidateRequest,
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    try:
        payload = decode_token(body.fa2_token)
        tenant_id = uuid.UUID(payload['tenant_id'])
        svc = AuthService(db, tenant_id)
        session = await svc.validate_2fa(body.fa2_token, body.code)
        return LoginResponse(**session)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception:
        raise HTTPException(status_code=401, detail='Token 2FA inválido o expirado')


@router.post('/forgot')
async def forgot(
    body: ForgotRequest,
    db: AsyncSession = Depends(get_db),
) -> ForgotResponse:
    settings = Settings()
    tenant_id = await _find_tenant_for_user(db, body.email)

    if not tenant_id:
        detail = 'Si el email existe, recibirás un enlace de recuperación'
        if settings.debug:
            return ForgotResponse(detail=detail)
        return ForgotResponse(detail=detail)

    svc = AuthService(db, tenant_id)
    result_data = await svc.forgot_password(body.email)
    return ForgotResponse(**result_data)


@router.post('/reset')
async def reset(
    body: ResetRequest,
    db: AsyncSession = Depends(get_db),
) -> ResetResponse:
    token_hash = _hash_token(body.token)
    result = await db.execute(
        select(PasswordResetToken).where(
            PasswordResetToken.token_hash == token_hash,
        ),
    )
    stored = result.scalar_one_or_none()
    if not stored:
        raise HTTPException(status_code=401, detail='Token inválido o expirado')

    svc = AuthService(db, stored.tenant_id)
    try:
        await svc.reset_password(body.token, body.new_password)
        return ResetResponse(detail='Contraseña actualizada exitosamente')
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
