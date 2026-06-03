import uuid
from datetime import date

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.core.security import create_access_token, hash_password
from app.main import create_app
from app.models.asignacion import Asignacion
from app.models.instancia_encuentro import EstadoInstancia, InstanciaEncuentro
from app.models.materia import Materia
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.slot_encuentro import DiaSemana, SlotEncuentro
from app.models.tenant import Tenant
from app.models.user import User
from app.models.user_role import UserRole


@pytest_asyncio.fixture
async def setup_data(db_session):
    tid = uuid.uuid4()
    tenant = Tenant(id=tid, nombre='Test', codigo='TST-ENC', estado='Activo')
    db_session.add(tenant)
    await db_session.flush()

    materia = Materia(tenant_id=tid, codigo='MAT-ENC', nombre='Matematicas', estado='Activa')
    db_session.add(materia)
    await db_session.flush()

    prof_user = User(tenant_id=tid, email='prof-enc@t.com', password_hash=hash_password('pass'), roles=['PROFESOR'])
    db_session.add(prof_user)
    await db_session.flush()

    asignacion = Asignacion(
        tenant_id=tid, usuario_id=prof_user.id,
        rol='PROFESOR', materia_id=materia.id,
    )
    db_session.add(asignacion)

    role_prof = Role(tenant_id=tid, name='PROFESOR', codigo='PROFESOR')
    db_session.add(role_prof)
    await db_session.flush()

    p = Permission(tenant_id=tid, codigo='encuentros:gestionar', modulo='encuentros', accion='gestionar')
    db_session.add(p)
    await db_session.flush()
    db_session.add(RolePermission(tenant_id=tid, role_id=role_prof.id, permiso_id=p.id))
    db_session.add(UserRole(tenant_id=tid, user_id=prof_user.id, role_id=role_prof.id))
    await db_session.flush()

    coord_user = User(tenant_id=tid, email='coord-enc@t.com', password_hash=hash_password('pass'), roles=['COORDINADOR'])
    db_session.add(coord_user)
    role_coord = Role(tenant_id=tid, name='COORDINADOR', codigo='COORDINADOR')
    db_session.add(role_coord)
    await db_session.flush()
    db_session.add(RolePermission(tenant_id=tid, role_id=role_coord.id, permiso_id=p.id))
    db_session.add(UserRole(tenant_id=tid, user_id=coord_user.id, role_id=role_coord.id))
    await db_session.flush()

    prof_token = create_access_token(str(prof_user.id), str(tid), ['PROFESOR'])
    coord_token = create_access_token(str(coord_user.id), str(tid), ['COORDINADOR'])

    return {
        'tid': tid,
        'materia': materia,
        'asignacion': asignacion,
        'prof_user': prof_user,
        'coord_user': coord_user,
        'prof_token': prof_token,
        'coord_token': coord_token,
    }


class TestSlotEncuentro:
    async def _client(self, app, db_session, token):
        app.dependency_overrides[get_db] = lambda: db_session
        client = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        client.headers['Authorization'] = f'Bearer {token}'
        return client

    async def test_crear_slot_recurrente_genera_instancias(self, app, db_session, setup_data):
        async with await self._client(app, db_session, setup_data['prof_token']) as client:
            resp = await client.post('/api/v1/encuentros/slots', json={
                'asignacion_id': str(setup_data['asignacion'].id),
                'materia_id': str(setup_data['materia'].id),
                'titulo': 'Clase Semanal',
                'hora': '18:00',
                'dia_semana': 'Lunes',
                'fecha_inicio': '2026-03-02',
                'cant_semanas': 4,
            })
        assert resp.status_code == 201
        data = resp.json()
        assert data['titulo'] == 'Clase Semanal'
        assert data['cant_semanas'] == 4

        result = await db_session.execute(
            select(InstanciaEncuentro).where(InstanciaEncuentro.slot_id == uuid.UUID(data['id']))
        )
        instancias = result.scalars().all()
        assert len(instancias) == 4
        fechas = [i.fecha.isoformat() for i in instancias]
        assert '2026-03-02' in fechas
        assert '2026-03-09' in fechas
        assert '2026-03-16' in fechas
        assert '2026-03-23' in fechas
        for i in instancias:
            assert i.estado == EstadoInstancia.PROGRAMADO
            assert i.hora == '18:00'

    async def test_crear_slot_sin_instancias(self, app, db_session, setup_data):
        async with await self._client(app, db_session, setup_data['prof_token']) as client:
            resp = await client.post('/api/v1/encuentros/slots', json={
                'asignacion_id': str(setup_data['asignacion'].id),
                'materia_id': str(setup_data['materia'].id),
                'titulo': 'Slot Sin Instancias',
                'hora': '10:00',
                'dia_semana': 'Martes',
                'fecha_inicio': '2026-04-01',
                'cant_semanas': 0,
            })
        assert resp.status_code == 201
        data = resp.json()

        result = await db_session.execute(
            select(InstanciaEncuentro).where(InstanciaEncuentro.slot_id == uuid.UUID(data['id']))
        )
        instancias = result.scalars().all()
        assert len(instancias) == 0

    async def test_crear_slot_dia_invalido_retorna_422(self, app, db_session, setup_data):
        async with await self._client(app, db_session, setup_data['prof_token']) as client:
            resp = await client.post('/api/v1/encuentros/slots', json={
                'asignacion_id': str(setup_data['asignacion'].id),
                'materia_id': str(setup_data['materia'].id),
                'titulo': 'Invalido',
                'hora': '10:00',
                'dia_semana': 'INVALIDO',
                'fecha_inicio': '2026-04-01',
                'cant_semanas': 1,
            })
        assert resp.status_code == 422

    async def test_listar_slots(self, app, db_session, setup_data):
        async with await self._client(app, db_session, setup_data['prof_token']) as client:
            resp = await client.get(f'/api/v1/encuentros/slots?materia_id={setup_data["materia"].id}')
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data['items'], list)


class TestInstanciaEncuentro:
    async def _client(self, app, db_session, token):
        app.dependency_overrides[get_db] = lambda: db_session
        client = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        client.headers['Authorization'] = f'Bearer {token}'
        return client

    async def test_crear_encuentro_unico(self, app, db_session, setup_data):
        async with await self._client(app, db_session, setup_data['prof_token']) as client:
            resp = await client.post('/api/v1/encuentros/instancias', json={
                'materia_id': str(setup_data['materia'].id),
                'fecha': '2026-04-15',
                'hora': '10:00',
                'titulo': 'Clase consulta',
            })
        assert resp.status_code == 201
        data = resp.json()
        assert data['titulo'] == 'Clase consulta'
        assert data['slot_id'] is None
        assert data['estado'] == 'Programado'

    async def test_editar_instancia_estado_realizado(self, app, db_session, setup_data):
        instancia = InstanciaEncuentro(
            tenant_id=setup_data['tid'],
            materia_id=setup_data['materia'].id,
            fecha=date(2026, 5, 1),
            hora='14:00',
            titulo='Parcial',
            estado=EstadoInstancia.PROGRAMADO,
        )
        db_session.add(instancia)
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['prof_token']) as client:
            resp = await client.patch(f'/api/v1/encuentros/instancias/{instancia.id}', json={
                'estado': 'Realizado',
            })
        assert resp.status_code == 200
        data = resp.json()
        assert data['estado'] == 'Realizado'

    async def test_editar_instancia_video_url(self, app, db_session, setup_data):
        instancia = InstanciaEncuentro(
            tenant_id=setup_data['tid'],
            materia_id=setup_data['materia'].id,
            fecha=date(2026, 5, 2),
            hora='15:00',
            titulo='Clase grabada',
            estado=EstadoInstancia.PROGRAMADO,
        )
        db_session.add(instancia)
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['prof_token']) as client:
            resp = await client.patch(f'/api/v1/encuentros/instancias/{instancia.id}', json={
                'estado': 'Realizado',
                'video_url': 'https://vimeo.com/123',
            })
        assert resp.status_code == 200
        assert resp.json()['video_url'] == 'https://vimeo.com/123'

    async def test_editar_instancia_inexistente_retorna_404(self, app, db_session, setup_data):
        fake_id = str(uuid.uuid4())
        async with await self._client(app, db_session, setup_data['prof_token']) as client:
            resp = await client.patch(f'/api/v1/encuentros/instancias/{fake_id}', json={
                'estado': 'Realizado',
            })
        assert resp.status_code == 404

    async def test_generar_html_con_encuentros(self, app, db_session, setup_data):
        for i in range(3):
            db_session.add(InstanciaEncuentro(
                tenant_id=setup_data['tid'],
                materia_id=setup_data['materia'].id,
                fecha=date(2026, 6, 1 + i),
                hora='10:00',
                titulo=f'Clase {i+1}',
                estado=EstadoInstancia.PROGRAMADO,
            ))
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['prof_token']) as client:
            resp = await client.get(
                f'/api/v1/encuentros/instancias?materia_id={setup_data["materia"].id}&html=true'
            )
        assert resp.status_code == 200
        html = resp.text
        assert '<table' in html
        assert 'Clase 1' in html
        assert 'Clase 2' in html
        assert 'Clase 3' in html

    async def test_generar_html_sin_encuentros(self, app, db_session, setup_data):
        async with await self._client(app, db_session, setup_data['prof_token']) as client:
            resp = await client.get(
                f'/api/v1/encuentros/instancias?materia_id={setup_data["materia"].id}&html=true'
            )
        assert resp.status_code == 200
        assert '<p>No hay encuentros programados.</p>' in resp.text

    async def test_vista_global_coordinador_ve_todo(self, app, db_session, setup_data):
        db_session.add(InstanciaEncuentro(
            tenant_id=setup_data['tid'],
            materia_id=setup_data['materia'].id,
            fecha=date(2026, 7, 1),
            hora='09:00',
            titulo='Coord test',
            estado=EstadoInstancia.PROGRAMADO,
        ))
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['coord_token']) as client:
            resp = await client.get('/api/v1/encuentros/instancias')
        assert resp.status_code == 200
        assert resp.json()['total'] >= 1

    async def test_vista_global_profesor_ve_solo_sus_materias(self, app, db_session, setup_data):
        otra_materia = Materia(
            tenant_id=setup_data['tid'],
            codigo='OTRA-ENC',
            nombre='Otra Materia',
            estado='Activa',
        )
        db_session.add(otra_materia)
        await db_session.flush()

        db_session.add(InstanciaEncuentro(
            tenant_id=setup_data['tid'],
            materia_id=otra_materia.id,
            fecha=date(2026, 8, 1),
            hora='11:00',
            titulo='No deberia ver',
            estado=EstadoInstancia.PROGRAMADO,
        ))
        db_session.add(InstanciaEncuentro(
            tenant_id=setup_data['tid'],
            materia_id=setup_data['materia'].id,
            fecha=date(2026, 8, 2),
            hora='12:00',
            titulo='Si deberia ver',
            estado=EstadoInstancia.PROGRAMADO,
        ))
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['prof_token']) as client:
            resp = await client.get('/api/v1/encuentros/instancias')
        assert resp.status_code == 200
        data = resp.json()
        assert data['total'] == 1
        assert data['items'][0]['titulo'] == 'Si deberia ver'

    async def test_permiso_401_sin_token(self, app, db_session, setup_data):
        client = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        resp = await client.get('/api/v1/encuentros/instancias')
        assert resp.status_code == 401
