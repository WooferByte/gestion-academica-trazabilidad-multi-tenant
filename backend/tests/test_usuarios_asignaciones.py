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

    p_usuarios = Permission(
        tenant_id=tid, codigo='usuarios:gestionar', modulo='usuarios', accion='gestionar',
    )
    p_equipos = Permission(
        tenant_id=tid, codigo='equipos:asignar', modulo='equipos', accion='asignar',
    )
    db_session.add_all([p_usuarios, p_equipos])
    await db_session.flush()

    db_session.add_all([
        RolePermission(tenant_id=tid, role_id=role_admin.id, permiso_id=p_usuarios.id),
        RolePermission(tenant_id=tid, role_id=role_admin.id, permiso_id=p_equipos.id),
        UserRole(tenant_id=tid, user_id=user.id, role_id=role_admin.id),
    ])
    await db_session.flush()

    token = create_access_token(str(user.id), str(tid), ['ADMIN'])
    return {
        'token': token,
        'tid': tid,
        'tenant': admin_tenant,
        'user': user,
        'role_admin': role_admin,
    }


@pytest_asyncio.fixture
async def base_entities(db_session, admin_tenant):
    carrera = Carrera(tenant_id=admin_tenant.id, codigo='ING', nombre='Ingeniería')
    db_session.add(carrera)
    await db_session.flush()

    cohorte = Cohorte(
        tenant_id=admin_tenant.id, carrera_id=carrera.id,
        nombre='2026', anio=2026,
        vig_desde=datetime.now(timezone.utc).date(),
    )
    db_session.add(cohorte)
    await db_session.flush()

    materia = Materia(tenant_id=admin_tenant.id, codigo='MATE', nombre='Matemáticas')
    db_session.add(materia)
    await db_session.flush()

    return {'carrera': carrera, 'cohorte': cohorte, 'materia': materia}


class TestUsuariosAPI:
    async def _client(self, app, db_session, token_value):
        app.dependency_overrides[get_db] = lambda: db_session
        client = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        client.headers['Authorization'] = f'Bearer {token_value}'
        return client

    # 6.1 PII cifrada no se expone en respuestas API
    async def test_pii_not_exposed_in_response(self, app, db_session, admin_setup):
        async with await self._client(app, db_session, admin_setup['token']) as client:
            response = await client.post(
                '/api/v1/admin/usuarios',
                json={
                    'email': 'docente@test.com',
                    'password': 'pass123',
                    'nombre': 'Juan',
                    'apellido': 'Perez',
                    'dni': '12345678',
                    'cuil': '20-12345678-9',
                    'cbu': '0000003100012345678901',
                    'alias_cbu': 'alias.juan',
                    'legajo': 'LEG-001',
                    'facturador': False,
                },
            )
            assert response.status_code == 201
            data = response.json()
            assert data['legajo'] == 'LEG-001'
            assert 'cuil' not in data
            assert 'cbu' not in data
            assert 'alias_cbu' not in data
            assert 'dni' not in data
            assert 'email' not in data
            assert 'cuil_cifrado' not in data
            assert 'cbu_cifrado' not in data

    # 6.2 Unicidad (tenant_id, email) — mismo email en distinto tenant sí se permite
    async def test_email_uniqueness_same_tenant(self, app, db_session, admin_setup):
        async with await self._client(app, db_session, admin_setup['token']) as client:
            await client.post(
                '/api/v1/admin/usuarios',
                json={'email': 'duplicado@test.com', 'password': 'pass123'},
            )
            response = await client.post(
                '/api/v1/admin/usuarios',
                json={'email': 'duplicado@test.com', 'password': 'pass123'},
            )
            assert response.status_code == 409

    async def test_email_uniqueness_different_tenant(
        self, app, db_session, admin_setup,
    ):
        tid2 = uuid.uuid4()
        tenant2 = Tenant(id=tid2, nombre='Test2', codigo='TST2', estado='Activo')
        db_session.add(tenant2)
        await db_session.flush()
        email2 = 'admin2@test.com'
        user2 = User(
            tenant_id=tid2, email=email2,
            email_cifrado=encrypt(email2), email_hash=hash_email(email2),
            password_hash='hash', roles=['ADMIN'],
        )
        role2 = Role(tenant_id=tid2, name='ADMIN', codigo='ADMIN')
        db_session.add_all([user2, role2])
        await db_session.flush()
        p2 = Permission(
            tenant_id=tid2, codigo='usuarios:gestionar', modulo='usuarios', accion='gestionar',
        )
        db_session.add(p2)
        await db_session.flush()
        db_session.add_all([
            RolePermission(tenant_id=tid2, role_id=role2.id, permiso_id=p2.id),
            UserRole(tenant_id=tid2, user_id=user2.id, role_id=role2.id),
        ])
        await db_session.flush()
        token2 = create_access_token(str(user2.id), str(tid2), ['ADMIN'])

        async with await self._client(app, db_session, admin_setup['token']) as c1:
            await c1.post(
                '/api/v1/admin/usuarios',
                json={'email': 'compartido@test.com', 'password': 'pass123'},
            )

        async with await self._client(app, db_session, token2) as c2:
            response = await c2.post(
                '/api/v1/admin/usuarios',
                json={'email': 'compartido@test.com', 'password': 'pass123'},
            )
            assert response.status_code == 201

    # 6.8 403 sin permiso usuarios:gestionar o equipos:asignar
    async def test_403_without_usuarios_gestionar(self, app, db_session, admin_tenant):
        tid = admin_tenant.id
        email = 'basico@test.com'
        user = User(
            tenant_id=tid, email=email,
            email_cifrado=encrypt(email), email_hash=hash_email(email),
            password_hash='hash', roles=['ALUMNO'],
        )
        db_session.add(user)
        role_basic = Role(tenant_id=tid, name='ALUMNO', codigo='ALUMNO')
        db_session.add(role_basic)
        await db_session.flush()
        db_session.add(UserRole(tenant_id=tid, user_id=user.id, role_id=role_basic.id))
        await db_session.flush()
        token = create_access_token(str(user.id), str(tid), ['ALUMNO'])

        async with await self._client(app, db_session, token) as client:
            response = await client.get('/api/v1/admin/usuarios')
            assert response.status_code == 403

    async def test_403_without_equipos_asignar(self, app, db_session, admin_tenant):
        tid = admin_tenant.id
        email = 'basico2@test.com'
        user = User(
            tenant_id=tid, email=email,
            email_cifrado=encrypt(email), email_hash=hash_email(email),
            password_hash='hash', roles=['ALUMNO'],
        )
        db_session.add(user)
        role_basic = Role(tenant_id=tid, name='ALUMNO', codigo='ALUMNO')
        db_session.add(role_basic)
        await db_session.flush()
        db_session.add(UserRole(tenant_id=tid, user_id=user.id, role_id=role_basic.id))
        await db_session.flush()
        token = create_access_token(str(user.id), str(tid), ['ALUMNO'])

        async with await self._client(app, db_session, token) as client:
            response = await client.get('/api/v1/asignaciones')
            assert response.status_code == 403

    # 6.9 Contexto nullable — asignación global sin materia/carrera/cohorte
    async def test_global_asignacion_nullable_context(
        self, app, db_session, admin_setup,
    ):
        async with await self._client(app, db_session, admin_setup['token']) as client:
            email = 'global@test.com'
            create_resp = await client.post(
                '/api/v1/admin/usuarios',
                json={'email': email, 'password': 'pass123'},
            )
            assert create_resp.status_code == 201
            usuario_id = create_resp.json()['id']

            response = await client.post(
                '/api/v1/asignaciones',
                json={
                    'usuario_id': usuario_id,
                    'rol': 'ADMIN',
                },
            )
            assert response.status_code == 201
            data = response.json()
            assert data['rol'] == 'ADMIN'
            assert data['materia_id'] is None
            assert data['carrera_id'] is None
            assert data['cohorte_id'] is None

    # 6.6 Aislamiento multi-tenant
    async def test_multi_tenant_isolation(
        self, app, db_session, admin_setup, base_entities,
    ):
        async with await self._client(app, db_session, admin_setup['token']) as c1:
            user_resp = await c1.post(
                '/api/v1/admin/usuarios',
                json={'email': 'user@test.com', 'password': 'pass123'},
            )
            uid = user_resp.json()['id']
            await c1.post(
                '/api/v1/asignaciones',
                json={
                    'usuario_id': uid,
                    'rol': 'PROFESOR',
                    'materia_id': str(base_entities['materia'].id),
                },
            )
            list_resp = await c1.get('/api/v1/asignaciones')
            assert list_resp.status_code == 200
            assert list_resp.json()['total'] == 1

        tid2 = uuid.uuid4()
        tenant2 = Tenant(id=tid2, nombre='Test2', codigo='TST2', estado='Activo')
        db_session.add(tenant2)
        await db_session.flush()
        email2 = 'admin2b@test.com'
        user2 = User(
            tenant_id=tid2, email=email2,
            email_cifrado=encrypt(email2), email_hash=hash_email(email2),
            password_hash='hash', roles=['ADMIN'],
        )
        role2 = Role(tenant_id=tid2, name='ADMIN', codigo='ADMIN')
        db_session.add_all([user2, role2])
        await db_session.flush()
        p2 = Permission(
            tenant_id=tid2, codigo='equipos:asignar', modulo='equipos', accion='asignar',
        )
        db_session.add(p2)
        await db_session.flush()
        db_session.add_all([
            RolePermission(tenant_id=tid2, role_id=role2.id, permiso_id=p2.id),
            UserRole(tenant_id=tid2, user_id=user2.id, role_id=role2.id),
        ])
        await db_session.flush()
        token2 = create_access_token(str(user2.id), str(tid2), ['ADMIN'])

        async with await self._client(app, db_session, token2) as c2:
            list_resp2 = await c2.get('/api/v1/asignaciones')
            assert list_resp2.status_code == 200
            assert list_resp2.json()['total'] == 0


class TestAsignacionesAPI:
    async def _client(self, app, db_session, token_value):
        app.dependency_overrides[get_db] = lambda: db_session
        client = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        client.headers['Authorization'] = f'Bearer {token_value}'
        return client

    async def _create_user(self, client, email='profesor@test.com'):
        resp = await client.post(
            '/api/v1/admin/usuarios',
            json={'email': email, 'password': 'pass123'},
        )
        return resp.json()['id']

    # 6.3 Creación y consulta de asignación vigente vs vencida
    async def test_asignacion_vigente_vs_vencida(
        self, app, db_session, admin_setup, base_entities,
    ):
        async with await self._client(app, db_session, admin_setup['token']) as client:
            uid = await self._create_user(client)

            vigente_resp = await client.post(
                '/api/v1/asignaciones',
                json={
                    'usuario_id': uid,
                    'rol': 'PROFESOR',
                    'materia_id': str(base_entities['materia'].id),
                    'desde': (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                    'hasta': (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
                },
            )
            assert vigente_resp.status_code == 201
            vigente_id = vigente_resp.json()['id']

            vencida_resp = await client.post(
                '/api/v1/asignaciones',
                json={
                    'usuario_id': uid,
                    'rol': 'TUTOR',
                    'materia_id': str(base_entities['materia'].id),
                    'desde': (datetime.now(timezone.utc) - timedelta(days=90)).isoformat(),
                    'hasta': (datetime.now(timezone.utc) - timedelta(days=61)).isoformat(),
                },
            )
            assert vencida_resp.status_code == 201

            all_resp = await client.get('/api/v1/asignaciones')
            assert all_resp.status_code == 200
            assert all_resp.json()['total'] == 2

            vigentes_resp = await client.get(
                '/api/v1/asignaciones?solo_vigentes=true',
            )
            assert vigentes_resp.status_code == 200
            vigentes = vigentes_resp.json()
            assert vigentes['total'] == 1
            assert vigentes['items'][0]['rol'] == 'PROFESOR'
            assert vigentes['items'][0]['id'] == vigente_id

    # 6.4 Multi-rol (mismo usuario con dos asignaciones distintas)
    async def test_multi_rol_mismo_usuario(
        self, app, db_session, admin_setup, base_entities,
    ):
        async with await self._client(app, db_session, admin_setup['token']) as client:
            uid = await self._create_user(client, 'multirrol@test.com')

            resp1 = await client.post(
                '/api/v1/asignaciones',
                json={
                    'usuario_id': uid,
                    'rol': 'PROFESOR',
                    'materia_id': str(base_entities['materia'].id),
                },
            )
            assert resp1.status_code == 201

            resp2 = await client.post(
                '/api/v1/asignaciones',
                json={
                    'usuario_id': uid,
                    'rol': 'COORDINADOR',
                    'materia_id': str(base_entities['materia'].id),
                },
            )
            assert resp2.status_code == 201

            list_resp = await client.get(
                f'/api/v1/asignaciones?usuario_id={uid}',
            )
            assert list_resp.status_code == 200
            assert list_resp.json()['total'] == 2
            roles = {i['rol'] for i in list_resp.json()['items']}
            assert roles == {'PROFESOR', 'COORDINADOR'}

    # 6.5 Jerarquía responsable_id
    async def test_jerarquia_responsable(
        self, app, db_session, admin_setup, base_entities,
    ):
        async with await self._client(app, db_session, admin_setup['token']) as client:
            responsable_id = await self._create_user(client, 'responsable@test.com')
            profesor_id = await self._create_user(client, 'profesor@test.com')

            resp = await client.post(
                '/api/v1/asignaciones',
                json={
                    'usuario_id': profesor_id,
                    'rol': 'PROFESOR',
                    'materia_id': str(base_entities['materia'].id),
                    'responsable_id': responsable_id,
                },
            )
            assert resp.status_code == 201
            data = resp.json()
            assert data['responsable_id'] == responsable_id

    # 6.7 Soft delete en usuario y asignación
    async def test_soft_delete_usuario(self, app, db_session, admin_setup):
        async with await self._client(app, db_session, admin_setup['token']) as client:
            resp = await client.post(
                '/api/v1/admin/usuarios',
                json={'email': 'delete-user@test.com', 'password': 'pass123'},
            )
            uid = resp.json()['id']

            del_resp = await client.delete(f'/api/v1/admin/usuarios/{uid}')
            assert del_resp.status_code == 200

            get_resp = await client.get(f'/api/v1/admin/usuarios/{uid}')
            assert get_resp.status_code == 404

    async def test_soft_delete_asignacion(
        self, app, db_session, admin_setup, base_entities,
    ):
        async with await self._client(app, db_session, admin_setup['token']) as client:
            uid = await self._create_user(client)
            create_resp = await client.post(
                '/api/v1/asignaciones',
                json={
                    'usuario_id': uid,
                    'rol': 'PROFESOR',
                    'materia_id': str(base_entities['materia'].id),
                },
            )
            aid = create_resp.json()['id']

            del_resp = await client.delete(f'/api/v1/asignaciones/{aid}')
            assert del_resp.status_code == 200

            get_resp = await client.get(f'/api/v1/asignaciones/{aid}')
            assert get_resp.status_code == 404