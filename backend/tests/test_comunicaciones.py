import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session_factory
from app.core.dependencies import get_db
from app.core.security import create_access_token, decrypt, encrypt, hash_password
from app.main import create_app
from app.models.comunicacion import Comunicacion, EstadoComunicacion
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.materia import Materia
from app.models.tenant import Tenant
from app.models.user import User
from app.models.user_role import UserRole


@pytest_asyncio.fixture
async def admin_token(db_session):
    tid = uuid.uuid4()
    tenant = Tenant(id=tid, nombre='Test', codigo='TST-COM', estado='Activo', aprobacion_comunicaciones=False)
    db_session.add(tenant)
    await db_session.flush()

    user = User(tenant_id=tid, email='admin-com@t.com', password_hash=hash_password('pass'), roles=['ADMIN'])
    role_admin = Role(tenant_id=tid, name='ADMIN', codigo='ADMIN')
    db_session.add_all([user, role_admin])
    await db_session.flush()

    for codigo in ['comunicacion:enviar', 'comunicacion:aprobar']:
        p = Permission(
            tenant_id=tid, codigo=codigo,
            modulo=codigo.split(':')[0], accion=codigo.split(':')[1],
        )
        db_session.add(p)
        await db_session.flush()
        db_session.add(RolePermission(tenant_id=tid, role_id=role_admin.id, permiso_id=p.id))

    db_session.add(UserRole(tenant_id=tid, user_id=user.id, role_id=role_admin.id))
    await db_session.flush()

    token = create_access_token(str(user.id), str(tid), ['ADMIN'])
    return {'token': token, 'tid': tid, 'tenant': tenant, 'user': user}


@pytest_asyncio.fixture
async def alumno_token(db_session):
    tid = uuid.uuid4()
    tenant = Tenant(id=tid, nombre='Test', codigo='TST-COM2', estado='Activo')
    db_session.add(tenant)
    await db_session.flush()

    user = User(tenant_id=tid, email='alumno-com@t.com', password_hash=hash_password('pass'), roles=['ALUMNO'])
    role_alumno = Role(tenant_id=tid, name='ALUMNO', codigo='ALUMNO')
    db_session.add_all([user, role_alumno])
    await db_session.flush()

    db_session.add(UserRole(tenant_id=tid, user_id=user.id, role_id=role_alumno.id))
    await db_session.flush()

    token = create_access_token(str(user.id), str(tid), ['ALUMNO'])
    return {'token': token, 'tid': tid, 'user': user}


class TestComunicacionModel:
    async def test_create_comunicacion(self, db_session: AsyncSession):
        tid = uuid.uuid4()
        tenant = Tenant(id=tid, nombre='Test', codigo='MODEL', estado='Activo')
        db_session.add(tenant)
        user = User(tenant_id=tid, email='u@t.com', password_hash='hash')
        db_session.add(user)
        await db_session.flush()

        lote_id = uuid.uuid4()
        c = Comunicacion(
            tenant_id=tid, enviado_por=user.id,
            destinatario=encrypt('a@b.com'),
            asunto='Test', cuerpo='Body',
            estado=EstadoComunicacion.PENDIENTE, lote_id=lote_id,
        )
        db_session.add(c)
        await db_session.commit()
        await db_session.refresh(c)

        assert c.id is not None
        assert c.estado == EstadoComunicacion.PENDIENTE
        assert decrypt(c.destinatario) == 'a@b.com'

    async def test_maquina_estados(self, db_session: AsyncSession):
        tid = uuid.uuid4()
        tenant = Tenant(id=tid, nombre='T', codigo='EST', estado='Activo')
        db_session.add(tenant)
        user = User(tenant_id=tid, email='u2@t.com', password_hash='hash')
        db_session.add(user)
        await db_session.flush()

        c = Comunicacion(
            tenant_id=tid, enviado_por=user.id,
            destinatario=encrypt('x@y.com'),
            asunto='E', cuerpo='B',
            estado=EstadoComunicacion.PENDIENTE, lote_id=uuid.uuid4(),
        )
        db_session.add(c)
        await db_session.flush()

        assert c.estado == EstadoComunicacion.PENDIENTE
        c.estado = EstadoComunicacion.ENVIANDO
        await db_session.flush()
        assert c.estado == EstadoComunicacion.ENVIANDO
        c.estado = EstadoComunicacion.ENVIADO
        await db_session.flush()
        assert c.estado == EstadoComunicacion.ENVIADO

    async def test_append_only(self, db_session: AsyncSession):
        tid = uuid.uuid4()
        tenant = Tenant(id=tid, nombre='T', codigo='APP', estado='Activo')
        db_session.add(tenant)
        await db_session.flush()
        c = Comunicacion(
            tenant_id=tid, destinatario=encrypt('x@y.com'),
            asunto='A', cuerpo='B',
            estado=EstadoComunicacion.PENDIENTE, lote_id=uuid.uuid4(),
        )
        db_session.add(c)
        await db_session.flush()
        assert c.deleted_at is None


class TestPreview:
    async def _client(self, app, db_session, token):
        app.dependency_overrides[get_db] = lambda: db_session
        client = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        client.headers['Authorization'] = f'Bearer {token}'
        return client

    async def test_con_variables(self, app, db_session, admin_token):
        async with await self._client(app, db_session, admin_token['token']) as client:
            resp = await client.post('/api/v1/comunicaciones/preview', json={
                'destinatario': 'a@b.com',
                'asunto': 'Hola {{alumno.nombre}}',
                'cuerpo': 'Materia {{materia.nombre}}',
                'variables': {'alumno.nombre': 'Juan', 'materia.nombre': 'Mate'},
            })
        assert resp.status_code == 200
        d = resp.json()
        assert d['asunto_renderizado'] == 'Hola Juan'
        assert d['cuerpo_renderizado'] == 'Materia Mate'
        assert d['variables_no_encontradas'] == []

    async def test_variable_no_encontrada(self, app, db_session, admin_token):
        async with await self._client(app, db_session, admin_token['token']) as client:
            resp = await client.post('/api/v1/comunicaciones/preview', json={
                'destinatario': 'a@b.com',
                'asunto': '{{x}}',
                'cuerpo': '{{y}}',
                'variables': {'x': 'OK'},
            })
        assert resp.status_code == 200
        assert 'y' in resp.json()['variables_no_encontradas']

    async def test_sin_crear_registro(self, app, db_session, admin_token):
        async with await self._client(app, db_session, admin_token['token']) as client:
            resp = await client.post('/api/v1/comunicaciones/preview', json={
                'destinatario': 'a@b.com',
                'asunto': 'Test',
                'cuerpo': 'Body',
            })
        assert resp.status_code == 200
        result = await db_session.execute(select(Comunicacion))
        assert result.scalar_one_or_none() is None


class TestEncolar:
    async def _client(self, app, db_session, token):
        app.dependency_overrides[get_db] = lambda: db_session
        client = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        client.headers['Authorization'] = f'Bearer {token}'
        return client

    async def test_encolar_cifra_destinatario(self, app, db_session, admin_token):
        async with await self._client(app, db_session, admin_token['token']) as client:
            resp = await client.post('/api/v1/comunicaciones', json={
                'destinatario': 'alumno@test.com',
                'asunto': 'Bienvenido',
                'cuerpo': 'Texto del cuerpo',
            })
        assert resp.status_code == 201
        data = resp.json()
        assert data['estado'] == 'Pendiente'
        assert data['destinatario'] != 'alumno@test.com'

        result = await db_session.execute(select(Comunicacion).where(Comunicacion.id == uuid.UUID(data['id'])))
        c = result.scalar_one()
        assert decrypt(c.destinatario) == 'alumno@test.com'

    async def test_encolar_lote(self, app, db_session, admin_token):
        async with await self._client(app, db_session, admin_token['token']) as client:
            resp = await client.post('/api/v1/comunicaciones/lote', json={
                'destinatarios': ['a@b.com', 'c@d.com'],
                'asunto': 'Lote test',
                'cuerpo': 'Cuerpo lote',
            })
        assert resp.status_code == 201
        data = resp.json()
        assert len(data) == 2
        assert data[0]['lote_id'] == data[1]['lote_id']

    async def test_encolar_sin_permiso_403(self, app, db_session, alumno_token):
        async with await self._client(app, db_session, alumno_token['token']) as client:
            resp = await client.post('/api/v1/comunicaciones', json={
                'destinatario': 'a@b.com',
                'asunto': 'Test',
                'cuerpo': 'Body',
            })
        assert resp.status_code == 403


class TestAprobacion:
    async def _client(self, app, db_session, token):
        app.dependency_overrides[get_db] = lambda: db_session
        client = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        client.headers['Authorization'] = f'Bearer {token}'
        return client

    async def test_aprobar_lote(self, app, db_session, admin_token):
        tid = admin_token['tid']
        admin_token['tenant'].aprobacion_comunicaciones = True
        await db_session.flush()

        async with await self._client(app, db_session, admin_token['token']) as client:
            resp = await client.post('/api/v1/comunicaciones', json={
                'destinatario': 'a@b.com',
                'asunto': 'Requiere aprob',
                'cuerpo': 'Test',
            })
        assert resp.status_code == 201
        data = resp.json()
        assert data['aprobacion_requerida'] is True

        async with await self._client(app, db_session, admin_token['token']) as client:
            resp = await client.post('/api/v1/comunicaciones/aprobar-lote', json={
                'lote_id': data['lote_id'],
                'accion': 'aprobar',
            })
        assert resp.status_code == 200

    async def test_rechazar_lote(self, app, db_session, admin_token):
        admin_token['tenant'].aprobacion_comunicaciones = True
        await db_session.flush()

        async with await self._client(app, db_session, admin_token['token']) as client:
            resp = await client.post('/api/v1/comunicaciones', json={
                'destinatario': 'a@b.com',
                'asunto': 'Test',
                'cuerpo': 'Body',
            })
            lote_id = resp.json()['lote_id']

            resp = await client.post('/api/v1/comunicaciones/aprobar-lote', json={
                'lote_id': lote_id,
                'accion': 'rechazar',
            })
        assert resp.status_code == 200

        result = await db_session.execute(
            select(Comunicacion).where(Comunicacion.lote_id == uuid.UUID(lote_id))
        )
        for c in result.scalars().all():
            assert c.estado == EstadoComunicacion.CANCELADO

    async def test_aprobar_sin_permiso_403(self, app, db_session, alumno_token):
        async with await self._client(app, db_session, alumno_token['token']) as client:
            resp = await client.post('/api/v1/comunicaciones/aprobar-lote', json={
                'lote_id': str(uuid.uuid4()),
                'accion': 'aprobar',
            })
        assert resp.status_code == 403

    async def test_tenant_sin_aprobacion(self, app, db_session, admin_token):
        async with await self._client(app, db_session, admin_token['token']) as client:
            resp = await client.post('/api/v1/comunicaciones', json={
                'destinatario': 'a@b.com',
                'asunto': 'Sin aprob',
                'cuerpo': 'Body',
            })
        assert resp.status_code == 201
        assert resp.json()['aprobacion_requerida'] is False


class TestCancelar:
    async def _client(self, app, db_session, token):
        app.dependency_overrides[get_db] = lambda: db_session
        client = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        client.headers['Authorization'] = f'Bearer {token}'
        return client

    async def test_cancelar_pendiente(self, app, db_session, admin_token):
        async with await self._client(app, db_session, admin_token['token']) as client:
            resp = await client.post('/api/v1/comunicaciones', json={
                'destinatario': 'a@b.com',
                'asunto': 'Cancelable',
                'cuerpo': 'Body',
            })
            c_id = resp.json()['id']
            resp = await client.post(f'/api/v1/comunicaciones/{c_id}/cancelar')
        assert resp.status_code == 200

    async def test_cancelar_enviando_error(self, app, db_session, admin_token):
        c = Comunicacion(
            tenant_id=admin_token['tid'],
            destinatario=encrypt('a@b.com'),
            asunto='En curso', cuerpo='Body',
            estado=EstadoComunicacion.ENVIANDO,
            lote_id=uuid.uuid4(),
        )
        db_session.add(c)
        await db_session.flush()

        async with await self._client(app, db_session, admin_token['token']) as client:
            resp = await client.post(f'/api/v1/comunicaciones/{c.id}/cancelar')
        assert resp.status_code == 400


class TestListar:
    async def _client(self, app, db_session, token):
        app.dependency_overrides[get_db] = lambda: db_session
        client = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        client.headers['Authorization'] = f'Bearer {token}'
        return client

    async def test_listar_por_lote(self, app, db_session, admin_token):
        lote_id = uuid.uuid4()
        for email in ['a@b.com', 'c@d.com']:
            db_session.add(Comunicacion(
                tenant_id=admin_token['tid'],
                destinatario=encrypt(email),
                asunto='L', cuerpo='B',
                estado=EstadoComunicacion.PENDIENTE,
                lote_id=lote_id,
            ))
        await db_session.flush()

        async with await self._client(app, db_session, admin_token['token']) as client:
            resp = await client.get(f'/api/v1/comunicaciones?lote_id={lote_id}')
        assert resp.status_code == 200
        assert resp.json()['total'] == 2

    async def test_listar_por_materia(self, app, db_session, admin_token):
        materia = Materia(
            tenant_id=admin_token['tid'],
            codigo='MAT-COM',
            nombre='Mat Comunicacion',
            estado='Activa',
        )
        db_session.add(materia)
        await db_session.flush()

        db_session.add(Comunicacion(
            tenant_id=admin_token['tid'],
            destinatario=encrypt('a@b.com'),
            asunto='X', cuerpo='Y',
            estado=EstadoComunicacion.PENDIENTE,
            lote_id=uuid.uuid4(),
            materia_id=materia.id,
        ))
        await db_session.flush()

        async with await self._client(app, db_session, admin_token['token']) as client:
            resp = await client.get(f'/api/v1/comunicaciones?materia_id={materia.id}')
        assert resp.status_code == 200
        assert resp.json()['total'] == 1


class TestWorker:
    async def test_worker_procesa_pendiente(self, db_session: AsyncSession):
        tid = uuid.uuid4()
        tenant = Tenant(id=tid, nombre='T', codigo='WK', estado='Activo')
        db_session.add(tenant)
        user = User(tenant_id=tid, email='w@k.com', password_hash='hash')
        db_session.add(user)
        await db_session.flush()

        c = Comunicacion(
            tenant_id=tid, destinatario=encrypt('a@b.com'),
            asunto='W', cuerpo='B',
            estado=EstadoComunicacion.PENDIENTE, lote_id=uuid.uuid4(),
        )
        db_session.add(c)
        await db_session.commit()

        from app.workers.main import _process_batch
        processed = await _process_batch(db_session)
        await db_session.flush()
        assert processed == 1

        await db_session.refresh(c)
        assert c.estado == EstadoComunicacion.ENVIADO

    async def test_worker_salta_sin_pendientes(self, db_session: AsyncSession):
        from app.workers.main import _process_batch
        processed = await _process_batch(db_session)
        assert processed == 0
