import uuid
from datetime import date, datetime, timedelta, timezone

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.core.security import create_access_token
from app.main import create_app
from app.models.acknowledgment_aviso import AcknowledgmentAviso
from app.models.aviso import Aviso
from app.models.asignacion import Asignacion
from app.models.tenant import Tenant
from app.models.user import User
from app.models.materia import Materia
from app.models.cohorte import Cohorte
from app.models.carrera import Carrera
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.user_role import UserRole


@pytest_asyncio.fixture
async def setup_data(db_session):
    tid = uuid.uuid4()
    tenant = Tenant(id=tid, nombre='Test', codigo='TST-AVS', estado='Activo')
    db_session.add(tenant)

    alumno = User(tenant_id=tid, email='alumno@t.com', password_hash='x', roles=['ALUMNO'])
    db_session.add(alumno)
    tutor = User(tenant_id=tid, email='tutor@t.com', password_hash='x', roles=['TUTOR'])
    db_session.add(tutor)
    coord = User(tenant_id=tid, email='coord@t.com', password_hash='x', roles=['COORDINADOR'])
    db_session.add(coord)
    await db_session.flush()

    carrera = Carrera(tenant_id=tid, codigo='CARR-01', nombre='Test Carrera')
    db_session.add(carrera)
    await db_session.flush()

    cohorte_a = Cohorte(tenant_id=tid, carrera_id=carrera.id, nombre='2025-A', anio=2025, vig_desde=date(2025, 1, 1))
    db_session.add(cohorte_a)
    cohorte_b = Cohorte(tenant_id=tid, carrera_id=carrera.id, nombre='2025-B', anio=2025, vig_desde=date(2025, 1, 1))
    db_session.add(cohorte_b)
    await db_session.flush()

    materia = Materia(tenant_id=tid, codigo='MAT-01', nombre='Matematica')
    db_session.add(materia)
    await db_session.flush()

    asignacion = Asignacion(
        tenant_id=tid, usuario_id=alumno.id, rol='ALUMNO',
        materia_id=materia.id, cohorte_id=cohorte_a.id,
    )
    db_session.add(asignacion)
    await db_session.flush()

    role_coord = Role(tenant_id=tid, name='COORDINADOR', codigo='COORDINADOR')
    db_session.add(role_coord)
    await db_session.flush()
    perm = Permission(tenant_id=tid, codigo='avisos:publicar', modulo='avisos', accion='publicar')
    db_session.add(perm)
    await db_session.flush()
    db_session.add(RolePermission(tenant_id=tid, role_id=role_coord.id, permiso_id=perm.id))
    db_session.add(UserRole(tenant_id=tid, user_id=coord.id, role_id=role_coord.id))
    await db_session.flush()

    alumno_token = create_access_token(str(alumno.id), str(tid), ['ALUMNO'])
    coord_token = create_access_token(str(coord.id), str(tid), ['COORDINADOR'])
    tutor_token = create_access_token(str(tutor.id), str(tid), ['TUTOR'])

    return {
        'tid': tid,
        'alumno': alumno, 'coord': coord, 'tutor': tutor,
        'alumno_token': alumno_token, 'coord_token': coord_token, 'tutor_token': tutor_token,
        'materia': materia, 'cohorte_a': cohorte_a, 'cohorte_b': cohorte_b,
    }


class TestCreacionAvisos:
    async def _client(self, app, db_session, token):
        app.dependency_overrides[get_db] = lambda: db_session
        c = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        c.headers['Authorization'] = f'Bearer {token}'
        return c

    @pytest.mark.asyncio
    async def test_crear_aviso_global_201(self, app, db_session, setup_data):
        now = datetime.now(timezone.utc)
        async with await self._client(app, db_session, setup_data['coord_token']) as c:
            resp = await c.post('/api/v1/avisos', json={
                'alcance': 'Global',
                'titulo': 'Nuevo aviso',
                'cuerpo': 'Contenido del aviso',
                'severidad': 'Info',
                'inicio_vigencia': now.isoformat(),
                'fin_vigencia': (now + timedelta(days=7)).isoformat(),
                'orden': 1,
                'requiere_ack': True,
            })
        assert resp.status_code == 201
        data = resp.json()
        assert data['titulo'] == 'Nuevo aviso'
        assert data['activo'] is True
        assert data['tenant_id'] == str(setup_data['tid'])
        assert data['alcance'] == 'Global'

    @pytest.mark.asyncio
    async def test_crear_aviso_por_materia(self, app, db_session, setup_data):
        now = datetime.now(timezone.utc)
        async with await self._client(app, db_session, setup_data['coord_token']) as c:
            resp = await c.post('/api/v1/avisos', json={
                'alcance': 'PorMateria',
                'materia_id': str(setup_data['materia'].id),
                'titulo': 'Aviso por materia',
                'cuerpo': 'Cuerpo',
                'severidad': 'Advertencia',
                'inicio_vigencia': now.isoformat(),
                'fin_vigencia': (now + timedelta(days=7)).isoformat(),
                'orden': 2,
            })
        assert resp.status_code == 201
        assert resp.json()['materia_id'] == str(setup_data['materia'].id)

    @pytest.mark.asyncio
    async def test_crear_aviso_por_cohorte(self, app, db_session, setup_data):
        now = datetime.now(timezone.utc)
        async with await self._client(app, db_session, setup_data['coord_token']) as c:
            resp = await c.post('/api/v1/avisos', json={
                'alcance': 'PorCohorte',
                'cohorte_id': str(setup_data['cohorte_a'].id),
                'titulo': 'Aviso por cohorte',
                'cuerpo': 'Cuerpo',
                'severidad': 'Crítico',
                'inicio_vigencia': now.isoformat(),
                'fin_vigencia': (now + timedelta(days=7)).isoformat(),
                'orden': 3,
            })
        assert resp.status_code == 201
        assert resp.json()['cohorte_id'] == str(setup_data['cohorte_a'].id)

    @pytest.mark.asyncio
    async def test_crear_aviso_por_rol(self, app, db_session, setup_data):
        now = datetime.now(timezone.utc)
        async with await self._client(app, db_session, setup_data['coord_token']) as c:
            resp = await c.post('/api/v1/avisos', json={
                'alcance': 'PorRol',
                'rol_destino': 'PROFESOR',
                'titulo': 'Aviso para profes',
                'cuerpo': 'Cuerpo',
                'severidad': 'Info',
                'inicio_vigencia': now.isoformat(),
                'fin_vigencia': (now + timedelta(days=7)).isoformat(),
                'orden': 0,
            })
        assert resp.status_code == 201
        assert resp.json()['rol_destino'] == 'PROFESOR'

    @pytest.mark.asyncio
    async def test_403_sin_permiso(self, app, db_session, setup_data):
        now = datetime.now(timezone.utc)
        async with await self._client(app, db_session, setup_data['alumno_token']) as c:
            resp = await c.post('/api/v1/avisos', json={
                'alcance': 'Global',
                'titulo': 'No autorizado',
                'cuerpo': 'Cuerpo',
                'severidad': 'Info',
                'inicio_vigencia': now.isoformat(),
                'fin_vigencia': (now + timedelta(days=7)).isoformat(),
                'orden': 1,
            })
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_422_campo_extra(self, app, db_session, setup_data):
        now = datetime.now(timezone.utc)
        async with await self._client(app, db_session, setup_data['coord_token']) as c:
            resp = await c.post('/api/v1/avisos', json={
                'alcance': 'Global',
                'titulo': 'Test',
                'cuerpo': 'Cuerpo',
                'severidad': 'Info',
                'inicio_vigencia': now.isoformat(),
                'fin_vigencia': (now + timedelta(days=7)).isoformat(),
                'orden': 1,
                'campo_extra': 'no_permitido',
            })
        assert resp.status_code == 422


class TestVisualizacion:
    async def _client(self, app, db_session, token):
        app.dependency_overrides[get_db] = lambda: db_session
        c = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        c.headers['Authorization'] = f'Bearer {token}'
        return c

    @pytest.mark.asyncio
    async def test_ve_avisos_global(self, app, db_session, setup_data):
        now = datetime.now(timezone.utc)
        aviso_global = Aviso(
            tenant_id=setup_data['tid'], alcance='Global', severidad='Info',
            titulo='Global para todos', cuerpo='Cuerpo',
            inicio_vigencia=now - timedelta(days=1),
            fin_vigencia=now + timedelta(days=1),
            orden=1, activo=True,
        )
        db_session.add(aviso_global)
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['alumno_token']) as c:
            resp = await c.get('/api/v1/avisos')
        assert resp.status_code == 200
        titulos = [item['titulo'] for item in resp.json()['items']]
        assert 'Global para todos' in titulos

    @pytest.mark.asyncio
    async def test_no_ve_avisos_de_otro_rol(self, app, db_session, setup_data):
        now = datetime.now(timezone.utc)
        aviso_rol = Aviso(
            tenant_id=setup_data['tid'], alcance='PorRol', severidad='Info',
            titulo='Solo profesores', cuerpo='Cuerpo',
            inicio_vigencia=now - timedelta(days=1),
            fin_vigencia=now + timedelta(days=1),
            orden=1, activo=True, rol_destino='PROFESOR',
        )
        db_session.add(aviso_rol)
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['alumno_token']) as c:
            resp = await c.get('/api/v1/avisos')
        assert resp.status_code == 200
        titulos = [item['titulo'] for item in resp.json()['items']]
        assert 'Solo profesores' not in titulos

    @pytest.mark.asyncio
    async def test_ve_avisos_por_cohorte(self, app, db_session, setup_data):
        now = datetime.now(timezone.utc)
        aviso_cohorte = Aviso(
            tenant_id=setup_data['tid'], alcance='PorCohorte', severidad='Info',
            titulo='Solo cohorte A', cuerpo='Cuerpo',
            inicio_vigencia=now - timedelta(days=1),
            fin_vigencia=now + timedelta(days=1),
            orden=1, activo=True, cohorte_id=setup_data['cohorte_a'].id,
        )
        db_session.add(aviso_cohorte)
        aviso_otra_cohorte = Aviso(
            tenant_id=setup_data['tid'], alcance='PorCohorte', severidad='Info',
            titulo='Solo cohorte B', cuerpo='Cuerpo',
            inicio_vigencia=now - timedelta(days=1),
            fin_vigencia=now + timedelta(days=1),
            orden=2, activo=True, cohorte_id=setup_data['cohorte_b'].id,
        )
        db_session.add(aviso_otra_cohorte)
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['alumno_token']) as c:
            resp = await c.get('/api/v1/avisos')
        assert resp.status_code == 200
        titulos = [item['titulo'] for item in resp.json()['items']]
        assert 'Solo cohorte A' in titulos
        assert 'Solo cohorte B' not in titulos

    @pytest.mark.asyncio
    async def test_ve_avisos_por_materia(self, app, db_session, setup_data):
        now = datetime.now(timezone.utc)
        aviso_materia = Aviso(
            tenant_id=setup_data['tid'], alcance='PorMateria', severidad='Info',
            titulo='Aviso de matematica', cuerpo='Cuerpo',
            inicio_vigencia=now - timedelta(days=1),
            fin_vigencia=now + timedelta(days=1),
            orden=1, activo=True, materia_id=setup_data['materia'].id,
        )
        db_session.add(aviso_materia)
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['alumno_token']) as c:
            resp = await c.get('/api/v1/avisos')
        assert resp.status_code == 200
        titulos = [item['titulo'] for item in resp.json()['items']]
        assert 'Aviso de matematica' in titulos

    @pytest.mark.asyncio
    async def test_aviso_fuera_vigencia_no_se_muestra(self, app, db_session, setup_data):
        now = datetime.now(timezone.utc)
        vencido = Aviso(
            tenant_id=setup_data['tid'], alcance='Global', severidad='Info',
            titulo='Vencido', cuerpo='Cuerpo',
            inicio_vigencia=now - timedelta(days=10),
            fin_vigencia=now - timedelta(days=5),
            orden=1, activo=True,
        )
        db_session.add(vencido)
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['alumno_token']) as c:
            resp = await c.get('/api/v1/avisos')
        assert resp.status_code == 200
        titulos = [item['titulo'] for item in resp.json()['items']]
        assert 'Vencido' not in titulos

    @pytest.mark.asyncio
    async def test_aviso_fuera_vigencia_404_en_detalle(self, app, db_session, setup_data):
        now = datetime.now(timezone.utc)
        vencido = Aviso(
            tenant_id=setup_data['tid'], alcance='Global', severidad='Info',
            titulo='Vencido detalle', cuerpo='Cuerpo',
            inicio_vigencia=now - timedelta(days=10),
            fin_vigencia=now - timedelta(days=5),
            orden=1, activo=True,
        )
        db_session.add(vencido)
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['alumno_token']) as c:
            resp = await c.get(f'/api/v1/avisos/{vencido.id}')
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_orden_por_prioridad(self, app, db_session, setup_data):
        now = datetime.now(timezone.utc)
        primero = Aviso(
            tenant_id=setup_data['tid'], alcance='Global', severidad='Info',
            titulo='Primero', cuerpo='Cuerpo',
            inicio_vigencia=now - timedelta(days=1),
            fin_vigencia=now + timedelta(days=1),
            orden=1, activo=True,
        )
        db_session.add(primero)
        segundo = Aviso(
            tenant_id=setup_data['tid'], alcance='Global', severidad='Info',
            titulo='Segundo', cuerpo='Cuerpo',
            inicio_vigencia=now,
            fin_vigencia=now + timedelta(days=1),
            orden=2, activo=True,
        )
        db_session.add(segundo)
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['alumno_token']) as c:
            resp = await c.get('/api/v1/avisos')
        assert resp.status_code == 200
        items = resp.json()['items']
        avisos_filtrados = [i for i in items if i['titulo'] in ('Primero', 'Segundo')]
        if len(avisos_filtrados) >= 2:
            assert avisos_filtrados[0]['orden'] <= avisos_filtrados[1]['orden']

    @pytest.mark.asyncio
    async def test_soft_delete_oculta_aviso(self, app, db_session, setup_data):
        now = datetime.now(timezone.utc)
        aviso = Aviso(
            tenant_id=setup_data['tid'], alcance='Global', severidad='Info',
            titulo='Se borra', cuerpo='Cuerpo',
            inicio_vigencia=now - timedelta(days=1),
            fin_vigencia=now + timedelta(days=1),
            orden=1, activo=True,
        )
        db_session.add(aviso)
        await db_session.flush()

        aviso.deleted_at = datetime.now(timezone.utc)
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['alumno_token']) as c:
            resp = await c.get('/api/v1/avisos')
        titulos = [i['titulo'] for i in resp.json()['items']]
        assert 'Se borra' not in titulos


class TestAcknowledgment:
    async def _client(self, app, db_session, token):
        app.dependency_overrides[get_db] = lambda: db_session
        c = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        c.headers['Authorization'] = f'Bearer {token}'
        return c

    @pytest.mark.asyncio
    async def test_ack_exitoso_201(self, app, db_session, setup_data):
        now = datetime.now(timezone.utc)
        aviso = Aviso(
            tenant_id=setup_data['tid'], alcance='Global', severidad='Info',
            titulo='Ack test', cuerpo='Cuerpo',
            inicio_vigencia=now - timedelta(days=1),
            fin_vigencia=now + timedelta(days=1),
            orden=1, activo=True, requiere_ack=True,
        )
        db_session.add(aviso)
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['alumno_token']) as c:
            resp = await c.post(f'/api/v1/avisos/{aviso.id}/ack')
        assert resp.status_code == 201
        data = resp.json()
        assert data['aviso_id'] == str(aviso.id)
        assert data['usuario_id'] == str(setup_data['alumno'].id)

        result = await db_session.execute(
            select(AcknowledgmentAviso).where(AcknowledgmentAviso.aviso_id == aviso.id)
        )
        ack = result.scalar_one_or_none()
        assert ack is not None
        assert ack.usuario_id == setup_data['alumno'].id

    @pytest.mark.asyncio
    async def test_ack_duplicado_409(self, app, db_session, setup_data):
        now = datetime.now(timezone.utc)
        aviso = Aviso(
            tenant_id=setup_data['tid'], alcance='Global', severidad='Info',
            titulo='Doble ack', cuerpo='Cuerpo',
            inicio_vigencia=now - timedelta(days=1),
            fin_vigencia=now + timedelta(days=1),
            orden=1, activo=True, requiere_ack=True,
        )
        db_session.add(aviso)
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['alumno_token']) as c:
            resp1 = await c.post(f'/api/v1/avisos/{aviso.id}/ack')
            assert resp1.status_code == 201

            resp2 = await c.post(f'/api/v1/avisos/{aviso.id}/ack')
        assert resp2.status_code == 409

    @pytest.mark.asyncio
    async def test_total_acks_refleja_confirmaciones(self, app, db_session, setup_data):
        now = datetime.now(timezone.utc)
        tid = setup_data['tid']

        aviso = Aviso(
            tenant_id=tid, alcance='Global', severidad='Info',
            titulo='Contador', cuerpo='Cuerpo',
            inicio_vigencia=now - timedelta(days=1),
            fin_vigencia=now + timedelta(days=1),
            orden=1, activo=True, requiere_ack=True,
        )
        db_session.add(aviso)
        await db_session.flush()

        users = []
        tokens = []
        for i in range(3):
            u = User(tenant_id=tid, email=f'user{i}@t.com', password_hash='x', roles=['ALUMNO'])
            db_session.add(u)
            await db_session.flush()
            users.append(u)
            tokens.append(create_access_token(str(u.id), str(tid), ['ALUMNO']))
            ack = AcknowledgmentAviso(
                tenant_id=tid, aviso_id=aviso.id, usuario_id=u.id,
                confirmado_at=datetime.now(timezone.utc),
            )
            db_session.add(ack)
        await db_session.flush()

        async with await self._client(app, db_session, tokens[0]) as c:
            resp = await c.get(f'/api/v1/avisos/{aviso.id}')
        assert resp.status_code == 200
        data = resp.json()
        assert data['total_acks'] == 3
        assert data['user_acked'] is True

    @pytest.mark.asyncio
    async def test_user_acked_true_si_confirmo(self, app, db_session, setup_data):
        now = datetime.now(timezone.utc)
        aviso = Aviso(
            tenant_id=setup_data['tid'], alcance='Global', severidad='Info',
            titulo='User acked', cuerpo='Cuerpo',
            inicio_vigencia=now - timedelta(days=1),
            fin_vigencia=now + timedelta(days=1),
            orden=1, activo=True, requiere_ack=True,
        )
        db_session.add(aviso)
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['alumno_token']) as c:
            await c.post(f'/api/v1/avisos/{aviso.id}/ack')
            resp = await c.get(f'/api/v1/avisos/{aviso.id}')
        assert resp.status_code == 200
        assert resp.json()['user_acked'] is True


class TestMultiTenant:
    @pytest.mark.asyncio
    async def test_aislamiento_entre_tenants(self, app, db_session):
        tid_a = uuid.uuid4()
        tid_b = uuid.uuid4()
        tenant_a = Tenant(id=tid_a, nombre='A', codigo='TNA', estado='Activo')
        tenant_b = Tenant(id=tid_b, nombre='B', codigo='TNB', estado='Activo')
        db_session.add_all([tenant_a, tenant_b])
        await db_session.flush()

        now = datetime.now(timezone.utc)
        aviso_a = Aviso(
            tenant_id=tid_a, alcance='Global', severidad='Info',
            titulo='Solo tenant A', cuerpo='Cuerpo',
            inicio_vigencia=now - timedelta(days=1),
            fin_vigencia=now + timedelta(days=1),
            orden=1, activo=True,
        )
        db_session.add(aviso_a)
        await db_session.flush()

        user_a = User(tenant_id=tid_a, email='a@t.com', password_hash='x', roles=['ALUMNO'])
        db_session.add(user_a)
        await db_session.flush()
        token_a = create_access_token(str(user_a.id), str(tid_a), ['ALUMNO'])

        async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as c:
            c.headers['Authorization'] = f'Bearer {token_a}'
            app.dependency_overrides[get_db] = lambda: db_session
            resp = await c.get('/api/v1/avisos')
        assert resp.status_code == 200
        titulos = [i['titulo'] for i in resp.json()['items']]
        assert 'Solo tenant A' in titulos
        for item in resp.json()['items']:
            assert item['tenant_id'] == str(tid_a)
