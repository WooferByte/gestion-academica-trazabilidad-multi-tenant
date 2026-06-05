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


class TestMateriasAPI:
    async def _client(self, app, db_session, token):
        app.dependency_overrides[get_db] = lambda: db_session
        client = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        client.headers['Authorization'] = f'Bearer {token}'
        return client

    @pytest.mark.asyncio
    async def test_create_materia(self, app, db_session, admin_token):
        async with await self._client(app, db_session, admin_token['token']) as client:
            response = await client.post(
                '/api/v1/admin/materias',
                json={'codigo': 'MATE', 'nombre': 'Matemáticas'},
            )
            assert response.status_code == 201
            data = response.json()
            assert data['codigo'] == 'MATE'
            assert data['nombre'] == 'Matemáticas'
            assert data['estado'] == 'Activa'

    @pytest.mark.asyncio
    async def test_create_materia_duplicate_codigo(self, app, db_session, admin_token):
        async with await self._client(app, db_session, admin_token['token']) as client:
            await client.post(
                '/api/v1/admin/materias',
                json={'codigo': 'FIS', 'nombre': 'Física'},
            )
            response = await client.post(
                '/api/v1/admin/materias',
                json={'codigo': 'FIS', 'nombre': 'Física II'},
            )
            assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_create_materia_duplicate_other_tenant(self, app, db_session, admin_token):
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
            await client1.post(
                '/api/v1/admin/materias',
                json={'codigo': 'MATE', 'nombre': 'Matemáticas'},
            )
        async with await self._client(app, db_session, token2) as client2:
            response = await client2.post(
                '/api/v1/admin/materias',
                json={'codigo': 'MATE', 'nombre': 'Matemáticas Aplicadas'},
            )
            assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_list_materias(self, app, db_session, admin_token):
        async with await self._client(app, db_session, admin_token['token']) as client:
            await client.post(
                '/api/v1/admin/materias',
                json={'codigo': 'MATE', 'nombre': 'Matemáticas'},
            )
            await client.post(
                '/api/v1/admin/materias',
                json={'codigo': 'FIS', 'nombre': 'Física'},
            )
            response = await client.get('/api/v1/admin/materias')
            assert response.status_code == 200
            data = response.json()
            assert data['total'] == 2

    @pytest.mark.asyncio
    async def test_get_materia(self, app, db_session, admin_token):
        async with await self._client(app, db_session, admin_token['token']) as client:
            created = await client.post(
                '/api/v1/admin/materias',
                json={'codigo': 'MATE', 'nombre': 'Matemáticas'},
            )
            materia_id = created.json()['id']
            response = await client.get(f'/api/v1/admin/materias/{materia_id}')
            assert response.status_code == 200
            assert response.json()['codigo'] == 'MATE'

    @pytest.mark.asyncio
    async def test_update_materia(self, app, db_session, admin_token):
        async with await self._client(app, db_session, admin_token['token']) as client:
            created = await client.post(
                '/api/v1/admin/materias',
                json={'codigo': 'MATE', 'nombre': 'Matemáticas'},
            )
            materia_id = created.json()['id']
            response = await client.put(
                f'/api/v1/admin/materias/{materia_id}',
                json={'nombre': 'Matemáticas Avanzadas'},
            )
            assert response.status_code == 200
            assert response.json()['nombre'] == 'Matemáticas Avanzadas'

    @pytest.mark.asyncio
    async def test_soft_delete_materia(self, app, db_session, admin_token):
        async with await self._client(app, db_session, admin_token['token']) as client:
            created = await client.post(
                '/api/v1/admin/materias',
                json={'codigo': 'TEMP', 'nombre': 'Temporal'},
            )
            materia_id = created.json()['id']
            response = await client.delete(f'/api/v1/admin/materias/{materia_id}')
            assert response.status_code == 204
            get_resp = await client.get(f'/api/v1/admin/materias/{materia_id}')
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
            await client1.post(
                '/api/v1/admin/materias',
                json={'codigo': 'MATE', 'nombre': 'Matemáticas'},
            )
        async with await self._client(app, db_session, token2) as client2:
            response = await client2.get('/api/v1/admin/materias')
            assert response.status_code == 200
            data = response.json()
            assert data['total'] == 0
