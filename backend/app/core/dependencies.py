import uuid
from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session_factory
from app.core.permissions import PermissionResolver
from app.core.security import decode_token
from app.models.tenant import Tenant
from app.schemas.auth import UserContext

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/auth/login')


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    session = get_session_factory()()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db),
) -> UserContext:
    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail='Token inválido o expirado')

    if 'tenant_id' not in payload or 'sub' not in payload:
        raise HTTPException(status_code=401, detail='Token inválido')

    if payload.get('purpose') == '2fa':
        raise HTTPException(status_code=401, detail='Token 2FA no otorga acceso a este endpoint')

    try:
        user_id = uuid.UUID(payload['sub'])
        tenant_id = uuid.UUID(payload['tenant_id'])
    except (ValueError, KeyError):
        raise HTTPException(status_code=401, detail='Token inválido')

    result = await session.execute(
        select(Tenant).where(Tenant.id == tenant_id),
    )
    tenant = result.scalar_one_or_none()
    if not tenant or tenant.estado != 'Activo':
        raise HTTPException(status_code=401, detail='Tenant inactivo o no encontrado')

    from app.models.user import User
    from sqlalchemy import select as sa_select

    user_result = await session.execute(
        sa_select(User).where(User.id == user_id).where(User.deleted_at.is_(None)),
    )
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail='Usuario no encontrado')

    impersonator_id_raw = payload.get('impersonator_id')
    impersonator_id: uuid.UUID | None = None
    if impersonator_id_raw is not None:
        try:
            impersonator_id = uuid.UUID(impersonator_id_raw)
        except (ValueError, KeyError):
            impersonator_id = None

    return UserContext(
        user_id=user_id,
        tenant_id=tenant_id,
        roles=payload.get('roles', []),
        impersonator_id=impersonator_id,
    )


def require_permission(permiso: str):
    async def _check(
        current_user: UserContext = Depends(get_current_user),
        session: AsyncSession = Depends(get_db),
    ) -> None:
        resolver = PermissionResolver(session, current_user.tenant_id)
        effective = await resolver.get_effective_permissions(current_user.user_id)
        if permiso not in effective:
            raise HTTPException(
                status_code=403,
                detail=f'Permiso insuficiente: {permiso}',
            )
    return Depends(_check)
