import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.core.dependencies import get_db
from app.core.security import create_access_token
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.user import User
from app.models.user_role import UserRole
from app.models.tenant import Tenant


@pytest_asyncio.fixture
async def auth_rbac_setup(db_session):
    tid = uuid.uuid4()
    tenant = Tenant(id=tid, nombre='Test', codigo='TST', estado='Activo')
    db_session.add(tenant)
    await db_session.flush()

    user = User(tenant_id=tid, email='admin@t.com', password_hash='hash', roles=['ADMIN'])
    user_no_perm = User(tenant_id=tid, email='noperm@t.com', password_hash='hash', roles=[])
    db_session.add_all([user, user_no_perm])
    await db_session.flush()

    role_admin = Role(tenant_id=tid, name='ADMIN', codigo='ADMIN')
    role_alumno = Role(tenant_id=tid, name='ALUMNO', codigo='ALUMNO')
    db_session.add_all([role_admin, role_alumno])
    await db_session.flush()

    p_rbac = Permission(
        tenant_id=tid, codigo='rbac:gestionar',
        modulo='rbac', accion='gestionar',
    )
    db_session.add(p_rbac)
    await db_session.flush()

    db_session.add_all([
        RolePermission(tenant_id=tid, role_id=role_admin.id, permiso_id=p_rbac.id),
        UserRole(tenant_id=tid, user_id=user.id, role_id=role_admin.id),
    ])
    await db_session.flush()

    token = create_access_token(str(user.id), str(tid), ['ADMIN'])
    token_no_perm = create_access_token(str(user_no_perm.id), str(tid), [])
    return {
        'tid': tid,
        'user': user,
        'token': token,
        'token_no_perm': token_no_perm,
        'user_no_perm': user_no_perm,
    }


class TestRequirePermission:
    @pytest.mark.asyncio
    async def test_user_with_permission_passes(self, app, db_session, auth_rbac_setup):
        app.dependency_overrides[get_db] = lambda: db_session
        async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
            response = await client.get(
                '/api/v1/roles',
                headers={'Authorization': f'Bearer {auth_rbac_setup["token"]}'},
            )
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_user_without_permission_gets_403(self, app, db_session, auth_rbac_setup):
        app.dependency_overrides[get_db] = lambda: db_session
        async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
            response = await client.get(
                '/api/v1/roles',
                headers={'Authorization': f'Bearer {auth_rbac_setup["token_no_perm"]}'},
            )
            assert response.status_code == 403
            assert 'Permiso insuficiente' in response.text

    @pytest.mark.asyncio
    async def test_fail_closed_nonexistent_permission(self, app, db_session, auth_rbac_setup):
        from app.core.dependencies import require_permission
        from fastapi import FastAPI

        test_app = FastAPI()
        test_app.dependency_overrides[get_db] = lambda: db_session

        @test_app.get('/test-ne')
        @pytest.mark.asyncio
        async def test_endpoint(_=require_permission('modulo:inexistente')):
            return {'ok': True}

        async with AsyncClient(transport=ASGITransport(app=test_app), base_url='http://test') as client:
            response = await client.get(
                '/test-ne',
                headers={'Authorization': f'Bearer {auth_rbac_setup["token"]}'},
            )
            assert response.status_code == 403
