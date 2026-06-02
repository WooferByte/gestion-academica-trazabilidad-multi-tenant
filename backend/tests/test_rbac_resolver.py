import uuid

import pytest
import pytest_asyncio
from datetime import datetime, timezone

from app.core.permissions import PermissionResolver
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.user import User
from app.models.user_role import UserRole
from app.models.tenant import Tenant


@pytest_asyncio.fixture
async def rbac_setup(db_session):
    tid = uuid.uuid4()
    tenant = Tenant(id=tid, nombre='Test', codigo='TST', estado='Activo')
    db_session.add(tenant)
    await db_session.flush()

    user = User(tenant_id=tid, email='u@t.com', password_hash='hash', roles=[])
    db_session.add_all([user])

    role_alumno = Role(tenant_id=tid, name='ALUMNO', codigo='ALUMNO')
    role_profesor = Role(tenant_id=tid, name='PROFESOR', codigo='PROFESOR')
    role_admin = Role(tenant_id=tid, name='ADMIN', codigo='ADMIN')
    db_session.add_all([role_alumno, role_profesor, role_admin])

    await db_session.flush()

    p_ver_estado = Permission(
        tenant_id=tid, codigo='ver_estado_academico_propio',
        modulo='calificaciones', accion='ver_propio',
    )
    p_reservar = Permission(
        tenant_id=tid, codigo='reservar_evaluacion',
        modulo='evaluaciones', accion='reservar',
    )
    p_importar = Permission(
        tenant_id=tid, codigo='calificaciones:importar',
        modulo='calificaciones', accion='importar',
    )
    p_admin = Permission(
        tenant_id=tid, codigo='admin:full',
        modulo='admin', accion='full',
    )
    db_session.add_all([p_ver_estado, p_reservar, p_importar, p_admin])
    await db_session.flush()

    db_session.add_all([
        RolePermission(tenant_id=tid, role_id=role_alumno.id, permiso_id=p_ver_estado.id),
        RolePermission(tenant_id=tid, role_id=role_alumno.id, permiso_id=p_reservar.id),
        RolePermission(tenant_id=tid, role_id=role_profesor.id, permiso_id=p_importar.id),
        RolePermission(tenant_id=tid, role_id=role_admin.id, permiso_id=p_admin.id),
    ])
    await db_session.flush()

    return {
        'tid': tid,
        'user': user,
        'roles': {
            'alumno': role_alumno,
            'profesor': role_profesor,
            'admin': role_admin,
        },
        'permisos': {
            'ver_estado': p_ver_estado,
            'reservar': p_reservar,
            'importar': p_importar,
            'admin': p_admin,
        },
    }


class TestPermissionResolver:
    async def test_single_role_permissions(self, db_session, rbac_setup):
        tid = rbac_setup['tid']
        user = rbac_setup['user']
        db_session.add(UserRole(
            tenant_id=tid, user_id=user.id, role_id=rbac_setup['roles']['alumno'].id,
        ))
        await db_session.flush()

        resolver = PermissionResolver(db_session, tid)
        perms = await resolver.get_effective_permissions(user.id)
        assert 'ver_estado_academico_propio' in perms
        assert 'reservar_evaluacion' in perms
        assert 'calificaciones:importar' not in perms

    async def test_union_of_multiple_roles(self, db_session, rbac_setup):
        tid = rbac_setup['tid']
        user = rbac_setup['user']
        db_session.add_all([
            UserRole(tenant_id=tid, user_id=user.id, role_id=rbac_setup['roles']['alumno'].id),
            UserRole(tenant_id=tid, user_id=user.id, role_id=rbac_setup['roles']['profesor'].id),
        ])
        await db_session.flush()

        resolver = PermissionResolver(db_session, tid)
        perms = await resolver.get_effective_permissions(user.id)
        assert 'ver_estado_academico_propio' in perms
        assert 'reservar_evaluacion' in perms
        assert 'calificaciones:importar' in perms

    async def test_excludes_soft_deleted_assignments(self, db_session, rbac_setup):
        tid = rbac_setup['tid']
        user = rbac_setup['user']
        ur = UserRole(
            tenant_id=tid, user_id=user.id, role_id=rbac_setup['roles']['alumno'].id,
        )
        db_session.add(ur)
        await db_session.flush()

        ur.deleted_at = datetime.now(timezone.utc)
        await db_session.flush()

        resolver = PermissionResolver(db_session, tid)
        perms = await resolver.get_effective_permissions(user.id)
        assert len(perms) == 0

    async def test_tenant_scoped_resolution(self, db_session, rbac_setup):
        tid = rbac_setup['tid']
        user = rbac_setup['user']
        db_session.add(UserRole(
            tenant_id=tid, user_id=user.id, role_id=rbac_setup['roles']['alumno'].id,
        ))
        await db_session.flush()

        other_tid = uuid.uuid4()
        resolver_other = PermissionResolver(db_session, other_tid)
        perms = await resolver_other.get_effective_permissions(user.id)
        assert len(perms) == 0

    async def test_user_with_no_roles_returns_empty(self, db_session, rbac_setup):
        resolver = PermissionResolver(db_session, rbac_setup['tid'])
        perms = await resolver.get_effective_permissions(rbac_setup['user'].id)
        assert len(perms) == 0
