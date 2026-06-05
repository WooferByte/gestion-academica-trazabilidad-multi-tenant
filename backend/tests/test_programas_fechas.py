"""Tests for C-17: programas-materia and fechas-academicas CRUD."""

import uuid
from datetime import date, datetime, timezone

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.core.dependencies import get_db
from app.core.security import create_access_token
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.materia import Materia
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.tenant import Tenant
from app.models.user import User
from app.models.user_role import UserRole


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


@pytest_asyncio.fixture
async def estructura(db_session, admin_token):
    carrera = Carrera(
        tenant_id=admin_token['tid'], codigo='ING', nombre='Ingeniería',
    )
    db_session.add(carrera)
    await db_session.flush()

    cohorte = Cohorte(
        tenant_id=admin_token['tid'], carrera_id=carrera.id,
        nombre='2025', anio=2025, vig_desde=date(2025, 1, 1), estado='Activa',
    )
    db_session.add(cohorte)
    await db_session.flush()

    materia = Materia(
        tenant_id=admin_token['tid'], codigo='MATE', nombre='Matemáticas',
    )
    db_session.add(materia)
    await db_session.flush()

    return {'carrera': carrera, 'cohorte': cohorte, 'materia': materia}


class TestProgramasMateria:
    async def _client(self, app, db_session, token):
        app.dependency_overrides[get_db] = lambda: db_session
        client = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        client.headers['Authorization'] = f'Bearer {token}'
        return client

    @pytest.mark.asyncio
    async def test_create_programa(self, app, db_session, admin_token, estructura):
        async with await self._client(app, db_session, admin_token['token']) as client:
            response = await client.post(
                '/api/v1/admin/programas',
                json={
                    'materia_id': str(estructura['materia'].id),
                    'carrera_id': str(estructura['carrera'].id),
                    'cohorte_id': str(estructura['cohorte'].id),
                    'titulo': 'Programa 2025',
                },
            )
            assert response.status_code == 201
            data = response.json()
            assert data['titulo'] == 'Programa 2025'
            assert data['materia_id'] == str(estructura['materia'].id)

    @pytest.mark.asyncio
    async def test_create_programa_duplicate(self, app, db_session, admin_token, estructura):
        async with await self._client(app, db_session, admin_token['token']) as client:
            await client.post(
                '/api/v1/admin/programas',
                json={
                    'materia_id': str(estructura['materia'].id),
                    'carrera_id': str(estructura['carrera'].id),
                    'cohorte_id': str(estructura['cohorte'].id),
                    'titulo': 'Programa 2025',
                },
            )
            response = await client.post(
                '/api/v1/admin/programas',
                json={
                    'materia_id': str(estructura['materia'].id),
                    'carrera_id': str(estructura['carrera'].id),
                    'cohorte_id': str(estructura['cohorte'].id),
                    'titulo': 'Programa 2025 v2',
                },
            )
            assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_list_programas(self, app, db_session, admin_token, estructura):
        async with await self._client(app, db_session, admin_token['token']) as client:
            await client.post(
                '/api/v1/admin/programas',
                json={
                    'materia_id': str(estructura['materia'].id),
                    'carrera_id': str(estructura['carrera'].id),
                    'cohorte_id': str(estructura['cohorte'].id),
                    'titulo': 'Programa 2025',
                },
            )
            response = await client.get('/api/v1/admin/programas')
            assert response.status_code == 200
            data = response.json()
            assert data['total'] == 1
            assert data['items'][0]['titulo'] == 'Programa 2025'

    @pytest.mark.asyncio
    async def test_get_programa(self, app, db_session, admin_token, estructura):
        async with await self._client(app, db_session, admin_token['token']) as client:
            created = await client.post(
                '/api/v1/admin/programas',
                json={
                    'materia_id': str(estructura['materia'].id),
                    'carrera_id': str(estructura['carrera'].id),
                    'cohorte_id': str(estructura['cohorte'].id),
                    'titulo': 'Programa 2025',
                },
            )
            programa_id = created.json()['id']
            response = await client.get(f'/api/v1/admin/programas/{programa_id}')
            assert response.status_code == 200
            assert response.json()['titulo'] == 'Programa 2025'

    @pytest.mark.asyncio
    async def test_update_programa(self, app, db_session, admin_token, estructura):
        async with await self._client(app, db_session, admin_token['token']) as client:
            created = await client.post(
                '/api/v1/admin/programas',
                json={
                    'materia_id': str(estructura['materia'].id),
                    'carrera_id': str(estructura['carrera'].id),
                    'cohorte_id': str(estructura['cohorte'].id),
                    'titulo': 'Programa 2025',
                },
            )
            programa_id = created.json()['id']
            response = await client.put(
                f'/api/v1/admin/programas/{programa_id}',
                json={'titulo': 'Programa 2025 Actualizado'},
            )
            assert response.status_code == 200
            assert response.json()['titulo'] == 'Programa 2025 Actualizado'

    @pytest.mark.asyncio
    async def test_soft_delete_programa(self, app, db_session, admin_token, estructura):
        async with await self._client(app, db_session, admin_token['token']) as client:
            created = await client.post(
                '/api/v1/admin/programas',
                json={
                    'materia_id': str(estructura['materia'].id),
                    'carrera_id': str(estructura['carrera'].id),
                    'cohorte_id': str(estructura['cohorte'].id),
                    'titulo': 'Programa 2025',
                },
            )
            programa_id = created.json()['id']
            response = await client.delete(f'/api/v1/admin/programas/{programa_id}')
            assert response.status_code == 204
            get_resp = await client.get(f'/api/v1/admin/programas/{programa_id}')
            assert get_resp.status_code == 404

    @pytest.mark.asyncio
    async def test_multi_tenant_isolation_programa(self, app, db_session, admin_token, estructura):
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
                '/api/v1/admin/programas',
                json={
                    'materia_id': str(estructura['materia'].id),
                    'carrera_id': str(estructura['carrera'].id),
                    'cohorte_id': str(estructura['cohorte'].id),
                    'titulo': 'Programa 2025',
                },
            )
        async with await self._client(app, db_session, token2) as client2:
            response = await client2.get('/api/v1/admin/programas')
            assert response.status_code == 200
            data = response.json()
            assert data['total'] == 0


class TestFechasAcademicas:
    async def _client(self, app, db_session, token):
        app.dependency_overrides[get_db] = lambda: db_session
        client = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        client.headers['Authorization'] = f'Bearer {token}'
        return client

    @pytest.mark.asyncio
    async def test_create_fecha(self, app, db_session, admin_token, estructura):
        async with await self._client(app, db_session, admin_token['token']) as client:
            response = await client.post(
                '/api/v1/admin/fechas-academicas',
                json={
                    'materia_id': str(estructura['materia'].id),
                    'cohorte_id': str(estructura['cohorte'].id),
                    'tipo': 'Parcial',
                    'numero': 1,
                    'periodo': '2025-1C',
                    'fecha': '2025-05-15',
                    'titulo': 'Primer Parcial',
                },
            )
            assert response.status_code == 201
            data = response.json()
            assert data['titulo'] == 'Primer Parcial'
            assert data['tipo'] == 'Parcial'

    @pytest.mark.asyncio
    async def test_list_fechas(self, app, db_session, admin_token, estructura):
        async with await self._client(app, db_session, admin_token['token']) as client:
            await client.post(
                '/api/v1/admin/fechas-academicas',
                json={
                    'materia_id': str(estructura['materia'].id),
                    'cohorte_id': str(estructura['cohorte'].id),
                    'tipo': 'Parcial',
                    'numero': 1,
                    'periodo': '2025-1C',
                    'fecha': '2025-05-15',
                    'titulo': 'Primer Parcial',
                },
            )
            await client.post(
                '/api/v1/admin/fechas-academicas',
                json={
                    'materia_id': str(estructura['materia'].id),
                    'cohorte_id': str(estructura['cohorte'].id),
                    'tipo': 'TP',
                    'numero': 1,
                    'periodo': '2025-1C',
                    'fecha': '2025-04-10',
                    'titulo': 'TP1',
                },
            )
            response = await client.get('/api/v1/admin/fechas-academicas')
            assert response.status_code == 200
            data = response.json()
            assert data['total'] == 2

    @pytest.mark.asyncio
    async def test_list_fechas_filtered(self, app, db_session, admin_token, estructura):
        async with await self._client(app, db_session, admin_token['token']) as client:
            await client.post(
                '/api/v1/admin/fechas-academicas',
                json={
                    'materia_id': str(estructura['materia'].id),
                    'cohorte_id': str(estructura['cohorte'].id),
                    'tipo': 'Parcial',
                    'numero': 1,
                    'periodo': '2025-1C',
                    'fecha': '2025-05-15',
                    'titulo': 'Primer Parcial',
                },
            )
            await client.post(
                '/api/v1/admin/fechas-academicas',
                json={
                    'materia_id': str(estructura['materia'].id),
                    'cohorte_id': str(estructura['cohorte'].id),
                    'tipo': 'TP',
                    'numero': 1,
                    'periodo': '2025-1C',
                    'fecha': '2025-04-10',
                    'titulo': 'TP1',
                },
            )
            response = await client.get(
                '/api/v1/admin/fechas-academicas',
                params={'tipo': 'TP'},
            )
            assert response.status_code == 200
            data = response.json()
            assert data['total'] == 1
            assert data['items'][0]['tipo'] == 'TP'

    @pytest.mark.asyncio
    async def test_get_fecha(self, app, db_session, admin_token, estructura):
        async with await self._client(app, db_session, admin_token['token']) as client:
            created = await client.post(
                '/api/v1/admin/fechas-academicas',
                json={
                    'materia_id': str(estructura['materia'].id),
                    'cohorte_id': str(estructura['cohorte'].id),
                    'tipo': 'Parcial',
                    'numero': 1,
                    'periodo': '2025-1C',
                    'fecha': '2025-05-15',
                    'titulo': 'Primer Parcial',
                },
            )
            fecha_id = created.json()['id']
            response = await client.get(f'/api/v1/admin/fechas-academicas/{fecha_id}')
            assert response.status_code == 200
            assert response.json()['titulo'] == 'Primer Parcial'

    @pytest.mark.asyncio
    async def test_update_fecha(self, app, db_session, admin_token, estructura):
        async with await self._client(app, db_session, admin_token['token']) as client:
            created = await client.post(
                '/api/v1/admin/fechas-academicas',
                json={
                    'materia_id': str(estructura['materia'].id),
                    'cohorte_id': str(estructura['cohorte'].id),
                    'tipo': 'Parcial',
                    'numero': 1,
                    'periodo': '2025-1C',
                    'fecha': '2025-05-15',
                    'titulo': 'Primer Parcial',
                },
            )
            fecha_id = created.json()['id']
            response = await client.put(
                f'/api/v1/admin/fechas-academicas/{fecha_id}',
                json={'titulo': 'Primer Parcial Modificado'},
            )
            assert response.status_code == 200
            assert response.json()['titulo'] == 'Primer Parcial Modificado'

    @pytest.mark.asyncio
    async def test_soft_delete_fecha(self, app, db_session, admin_token, estructura):
        async with await self._client(app, db_session, admin_token['token']) as client:
            created = await client.post(
                '/api/v1/admin/fechas-academicas',
                json={
                    'materia_id': str(estructura['materia'].id),
                    'cohorte_id': str(estructura['cohorte'].id),
                    'tipo': 'Parcial',
                    'numero': 1,
                    'periodo': '2025-1C',
                    'fecha': '2025-05-15',
                    'titulo': 'Primer Parcial',
                },
            )
            fecha_id = created.json()['id']
            response = await client.delete(f'/api/v1/admin/fechas-academicas/{fecha_id}')
            assert response.status_code == 204
            get_resp = await client.get(f'/api/v1/admin/fechas-academicas/{fecha_id}')
            assert get_resp.status_code == 404
