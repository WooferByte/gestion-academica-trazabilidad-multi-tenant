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
async def admin_token(db_session):
    tid = uuid.uuid4()
    tenant = Tenant(id=tid, nombre='Test', codigo='TST', estado='Activo')
    db_session.add(tenant)
    await db_session.flush()

    user = User(tenant_id=tid, email='admin@t.com', password_hash='hash', roles=['ADMIN'])
    role_admin = Role(tenant_id=tid, name='ADMIN', codigo='ADMIN')
    db_session.add_all([user, role_admin])
    await db_session.flush()

    p_rbac = Permission(
        tenant_id=tid, codigo='rbac:gestionar', modulo='rbac', accion='gestionar',
    )
    db_session.add(p_rbac)
    await db_session.flush()

    db_session.add_all([
        RolePermission(tenant_id=tid, role_id=role_admin.id, permiso_id=p_rbac.id),
        UserRole(tenant_id=tid, user_id=user.id, role_id=role_admin.id),
    ])
    await db_session.flush()

    token = create_access_token(str(user.id), str(tid), ['ADMIN'])
    return {'token': token, 'tid': tid, 'tenant': tenant, 'user': user}


class TestRolesAPI:
    @pytest.mark.asyncio
    async def test_list_roles(self, app, db_session, admin_token):
        app.dependency_overrides[get_db] = lambda: db_session
        async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
            response = await client.get(
                '/api/v1/roles',
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            assert response.status_code == 200
            data = response.json()
            assert 'items' in data

    @pytest.mark.asyncio
    async def test_create_role(self, app, db_session, admin_token):
        app.dependency_overrides[get_db] = lambda: db_session
        async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
            response = await client.post(
                '/api/v1/roles',
                json={'name': 'Supervisor', 'codigo': 'SUPERVISOR'},
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            assert response.status_code == 201
            data = response.json()
            assert data['name'] == 'Supervisor'
            assert data['codigo'] == 'SUPERVISOR'

    @pytest.mark.asyncio
    async def test_create_role_duplicate(self, app, db_session, admin_token):
        app.dependency_overrides[get_db] = lambda: db_session
        async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
            await client.post(
                '/api/v1/roles',
                json={'name': 'Dupe', 'codigo': 'DUPE'},
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            response = await client.post(
                '/api/v1/roles',
                json={'name': 'Dupe2', 'codigo': 'DUPE'},
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_update_role(self, app, db_session, admin_token):
        app.dependency_overrides[get_db] = lambda: db_session
        async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
            created = await client.post(
                '/api/v1/roles',
                json={'name': 'Old', 'codigo': 'OLD'},
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            role_id = created.json()['id']
            response = await client.put(
                f'/api/v1/roles/{role_id}',
                json={'name': 'New'},
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            assert response.status_code == 200
            assert response.json()['name'] == 'New'

    @pytest.mark.asyncio
    async def test_delete_role(self, app, db_session, admin_token):
        app.dependency_overrides[get_db] = lambda: db_session
        async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
            created = await client.post(
                '/api/v1/roles',
                json={'name': 'Temp', 'codigo': 'TEMP'},
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            role_id = created.json()['id']
            response = await client.delete(
                f'/api/v1/roles/{role_id}',
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            assert response.status_code == 204

            get_resp = await client.get(
                f'/api/v1/roles/{role_id}',
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            assert get_resp.status_code == 404


class TestPermisosAPI:
    @pytest.mark.asyncio
    async def test_create_permission(self, app, db_session, admin_token):
        app.dependency_overrides[get_db] = lambda: db_session
        async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
            response = await client.post(
                '/api/v1/permisos',
                json={
                    'codigo': 'nuevo_modulo:accion',
                    'descripcion': 'Test permission',
                    'modulo': 'nuevo_modulo',
                    'accion': 'accion',
                },
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            assert response.status_code == 201
            data = response.json()
            assert data['codigo'] == 'nuevo_modulo:accion'
            assert data['modulo'] == 'nuevo_modulo'

    @pytest.mark.asyncio
    async def test_duplicate_permission_code(self, app, db_session, admin_token):
        app.dependency_overrides[get_db] = lambda: db_session
        async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
            await client.post(
                '/api/v1/permisos',
                json={
                    'codigo': 'mod:dup', 'descripcion': 'A',
                    'modulo': 'mod', 'accion': 'dup',
                },
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            response = await client.post(
                '/api/v1/permisos',
                json={
                    'codigo': 'mod:dup', 'descripcion': 'B',
                    'modulo': 'mod', 'accion': 'dup',
                },
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_list_permisos(self, app, db_session, admin_token):
        app.dependency_overrides[get_db] = lambda: db_session
        async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
            response = await client.get(
                '/api/v1/permisos',
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_update_permiso(self, app, db_session, admin_token):
        app.dependency_overrides[get_db] = lambda: db_session
        async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
            created = await client.post(
                '/api/v1/permisos',
                json={
                    'codigo': 'mod:upd', 'descripcion': 'Old',
                    'modulo': 'mod', 'accion': 'upd',
                },
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            perm_id = created.json()['id']
            response = await client.put(
                f'/api/v1/permisos/{perm_id}',
                json={'descripcion': 'Updated'},
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_delete_permiso(self, app, db_session, admin_token):
        app.dependency_overrides[get_db] = lambda: db_session
        async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
            created = await client.post(
                '/api/v1/permisos',
                json={
                    'codigo': 'mod:del', 'descripcion': 'Del',
                    'modulo': 'mod', 'accion': 'del',
                },
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            perm_id = created.json()['id']
            response = await client.delete(
                f'/api/v1/permisos/{perm_id}',
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            assert response.status_code == 204


class TestRolePermisosAPI:
    @pytest.mark.asyncio
    async def test_assign_and_list(self, app, db_session, admin_token):
        app.dependency_overrides[get_db] = lambda: db_session
        async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
            role = await client.post(
                '/api/v1/roles',
                json={'name': 'Test', 'codigo': 'TEST'},
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            role_id = role.json()['id']

            perm = await client.post(
                '/api/v1/permisos',
                json={
                    'codigo': 'mod:test', 'descripcion': 'T',
                    'modulo': 'mod', 'accion': 'test',
                },
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            perm_id = perm.json()['id']

            assign = await client.post(
                f'/api/v1/roles/{role_id}/permisos',
                json={'permiso_id': perm_id, 'propio': True},
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            assert assign.status_code == 201

            lista = await client.get(
                f'/api/v1/roles/{role_id}/permisos',
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            assert lista.status_code == 200
            assert len(lista.json()) >= 1

    @pytest.mark.asyncio
    async def test_unassign(self, app, db_session, admin_token):
        app.dependency_overrides[get_db] = lambda: db_session
        async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
            role = await client.post(
                '/api/v1/roles',
                json={'name': 'R', 'codigo': 'R'},
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            role_id = role.json()['id']
            perm = await client.post(
                '/api/v1/permisos',
                json={'codigo': 'm:u', 'descripcion': 'U', 'modulo': 'm', 'accion': 'u'},
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            perm_id = perm.json()['id']

            await client.post(
                f'/api/v1/roles/{role_id}/permisos',
                json={'permiso_id': perm_id, 'propio': False},
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            delete_resp = await client.delete(
                f'/api/v1/roles/{role_id}/permisos/{perm_id}',
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            assert delete_resp.status_code == 204


class TestUserRolesAPI:
    @pytest.mark.asyncio
    async def test_assign_and_list(self, app, db_session, admin_token):
        app.dependency_overrides[get_db] = lambda: db_session
        async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
            role = await client.post(
                '/api/v1/roles',
                json={'name': 'Prof', 'codigo': 'PROF'},
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            role_id = role.json()['id']
            user_id = str(admin_token['user'].id)

            assign = await client.post(
                f'/api/v1/users/{user_id}/roles',
                json={'role_id': role_id},
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            assert assign.status_code == 201

            lista = await client.get(
                f'/api/v1/users/{user_id}/roles',
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            assert lista.status_code == 200

    @pytest.mark.asyncio
    async def test_unassign(self, app, db_session, admin_token):
        app.dependency_overrides[get_db] = lambda: db_session
        async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
            role = await client.post(
                '/api/v1/roles',
                json={'name': 'Temp', 'codigo': 'TMP'},
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            role_id = role.json()['id']
            user_id = str(admin_token['user'].id)

            await client.post(
                f'/api/v1/users/{user_id}/roles',
                json={'role_id': role_id},
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            delete_resp = await client.delete(
                f'/api/v1/users/{user_id}/roles/{role_id}',
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            assert delete_resp.status_code == 204

    @pytest.mark.asyncio
    async def test_non_admin_gets_403(self, app, db_session, admin_token):
        tid = admin_token['tid']
        no_perm_user = User(tenant_id=tid, email='noperm@t.com', password_hash='hash', roles=[])
        db_session.add(no_perm_user)
        await db_session.flush()
        no_perm_token = create_access_token(str(no_perm_user.id), str(tid), [])

        app.dependency_overrides[get_db] = lambda: db_session
        async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
            response = await client.get(
                '/api/v1/roles',
                headers={'Authorization': f'Bearer {no_perm_token}'},
            )
            assert response.status_code == 403
