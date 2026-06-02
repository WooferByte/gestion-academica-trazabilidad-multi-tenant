import uuid

import pytest
import pytest_asyncio

from app.models.role import Role
from app.repositories.role import RoleRepository
from app.repositories.permission import PermissionRepository
from app.repositories.role_permission import RolePermissionRepository
from app.repositories.user_role import UserRoleRepository
from app.models.permission import Permission
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


class TestRoleRepository:
    async def test_create_and_get(self, db_session, tenant):
        repo = RoleRepository(db_session, tenant.id)
        role = await repo.create(name='Admin', codigo='ADMIN')
        assert role.id is not None
        assert role.codigo == 'ADMIN'

        fetched = await repo.get(role.id)
        assert fetched is not None
        assert fetched.name == 'Admin'

    async def test_get_by_codigo(self, db_session, tenant):
        repo = RoleRepository(db_session, tenant.id)
        await repo.create(name='Prof', codigo='PROFESOR')
        fetched = await repo.get_by_codigo('PROFESOR')
        assert fetched is not None
        assert fetched.name == 'Prof'

    async def test_tenant_scope(self, db_session, tenant):
        t_b = Tenant(nombre='Other', codigo='OTH', estado='Activo')
        db_session.add(t_b)
        await db_session.flush()
        repo1 = RoleRepository(db_session, tenant.id)
        repo2 = RoleRepository(db_session, t_b.id)
        await repo1.create(name='Admin', codigo='ADMIN')
        roles_other = await repo2.get_multi()
        assert len(roles_other) == 0

    async def test_soft_delete(self, db_session, tenant):
        repo = RoleRepository(db_session, tenant.id)
        role = await repo.create(name='Temp', codigo='TEMP')
        await repo.soft_delete(role)
        assert role.deleted_at is not None
        fetched = await repo.get(role.id)
        assert fetched is None

    async def test_unique_codigo_violation(self, db_session, tenant):
        repo = RoleRepository(db_session, tenant.id)
        await repo.create(name='A', codigo='DUPE')
        with pytest.raises(Exception):
            await repo.create(name='B', codigo='DUPE')


class TestPermissionRepository:
    async def test_create_and_get_by_codigo(self, db_session, tenant):
        repo = PermissionRepository(db_session, tenant.id)
        perm = await repo.create(
            codigo='mod:acc', modulo='mod', accion='acc', descripcion='Test',
        )
        fetched = await repo.get_by_codigo('mod:acc')
        assert fetched is not None
        assert fetched.modulo == 'mod'

    async def test_get_multi_by_codigos(self, db_session, tenant):
        repo = PermissionRepository(db_session, tenant.id)
        p1 = await repo.create(codigo='a:x', modulo='a', accion='x')
        p2 = await repo.create(codigo='b:y', modulo='b', accion='y')
        codigos = ['a:x', 'b:y']
        result = await repo.get_multi_by_codigos(codigos)
        assert len(result) == 2


class TestRolePermissionRepository:
    async def test_assign_and_list(self, db_session, tenant):
        role_repo = RoleRepository(db_session, tenant.id)
        perm_repo = PermissionRepository(db_session, tenant.id)
        rp_repo = RolePermissionRepository(db_session, tenant.id)

        role = await role_repo.create(name='R', codigo='R')
        perm = await perm_repo.create(codigo='m:a', modulo='m', accion='a')

        rp = await rp_repo.create(role_id=role.id, permiso_id=perm.id, propio=False)
        assert rp.id is not None

        lista = await rp_repo.list_by_role(role.id)
        assert len(lista) == 1
        assert lista[0].permiso_id == perm.id

    async def test_delete_by_role_and_permiso(self, db_session, tenant):
        role_repo = RoleRepository(db_session, tenant.id)
        perm_repo = PermissionRepository(db_session, tenant.id)
        rp_repo = RolePermissionRepository(db_session, tenant.id)

        role = await role_repo.create(name='R', codigo='R')
        perm = await perm_repo.create(codigo='m:a', modulo='m', accion='a')
        await rp_repo.create(role_id=role.id, permiso_id=perm.id, propio=False)

        deleted = await rp_repo.delete_by_role_and_permiso(role.id, perm.id)
        assert deleted is not None

        lista = await rp_repo.list_by_role(role.id)
        assert len(lista) == 0


class TestUserRoleRepository:
    async def test_assign_and_list(self, db_session, tenant):
        from app.repositories.user_repository import UserRepository

        user_repo = UserRepository(db_session, tenant.id)
        role_repo = RoleRepository(db_session, tenant.id)
        ur_repo = UserRoleRepository(db_session, tenant.id)

        user = await user_repo.create(
            email='u@t.com', password_hash='hash', roles=[],
        )
        role = await role_repo.create(name='R', codigo='R')
        ur = await ur_repo.create(user_id=user.id, role_id=role.id)
        assert ur.id is not None

        lista = await ur_repo.list_by_user(user.id)
        assert len(lista) == 1

    async def test_delete_by_user_and_role(self, db_session, tenant):
        from app.repositories.user_repository import UserRepository

        user_repo = UserRepository(db_session, tenant.id)
        role_repo = RoleRepository(db_session, tenant.id)
        ur_repo = UserRoleRepository(db_session, tenant.id)

        user = await user_repo.create(email='u@t.com', password_hash='hash', roles=[])
        role = await role_repo.create(name='R', codigo='R')
        await ur_repo.create(user_id=user.id, role_id=role.id)

        deleted = await ur_repo.delete_by_user_and_role(user.id, role.id)
        assert deleted is not None
        lista = await ur_repo.list_by_user(user.id)
        assert len(lista) == 0
