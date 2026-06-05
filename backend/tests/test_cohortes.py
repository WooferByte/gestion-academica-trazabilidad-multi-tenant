import uuid

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
import pytest


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


class TestCohortesAPI:
    async def _client(self, app, db_session, token):
        app.dependency_overrides[get_db] = lambda: db_session
        client = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        client.headers['Authorization'] = f'Bearer {token}'
        return client

    @pytest.mark.asyncio
    async def test_create_cohorte(self, app, db_session, admin_token):
        async with await self._client(app, db_session, admin_token['token']) as client:
            carrera = await client.post(
                '/api/v1/admin/carreras',
                json={'codigo': 'ING', 'nombre': 'Ingeniería'},
            )
            carrera_id = carrera.json()['id']

            response = await client.post(
                '/api/v1/admin/cohortes',
                json={
                    'carrera_id': carrera_id,
                    'nombre': '2025',
                    'anio': 2025,
                    'vig_desde': '2025-01-01',
                },
            )
            assert response.status_code == 201
            data = response.json()
            assert data['nombre'] == '2025'
            assert data['anio'] == 2025

    @pytest.mark.asyncio
    async def test_create_cohorte_duplicate_name_same_carrera(self, app, db_session, admin_token):
        async with await self._client(app, db_session, admin_token['token']) as client:
            carrera = await client.post(
                '/api/v1/admin/carreras',
                json={'codigo': 'ING', 'nombre': 'Ingeniería'},
            )
            carrera_id = carrera.json()['id']

            await client.post(
                '/api/v1/admin/cohortes',
                json={
                    'carrera_id': carrera_id,
                    'nombre': '2025',
                    'anio': 2025,
                    'vig_desde': '2025-01-01',
                },
            )
            response = await client.post(
                '/api/v1/admin/cohortes',
                json={
                    'carrera_id': carrera_id,
                    'nombre': '2025',
                    'anio': 2026,
                    'vig_desde': '2026-01-01',
                },
            )
            assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_create_cohorte_duplicate_name_different_carrera(self, app, db_session, admin_token):
        async with await self._client(app, db_session, admin_token['token']) as client:
            c1 = await client.post(
                '/api/v1/admin/carreras',
                json={'codigo': 'ING', 'nombre': 'Ingeniería'},
            )
            c2 = await client.post(
                '/api/v1/admin/carreras',
                json={'codigo': 'LIC', 'nombre': 'Licenciatura'},
            )

            await client.post(
                '/api/v1/admin/cohortes',
                json={
                    'carrera_id': c1.json()['id'],
                    'nombre': '2025',
                    'anio': 2025,
                    'vig_desde': '2025-01-01',
                },
            )
            response = await client.post(
                '/api/v1/admin/cohortes',
                json={
                    'carrera_id': c2.json()['id'],
                    'nombre': '2025',
                    'anio': 2025,
                    'vig_desde': '2025-01-01',
                },
            )
            assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_create_cohorte_carrera_inactiva(self, app, db_session, admin_token):
        async with await self._client(app, db_session, admin_token['token']) as client:
            carrera = await client.post(
                '/api/v1/admin/carreras',
                json={'codigo': 'ING', 'nombre': 'Ingeniería'},
            )
            carrera_id = carrera.json()['id']
            await client.put(
                f'/api/v1/admin/carreras/{carrera_id}',
                json={'estado': 'Inactiva'},
            )
            response = await client.post(
                '/api/v1/admin/cohortes',
                json={
                    'carrera_id': carrera_id,
                    'nombre': '2025',
                    'anio': 2025,
                    'vig_desde': '2025-01-01',
                },
            )
            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_cohorte_carrera_inexistente(self, app, db_session, admin_token):
        async with await self._client(app, db_session, admin_token['token']) as client:
            response = await client.post(
                '/api/v1/admin/cohortes',
                json={
                    'carrera_id': str(uuid.uuid4()),
                    'nombre': '2025',
                    'anio': 2025,
                    'vig_desde': '2025-01-01',
                },
            )
            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_list_cohortes(self, app, db_session, admin_token):
        async with await self._client(app, db_session, admin_token['token']) as client:
            carrera = await client.post(
                '/api/v1/admin/carreras',
                json={'codigo': 'ING', 'nombre': 'Ingeniería'},
            )
            carrera_id = carrera.json()['id']

            await client.post(
                '/api/v1/admin/cohortes',
                json={
                    'carrera_id': carrera_id,
                    'nombre': '2025',
                    'anio': 2025,
                    'vig_desde': '2025-01-01',
                },
            )
            await client.post(
                '/api/v1/admin/cohortes',
                json={
                    'carrera_id': carrera_id,
                    'nombre': '2026',
                    'anio': 2026,
                    'vig_desde': '2026-01-01',
                },
            )

            response = await client.get('/api/v1/admin/cohortes')
            assert response.status_code == 200
            data = response.json()
            assert data['total'] == 2

    @pytest.mark.asyncio
    async def test_get_cohorte(self, app, db_session, admin_token):
        async with await self._client(app, db_session, admin_token['token']) as client:
            carrera = await client.post(
                '/api/v1/admin/carreras',
                json={'codigo': 'ING', 'nombre': 'Ingeniería'},
            )
            created = await client.post(
                '/api/v1/admin/cohortes',
                json={
                    'carrera_id': carrera.json()['id'],
                    'nombre': '2025',
                    'anio': 2025,
                    'vig_desde': '2025-01-01',
                },
            )
            cohorte_id = created.json()['id']
            response = await client.get(f'/api/v1/admin/cohortes/{cohorte_id}')
            assert response.status_code == 200
            assert response.json()['nombre'] == '2025'

    @pytest.mark.asyncio
    async def test_update_cohorte(self, app, db_session, admin_token):
        async with await self._client(app, db_session, admin_token['token']) as client:
            carrera = await client.post(
                '/api/v1/admin/carreras',
                json={'codigo': 'ING', 'nombre': 'Ingeniería'},
            )
            created = await client.post(
                '/api/v1/admin/cohortes',
                json={
                    'carrera_id': carrera.json()['id'],
                    'nombre': '2025',
                    'anio': 2025,
                    'vig_desde': '2025-01-01',
                },
            )
            cohorte_id = created.json()['id']
            response = await client.put(
                f'/api/v1/admin/cohortes/{cohorte_id}',
                json={'vig_hasta': '2025-12-31'},
            )
            assert response.status_code == 200
            assert response.json()['vig_hasta'] == '2025-12-31'

    @pytest.mark.asyncio
    async def test_soft_delete_cohorte(self, app, db_session, admin_token):
        async with await self._client(app, db_session, admin_token['token']) as client:
            carrera = await client.post(
                '/api/v1/admin/carreras',
                json={'codigo': 'ING', 'nombre': 'Ingeniería'},
            )
            created = await client.post(
                '/api/v1/admin/cohortes',
                json={
                    'carrera_id': carrera.json()['id'],
                    'nombre': '2025',
                    'anio': 2025,
                    'vig_desde': '2025-01-01',
                },
            )
            cohorte_id = created.json()['id']
            response = await client.delete(f'/api/v1/admin/cohortes/{cohorte_id}')
            assert response.status_code == 204
            get_resp = await client.get(f'/api/v1/admin/cohortes/{cohorte_id}')
            assert get_resp.status_code == 404

    @pytest.mark.asyncio
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

        async with await self._client(app, db_session, admin_token['token']) as client1:
            carrera = await client1.post(
                '/api/v1/admin/carreras',
                json={'codigo': 'ING', 'nombre': 'Ingeniería'},
            )
        async with await self._client(app, db_session, token2) as client2:
            await client2.post(
                '/api/v1/admin/carreras',
                json={'codigo': 'LIC', 'nombre': 'Licenciatura'},
            )
            response = await client2.get('/api/v1/admin/cohortes')
            assert response.status_code == 200
            assert response.json()['total'] == 0
