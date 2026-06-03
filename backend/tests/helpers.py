import uuid
from datetime import datetime

from httpx import AsyncClient
from sqlalchemy import String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.core.security import create_access_token, hash_password
from app.models.mixins import BaseModelMixin


class TestModel(Base, BaseModelMixin):
    __tablename__ = 'test_models'

    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    codigo: Mapped[str] = mapped_column(String(50), nullable=False)

from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.tenant import Tenant
from app.models.user import User
from app.models.user_role import UserRole


async def _create_tenant(
    session: AsyncSession,
    nombre: str = 'Test',
    codigo: str = 'TEST',
    aprobacion_comunicaciones: bool = False,
) -> Tenant:
    tid = uuid.uuid4()
    tenant = Tenant(
        id=tid,
        nombre=nombre,
        codigo=codigo,
        estado='Activo',
        aprobacion_comunicaciones=aprobacion_comunicaciones,
    )
    session.add(tenant)
    await session.flush()
    return tenant


async def _create_user(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    email: str | None = None,
    roles: list[str] | None = None,
) -> User:
    uid = uuid.uuid4()
    user = User(
        id=uid,
        tenant_id=tenant_id,
        email=email or f'{uid.hex[:8]}@test.com',
        password_hash=hash_password('password123'),
        roles=roles or [],
    )
    session.add(user)
    await session.flush()

    if roles:
        for role_codigo in roles:
            result = await session.execute(
                __import__('sqlalchemy').select(Role).where(
                    Role.tenant_id == tenant_id,
                    Role.codigo == role_codigo,
                )
            )
            role = result.scalar_one_or_none()
            if not role:
                role = Role(
                    tenant_id=tenant_id,
                    name=role_codigo,
                    codigo=role_codigo,
                )
                session.add(role)
                await session.flush()
            session.add(UserRole(
                tenant_id=tenant_id,
                user_id=user.id,
                role_id=role.id,
            ))
            await session.flush()

    return user


async def _login_as(
    client: AsyncClient,
    email: str,
) -> str:
    tenant_id = None
    from app.models.user import User as _UserModel
    from sqlalchemy import select
    async with __import__('app.core.database', fromlist=['get_session_factory']).get_session_factory()() as s:
        result = await s.execute(select(_UserModel).where(_UserModel.email == email))
        user = result.scalar_one_or_none()
        if user:
            tenant_id = user.tenant_id
    if not tenant_id:
        raise ValueError(f'User {email} not found')
    from app.models.user_role import UserRole as _UR
    async with __import__('app.core.database', fromlist=['get_session_factory']).get_session_factory()() as s:
        result = await s.execute(
            select(_UR).where(_UR.user_id == user.id, _UR.tenant_id == tenant_id)
        )
        ur = result.scalars().all()
        from app.models.role import Role as _Role
        role_ids = [r.role_id for r in ur]
        roles_result = await s.execute(select(_Role).where(_Role.id.in_(role_ids)))
        roles = [r.codigo for r in roles_result.scalars().all()]
    return create_access_token(str(user.id), str(tenant_id), roles)


async def _seed_permission_for_role(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    role_codigo: str,
    permiso_codigo: str,
) -> None:
    from sqlalchemy import select

    result = await session.execute(
        select(Role).where(Role.tenant_id == tenant_id, Role.codigo == role_codigo)
    )
    role = result.scalar_one_or_none()
    if not role:
        role = Role(tenant_id=tenant_id, name=role_codigo, codigo=role_codigo)
        session.add(role)
        await session.flush()

    result = await session.execute(
        select(Permission).where(Permission.tenant_id == tenant_id, Permission.codigo == permiso_codigo)
    )
    permiso = result.scalar_one_or_none()
    if not permiso:
        permiso = Permission(
            tenant_id=tenant_id,
            codigo=permiso_codigo,
            modulo=permiso_codigo.split(':')[0],
            accion=permiso_codigo.split(':')[1] if ':' in permiso_codigo else permiso_codigo,
        )
        session.add(permiso)
        await session.flush()

    session.add(RolePermission(
        tenant_id=tenant_id,
        role_id=role.id,
        permiso_id=permiso.id,
    ))
    await session.flush()
