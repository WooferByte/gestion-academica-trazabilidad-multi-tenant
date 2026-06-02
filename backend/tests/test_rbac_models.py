import uuid
from datetime import datetime, timezone

import pytest
import pytest_asyncio
from sqlalchemy import select

from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.user_role import UserRole
from app.models.user import User
from app.models.tenant import Tenant


@pytest_asyncio.fixture
async def tenant(db_session):
    t = Tenant(nombre='Test', codigo='TST', estado='Activo')
    db_session.add(t)
    await db_session.flush()
    return t


class TestRoleModel:
    async def test_create_role(self, db_session, tenant):
        role = Role(tenant_id=tenant.id, name='Supervisor', codigo='SUPERVISOR')
        db_session.add(role)
        await db_session.flush()

        assert role.id is not None
        assert role.name == 'Supervisor'
        assert role.codigo == 'SUPERVISOR'
        assert role.deleted_at is None

    async def test_soft_delete_role(self, db_session, tenant):
        role = Role(tenant_id=tenant.id, name='Test', codigo='TEST')
        db_session.add(role)
        await db_session.flush()

        role_id = role.id
        role.deleted_at = datetime.now(timezone.utc)
        await db_session.flush()

        result = await db_session.execute(
            select(Role).where(Role.id == role_id).where(Role.deleted_at.is_(None)),
        )
        assert result.scalar_one_or_none() is None

    async def test_tenant_isolation_role(self, db_session, tenant):
        tid_b = uuid.uuid4()
        t_b = Tenant(id=tid_b, nombre='Other', codigo='OTH', estado='Activo')
        db_session.add(t_b)
        await db_session.flush()

        db_session.add_all([
            Role(tenant_id=tenant.id, name='Prof A', codigo='PROFESOR'),
            Role(tenant_id=tid_b, name='Prof B', codigo='PROFESOR'),
        ])
        await db_session.flush()

        result_a = await db_session.execute(
            select(Role).where(Role.tenant_id == tenant.id).where(Role.deleted_at.is_(None)),
        )
        roles_a = list(result_a.scalars().all())
        assert len(roles_a) == 1
        assert roles_a[0].codigo == 'PROFESOR'

    async def test_unique_codigo_per_tenant(self, db_session, tenant):
        db_session.add(Role(tenant_id=tenant.id, name='Admin', codigo='ADMIN'))
        await db_session.flush()

        with pytest.raises(Exception):
            db_session.add(Role(tenant_id=tenant.id, name='Admin Dup', codigo='ADMIN'))
            await db_session.flush()


class TestPermissionModel:
    async def test_create_permission(self, db_session, tenant):
        perm = Permission(
            tenant_id=tenant.id,
            codigo='calificaciones:importar',
            descripcion='Importar calificaciones',
            modulo='calificaciones',
            accion='importar',
        )
        db_session.add(perm)
        await db_session.flush()

        assert perm.id is not None
        assert perm.codigo == 'calificaciones:importar'
        assert perm.modulo == 'calificaciones'
        assert perm.accion == 'importar'

    async def test_unique_codigo_per_tenant(self, db_session, tenant):
        db_session.add(Permission(
            tenant_id=tenant.id, codigo='mod:acc', modulo='mod', accion='acc',
        ))
        await db_session.flush()

        with pytest.raises(Exception):
            db_session.add(Permission(
                tenant_id=tenant.id, codigo='mod:acc', modulo='mod', accion='acc',
            ))
            await db_session.flush()


class TestRolePermissionModel:
    async def test_create_role_permission(self, db_session, tenant):
        role = Role(tenant_id=tenant.id, name='Prof', codigo='PROFESOR')
        perm = Permission(tenant_id=tenant.id, codigo='mod:acc', modulo='mod', accion='acc')
        db_session.add_all([role, perm])
        await db_session.flush()

        rp = RolePermission(tenant_id=tenant.id, role_id=role.id, permiso_id=perm.id, propio=True)
        db_session.add(rp)
        await db_session.flush()

        assert rp.role_id == role.id
        assert rp.permiso_id == perm.id
        assert rp.propio is True


class TestUserRoleModel:
    async def test_create_user_role(self, db_session, tenant):
        user = User(tenant_id=tenant.id, email='test@test.com', password_hash='hash', roles=[])
        role = Role(tenant_id=tenant.id, name='Prof', codigo='PROFESOR')
        db_session.add_all([user, role])
        await db_session.flush()

        ur = UserRole(tenant_id=tenant.id, user_id=user.id, role_id=role.id)
        db_session.add(ur)
        await db_session.flush()

        assert ur.user_id == user.id
        assert ur.role_id == role.id
