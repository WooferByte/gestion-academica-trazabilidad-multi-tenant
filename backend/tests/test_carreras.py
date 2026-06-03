import uuid

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.core.dependencies import get_db
from app.core.security import create_access_token
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
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

    p_estructura = Permission(
        tenant_id=tid, codigo='estructura:gestionar', modulo='estructura', accion='gestionar',
    )
    db_session.add(p_estructura)
    await db_session.flush()

    db_session.add_all([
        RolePermission(tenant_id=tid, role_id=role_admin.id, permiso_id=p_estructura.id),
        UserRole(tenant_id=tid, user_id=user.id, role_id=role_admin.id),
    ])
    await db_session.flush()

    token = create_access_token(str(user.id), str(tid), ['ADMIN'])
    return {'token': token, 'tid': tid, 'tenant': tenant, 'user': user}


class TestCarrerasAPI:
    async def _client(self, app, db_session):
        app.dependency_overrides[get_db] = lambda: db_session
        return AsyncClient(transport=ASGITransport(app=app), base_url='http://test')

    async def test_create_carrera(self, app, db_session, admin_token):
        async with await self._client(app, db_session) as client:
            response = await client.post(
                '/api/v1/admin/carreras',
                json={'codigo': 'ING', 'nombre': 'Ingeniería'},
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            assert response.status_code == 201
            data = response.json()
            assert data['codigo'] == 'ING'
            assert data['nombre'] == 'Ingeniería'
            assert data['estado'] == 'Activa'

    async def test_create_carrera_duplicate_codigo(self, app, db_session, admin_token):
        async with await self._client(app, db_session) as client:
            await client.post(
                '/api/v1/admin/carreras',
                json={'codigo': 'LIC', 'nombre': 'Licenciatura'},
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            response = await client.post(
                '/api/v1/admin/carreras',
                json={'codigo': 'LIC', 'nombre': 'Licenciatura en Letras'},
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            assert response.status_code == 409

    async def test_create_carrera_duplicate_other_tenant(self, app, db_session, admin_token):
        tid2 = uuid.uuid4()
        tenant2 = Tenant(id=tid2, nombre='Test2', codigo='TST2', estado='Activo')
        db_session.add(tenant2)
        await db_session.flush()
        user2 = User(tenant_id=tid2, email='admin2@t.com', password_hash='hash', roles=['ADMIN'])
        role2 = Role(tenant_id=tid2, name='ADMIN', codigo='ADMIN')
        db_session.add_all([user2, role2])
        await db_session.flush()
        p2 = Permission(
            tenant_id=tid2, codigo='estructura:gestionar', modulo='estructura', accion='gestionar',
        )
        db_session.add(p2)
        await db_session.flush()
        db_session.add_all([
            RolePermission(tenant_id=tid2, role_id=role2.id, permiso_id=p2.id),
            UserRole(tenant_id=tid2, user_id=user2.id, role_id=role2.id),
        ])
        await db_session.flush()
        token2 = create_access_token(str(user2.id), str(tid2), ['ADMIN'])

        async with await self._client(app, db_session) as client:
            await client.post(
                '/api/v1/admin/carreras',
                json={'codigo': 'LIC', 'nombre': 'Licenciatura'},
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            response = await client.post(
                '/api/v1/admin/carreras',
                json={'codigo': 'LIC', 'nombre': 'Licenciatura en Letras'},
                headers={'Authorization': f'Bearer {token2}'},
            )
            assert response.status_code == 201

    async def test_list_carreras(self, app, db_session, admin_token):
        async with await self._client(app, db_session) as client:
            await client.post(
                '/api/v1/admin/carreras',
                json={'codigo': 'ING', 'nombre': 'Ingeniería'},
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            await client.post(
                '/api/v1/admin/carreras',
                json={'codigo': 'LIC', 'nombre': 'Licenciatura'},
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            response = await client.get(
                '/api/v1/admin/carreras',
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            assert response.status_code == 200
            data = response.json()
            assert data['total'] == 2

    async def test_get_carrera(self, app, db_session, admin_token):
        async with await self._client(app, db_session) as client:
            created = await client.post(
                '/api/v1/admin/carreras',
                json={'codigo': 'ING', 'nombre': 'Ingeniería'},
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            carrera_id = created.json()['id']
            response = await client.get(
                f'/api/v1/admin/carreras/{carrera_id}',
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            assert response.status_code == 200
            assert response.json()['codigo'] == 'ING'

    async def test_get_carrera_not_found(self, app, db_session, admin_token):
        async with await self._client(app, db_session) as client:
            response = await client.get(
                f'/api/v1/admin/carreras/{uuid.uuid4()}',
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            assert response.status_code == 404

    async def test_update_carrera(self, app, db_session, admin_token):
        async with await self._client(app, db_session) as client:
            created = await client.post(
                '/api/v1/admin/carreras',
                json={'codigo': 'ING', 'nombre': 'Ingeniería'},
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            carrera_id = created.json()['id']
            response = await client.put(
                f'/api/v1/admin/carreras/{carrera_id}',
                json={'nombre': 'Ingeniería Actualizada'},
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            assert response.status_code == 200
            assert response.json()['nombre'] == 'Ingeniería Actualizada'

    async def test_update_carrera_duplicate_codigo(self, app, db_session, admin_token):
        async with await self._client(app, db_session) as client:
            await client.post(
                '/api/v1/admin/carreras',
                json={'codigo': 'ING', 'nombre': 'Ingeniería'},
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            c2 = await client.post(
                '/api/v1/admin/carreras',
                json={'codigo': 'LIC', 'nombre': 'Licenciatura'},
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            c2_id = c2.json()['id']
            response = await client.put(
                f'/api/v1/admin/carreras/{c2_id}',
                json={'codigo': 'ING'},
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            assert response.status_code == 409

    async def test_soft_delete_carrera(self, app, db_session, admin_token):
        async with await self._client(app, db_session) as client:
            created = await client.post(
                '/api/v1/admin/carreras',
                json={'codigo': 'ING', 'nombre': 'Ingeniería'},
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            carrera_id = created.json()['id']
            response = await client.delete(
                f'/api/v1/admin/carreras/{carrera_id}',
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            assert response.status_code == 204
            get_resp = await client.get(
                f'/api/v1/admin/carreras/{carrera_id}',
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            assert get_resp.status_code == 404

    async def test_multi_tenant_isolation(self, app, db_session, admin_token):
        tid2 = uuid.uuid4()
        tenant2 = Tenant(id=tid2, nombre='Test2', codigo='TST2', estado='Activo')
        db_session.add(tenant2)
        await db_session.flush()
        user2 = User(tenant_id=tid2, email='admin2@t.com', password_hash='hash', roles=['ADMIN'])
        role2 = Role(tenant_id=tid2, name='ADMIN', codigo='ADMIN')
        db_session.add_all([user2, role2])
        await db_session.flush()
        p2 = Permission(
            tenant_id=tid2, codigo='estructura:gestionar', modulo='estructura', accion='gestionar',
        )
        db_session.add(p2)
        await db_session.flush()
        db_session.add_all([
            RolePermission(tenant_id=tid2, role_id=role2.id, permiso_id=p2.id),
            UserRole(tenant_id=tid2, user_id=user2.id, role_id=role2.id),
        ])
        await db_session.flush()
        token2 = create_access_token(str(user2.id), str(tid2), ['ADMIN'])

        async with await self._client(app, db_session) as client:
            await client.post(
                '/api/v1/admin/carreras',
                json={'codigo': 'ING', 'nombre': 'Ingeniería'},
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            response = await client.get(
                '/api/v1/admin/carreras',
                headers={'Authorization': f'Bearer {token2}'},
            )
            assert response.status_code == 200
            data = response.json()
            assert data['total'] == 0

    async def test_inactivar_carrera_con_cohortes_abiertas(self, app, db_session, admin_token):
        async with await self._client(app, db_session) as client:
            created = await client.post(
                '/api/v1/admin/carreras',
                json={'codigo': 'ING', 'nombre': 'Ingeniería'},
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            carrera_id = created.json()['id']

            await client.post(
                '/api/v1/admin/cohortes',
                json={
                    'carrera_id': carrera_id,
                    'nombre': '2025',
                    'anio': 2025,
                    'vig_desde': '2025-01-01',
                },
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )

            response = await client.put(
                f'/api/v1/admin/carreras/{carrera_id}',
                json={'estado': 'Inactiva'},
                headers={'Authorization': f'Bearer {admin_token["token"]}'},
            )
            assert response.status_code == 422

    async def test_access_without_permission(self, app, db_session, admin_token):
        tid = admin_token['tid']
        no_perm_user = User(tenant_id=tid, email='noperm@t.com', password_hash='hash', roles=[])
        db_session.add(no_perm_user)
        await db_session.flush()
        no_perm_token = create_access_token(str(no_perm_user.id), str(tid), [])

        async with await self._client(app, db_session) as client:
            response = await client.get(
                '/api/v1/admin/carreras',
                headers={'Authorization': f'Bearer {no_perm_token}'},
            )
            assert response.status_code == 403
