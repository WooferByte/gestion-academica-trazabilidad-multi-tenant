import uuid
from datetime import datetime, timedelta, timezone

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.core.dependencies import get_db
from app.core.security import (
    create_access_token,
    decrypt,
    encrypt,
    hash_email,
    hash_password,
)
from app.models.asignacion import Asignacion
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
async def admin_tenant(db_session):
    tid = uuid.uuid4()
    t = Tenant(id=tid, nombre='Test', codigo='TST', estado='Activo')
    db_session.add(t)
    await db_session.flush()
    return t


@pytest_asyncio.fixture
async def admin_setup(db_session, admin_tenant):
    tid = admin_tenant.id
    email = 'admin@test.com'
    user = User(
        tenant_id=tid,
        email=email,
        email_cifrado=encrypt(email),
        email_hash=hash_email(email),
        password_hash=hash_password('admin123'),
        roles=['ADMIN'],
    )
    db_session.add(user)

    role_admin = Role(tenant_id=tid, name='ADMIN', codigo='ADMIN')
    db_session.add(role_admin)

    p_equipos = Permission(
        tenant_id=tid, codigo='equipos:asignar', modulo='equipos', accion='asignar',
    )
    db_session.add(p_equipos)
    await db_session.flush()

    db_session.add_all([
        RolePermission(tenant_id=tid, role_id=role_admin.id, permiso_id=p_equipos.id),
        UserRole(tenant_id=tid, user_id=user.id, role_id=role_admin.id),
    ])
    await db_session.flush()

    token = create_access_token(str(user.id), str(tid), ['ADMIN'])
    return {
        'token': token,
        'tid': tid,
        'user': user,
    }


@pytest_asyncio.fixture
async def base_entities(db_session, admin_tenant):
    carrera = Carrera(tenant_id=admin_tenant.id, codigo='ING', nombre='Ingeniería')
    db_session.add(carrera)
    await db_session.flush()

    cohorte1 = Cohorte(
        tenant_id=admin_tenant.id, carrera_id=carrera.id,
        nombre='2026', anio=2026,
        vig_desde=datetime.now(timezone.utc).date(),
    )
    cohorte2 = Cohorte(
        tenant_id=admin_tenant.id, carrera_id=carrera.id,
        nombre='2027', anio=2027,
        vig_desde=datetime.now(timezone.utc).date(),
    )
    db_session.add_all([cohorte1, cohorte2])

    materia = Materia(tenant_id=admin_tenant.id, codigo='MATE', nombre='Matemáticas')
    db_session.add(materia)
    await db_session.flush()

    return {
        'carrera': carrera,
        'cohorte1': cohorte1,
        'cohorte2': cohorte2,
        'materia': materia,
    }


@pytest_asyncio.fixture
async def profesor_setup(db_session, admin_tenant):
    users = []
    for i in range(3):
        email = f'profesor{i}@test.com'
        u = User(
            tenant_id=admin_tenant.id,
            email=email,
            email_cifrado=encrypt(email),
            email_hash=hash_email(email),
            password_hash='hash',
            roles=['PROFESOR'],
            nombre_cifrado=encrypt(f'Nombre{i}'),
            apellido_cifrado=encrypt(f'Apellido{i}'),
        )
        db_session.add(u)
        users.append(u)
    await db_session.flush()
    return users


class TestMisEquipos:
    async def _client(self, app, db_session, token_value):
        app.dependency_overrides[get_db] = lambda: db_session
        client = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        client.headers['Authorization'] = f'Bearer {token_value}'
        return client

    @pytest_asyncio.fixture(autouse=True)
    async def _setup_asignaciones(self, db_session, admin_tenant, base_entities, profesor_setup):
        for p in profesor_setup:
            a = Asignacion(
                tenant_id=admin_tenant.id,
                usuario_id=p.id,
                rol='PROFESOR',
                materia_id=base_entities['materia'].id,
                carrera_id=base_entities['carrera'].id,
                cohorte_id=base_entities['cohorte1'].id,
                desde=datetime.now(timezone.utc) - timedelta(days=30),
                hasta=datetime.now(timezone.utc) + timedelta(days=30),
            )
            db_session.add(a)
        await db_session.flush()

    async def test_mis_equipos_sin_filtros(self, app, db_session, admin_setup, profesor_setup):
        token = create_access_token(
            str(profesor_setup[0].id), str(admin_setup['tid']), ['PROFESOR'],
        )
        async with await self._client(app, db_session, token) as client:
            response = await client.get('/api/v1/equipos/mis-equipos')
            assert response.status_code == 200
            data = response.json()
            assert data['total'] == 1
            assert data['items'][0]['usuario_id'] == str(profesor_setup[0].id)

    async def test_mis_equipos_filtro_materia(self, app, db_session, admin_setup, profesor_setup, base_entities):
        token = create_access_token(
            str(profesor_setup[0].id), str(admin_setup['tid']), ['PROFESOR'],
        )
        async with await self._client(app, db_session, token) as client:
            response = await client.get(
                f'/api/v1/equipos/mis-equipos?materia_id={base_entities["materia"].id}',
            )
            assert response.status_code == 200
            assert response.json()['total'] == 1

    async def test_mis_equipos_solo_vigentes(self, app, db_session, admin_setup, profesor_setup, base_entities):
        tid = admin_setup['tid']
        vencida = Asignacion(
            tenant_id=tid,
            usuario_id=profesor_setup[1].id,
            rol='TUTOR',
            materia_id=base_entities['materia'].id,
            carrera_id=base_entities['carrera'].id,
            cohorte_id=base_entities['cohorte1'].id,
            desde=datetime.now(timezone.utc) - timedelta(days=60),
            hasta=datetime.now(timezone.utc) - timedelta(days=1),
        )
        db_session.add(vencida)
        await db_session.flush()

        token = create_access_token(
            str(profesor_setup[1].id), str(tid), ['PROFESOR', 'TUTOR'],
        )
        async with await self._client(app, db_session, token) as client:
            response = await client.get('/api/v1/equipos/mis-equipos?solo_vigentes=true')
            assert response.status_code == 200
            data = response.json()
            assert data['total'] == 1
            assert data['items'][0]['rol'] == 'PROFESOR'

    async def test_mis_equipos_401(self, app, db_session):
        async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
            response = await client.get('/api/v1/equipos/mis-equipos')
            assert response.status_code == 401


class TestAsignacionMasiva:
    async def _client(self, app, db_session, token_value):
        app.dependency_overrides[get_db] = lambda: db_session
        client = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        client.headers['Authorization'] = f'Bearer {token_value}'
        return client

    async def test_asignacion_masiva_exitosa(self, app, db_session, admin_setup, base_entities, profesor_setup):
        async with await self._client(app, db_session, admin_setup['token']) as client:
            response = await client.post(
                '/api/v1/equipos/asignacion-masiva',
                json={
                    'usuario_ids': [str(p.id) for p in profesor_setup],
                    'materia_id': str(base_entities['materia'].id),
                    'carrera_id': str(base_entities['carrera'].id),
                    'cohorte_id': str(base_entities['cohorte1'].id),
                    'rol': 'PROFESOR',
                    'comisiones': ['A', 'B'],
                    'desde': (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                    'hasta': (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
                },
            )
            assert response.status_code == 201
            data = response.json()
            assert len(data) == 3
            for item in data:
                assert item['rol'] == 'PROFESOR'
                assert item['materia_id'] == str(base_entities['materia'].id)

    async def test_asignacion_masiva_usuario_inexistente(self, app, db_session, admin_setup, base_entities):
        async with await self._client(app, db_session, admin_setup['token']) as client:
            fake_id = uuid.uuid4()
            response = await client.post(
                '/api/v1/equipos/asignacion-masiva',
                json={
                    'usuario_ids': [str(fake_id)],
                    'materia_id': str(base_entities['materia'].id),
                    'carrera_id': str(base_entities['carrera'].id),
                    'cohorte_id': str(base_entities['cohorte1'].id),
                    'rol': 'PROFESOR',
                },
            )
            assert response.status_code == 422

    async def test_asignacion_masiva_403(self, app, db_session, admin_tenant, base_entities):
        tid = admin_tenant.id
        email = 'alumno@test.com'
        user = User(
            tenant_id=tid, email=email,
            email_cifrado=encrypt(email), email_hash=hash_email(email),
            password_hash='hash', roles=['ALUMNO'],
        )
        db_session.add(user)
        role_alumno = Role(tenant_id=tid, name='ALUMNO', codigo='ALUMNO')
        db_session.add(role_alumno)
        await db_session.flush()
        db_session.add(UserRole(tenant_id=tid, user_id=user.id, role_id=role_alumno.id))
        await db_session.flush()
        token = create_access_token(str(user.id), str(tid), ['ALUMNO'])

        async with await self._client(app, db_session, token) as client:
            response = await client.post(
                '/api/v1/equipos/asignacion-masiva',
                json={
                    'usuario_ids': [str(uuid.uuid4())],
                    'rol': 'PROFESOR',
                },
            )
            assert response.status_code == 403


class TestClonarEquipo:
    async def _client(self, app, db_session, token_value):
        app.dependency_overrides[get_db] = lambda: db_session
        client = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        client.headers['Authorization'] = f'Bearer {token_value}'
        return client

    async def test_clonar_exitoso(self, app, db_session, admin_setup, base_entities, profesor_setup):
        tid = admin_setup['tid']
        for p in profesor_setup:
            a = Asignacion(
                tenant_id=tid,
                usuario_id=p.id,
                rol='PROFESOR',
                materia_id=base_entities['materia'].id,
                carrera_id=base_entities['carrera'].id,
                cohorte_id=base_entities['cohorte1'].id,
                desde=datetime.now(timezone.utc) - timedelta(days=30),
                hasta=datetime.now(timezone.utc) + timedelta(days=30),
                comisiones=['A'],
            )
            db_session.add(a)
        await db_session.flush()

        async with await self._client(app, db_session, admin_setup['token']) as client:
            response = await client.post(
                '/api/v1/equipos/clonar',
                json={
                    'origen': {
                        'materia_id': str(base_entities['materia'].id),
                        'carrera_id': str(base_entities['carrera'].id),
                        'cohorte_id': str(base_entities['cohorte1'].id),
                    },
                    'destino': {
                        'materia_id': str(base_entities['materia'].id),
                        'carrera_id': str(base_entities['carrera'].id),
                        'cohorte_id': str(base_entities['cohorte2'].id),
                        'desde': (datetime.now(timezone.utc)).isoformat(),
                        'hasta': (datetime.now(timezone.utc) + timedelta(days=365)).isoformat(),
                    },
                },
            )
            assert response.status_code == 201
            data = response.json()
            assert len(data) == 3
            for item in data:
                assert item['cohorte_id'] == str(base_entities['cohorte2'].id)

    async def test_clonar_sin_vigentes(self, app, db_session, admin_setup, base_entities):
        async with await self._client(app, db_session, admin_setup['token']) as client:
            response = await client.post(
                '/api/v1/equipos/clonar',
                json={
                    'origen': {
                        'materia_id': str(base_entities['materia'].id),
                        'carrera_id': str(base_entities['carrera'].id),
                        'cohorte_id': str(base_entities['cohorte1'].id),
                    },
                    'destino': {
                        'materia_id': str(base_entities['materia'].id),
                        'carrera_id': str(base_entities['carrera'].id),
                        'cohorte_id': str(base_entities['cohorte2'].id),
                        'desde': (datetime.now(timezone.utc)).isoformat(),
                        'hasta': (datetime.now(timezone.utc) + timedelta(days=365)).isoformat(),
                    },
                },
            )
            assert response.status_code == 201
            assert response.json() == []


class TestVigenciaEquipo:
    async def _client(self, app, db_session, token_value):
        app.dependency_overrides[get_db] = lambda: db_session
        client = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        client.headers['Authorization'] = f'Bearer {token_value}'
        return client

    @pytest_asyncio.fixture(autouse=True)
    async def _setup(self, db_session, admin_setup, base_entities, profesor_setup):
        tid = admin_setup['tid']
        for p in profesor_setup:
            a = Asignacion(
                tenant_id=tid,
                usuario_id=p.id,
                rol='PROFESOR',
                materia_id=base_entities['materia'].id,
                carrera_id=base_entities['carrera'].id,
                cohorte_id=base_entities['cohorte1'].id,
                desde=datetime.now(timezone.utc) - timedelta(days=30),
                hasta=datetime.now(timezone.utc) + timedelta(days=30),
            )
            db_session.add(a)
        await db_session.flush()

    async def test_modificar_vigencia_exitoso(self, app, db_session, admin_setup, base_entities):
        async with await self._client(app, db_session, admin_setup['token']) as client:
            nuevo_desde = (datetime.now(timezone.utc)).isoformat()
            nuevo_hasta = (datetime.now(timezone.utc) + timedelta(days=60)).isoformat()
            response = await client.patch(
                '/api/v1/equipos/vigencia',
                json={
                    'materia_id': str(base_entities['materia'].id),
                    'carrera_id': str(base_entities['carrera'].id),
                    'cohorte_id': str(base_entities['cohorte1'].id),
                    'desde': nuevo_desde,
                    'hasta': nuevo_hasta,
                },
            )
            assert response.status_code == 200
            data = response.json()
            assert data['filas_afectadas'] == 3

    async def test_equipo_inexistente(self, app, db_session, admin_setup, base_entities):
        async with await self._client(app, db_session, admin_setup['token']) as client:
            response = await client.patch(
                '/api/v1/equipos/vigencia',
                json={
                    'materia_id': str(base_entities['materia'].id),
                    'carrera_id': str(base_entities['carrera'].id),
                    'cohorte_id': str(base_entities['cohorte2'].id),
                    'desde': (datetime.now(timezone.utc)).isoformat(),
                },
            )
            assert response.status_code == 404


class TestExportar:
    async def _client(self, app, db_session, token_value):
        app.dependency_overrides[get_db] = lambda: db_session
        client = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        client.headers['Authorization'] = f'Bearer {token_value}'
        return client

    @pytest_asyncio.fixture(autouse=True)
    async def _setup(self, db_session, admin_setup, base_entities, profesor_setup):
        tid = admin_setup['tid']
        for p in profesor_setup:
            a = Asignacion(
                tenant_id=tid,
                usuario_id=p.id,
                rol='PROFESOR',
                materia_id=base_entities['materia'].id,
                carrera_id=base_entities['carrera'].id,
                cohorte_id=base_entities['cohorte1'].id,
            )
            db_session.add(a)
        await db_session.flush()

    async def test_exportar_csv_con_datos(self, app, db_session, admin_setup, base_entities):
        async with await self._client(app, db_session, admin_setup['token']) as client:
            response = await client.get(
                '/api/v1/equipos/exportar',
                params={
                    'materia_id': str(base_entities['materia'].id),
                    'carrera_id': str(base_entities['carrera'].id),
                    'cohorte_id': str(base_entities['cohorte1'].id),
                },
            )
            assert response.status_code == 200
            assert 'text/csv' in response.headers['content-type']
            body = response.text
            assert 'docente' in body
            assert 'Nombre0' in body or 'Apellido0' in body
            lines = body.strip().split('\n')
            assert len(lines) == 4  # header + 3 profes

    async def test_exportar_csv_vacio(self, app, db_session, admin_setup, base_entities):
        async with await self._client(app, db_session, admin_setup['token']) as client:
            response = await client.get(
                '/api/v1/equipos/exportar',
                params={
                    'materia_id': str(uuid.uuid4()),
                },
            )
            assert response.status_code == 200
            assert 'text/csv' in response.headers['content-type']
            body = response.text.strip()
            lines = body.split('\n')
            assert len(lines) == 1  # solo headers
