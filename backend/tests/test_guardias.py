import uuid

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.core.security import create_access_token, hash_password
from app.main import create_app
from app.models.asignacion import Asignacion
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.guardia import EstadoGuardia, Guardia
from app.models.materia import Materia
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.slot_encuentro import DiaSemana
from app.models.tenant import Tenant
from app.models.user import User
from app.models.user_role import UserRole


@pytest_asyncio.fixture
async def setup_data(db_session):
    tid = uuid.uuid4()
    tenant = Tenant(id=tid, nombre='Test', codigo='TST-GUA', estado='Activo')
    db_session.add(tenant)
    await db_session.flush()

    materia = Materia(tenant_id=tid, codigo='MAT-GUA', nombre='Historia', estado='Activa')
    db_session.add(materia)
    carrera = Carrera(tenant_id=tid, codigo='TUPAD', nombre='TU Pad', estado='Activa')
    db_session.add(carrera)
    await db_session.flush()

    from datetime import date
    cohorte = Cohorte(tenant_id=tid, carrera_id=carrera.id, nombre='AGO-2025', anio=2025, vig_desde=date(2025, 1, 1))
    db_session.add(cohorte)
    await db_session.flush()

    tutor_user = User(tenant_id=tid, email='tutor-gua@t.com', password_hash=hash_password('pass'), roles=['TUTOR'])
    db_session.add(tutor_user)
    await db_session.flush()

    asignacion = Asignacion(
        tenant_id=tid, usuario_id=tutor_user.id,
        rol='TUTOR', materia_id=materia.id,
        carrera_id=carrera.id, cohorte_id=cohorte.id,
    )
    db_session.add(asignacion)

    role_tutor = Role(tenant_id=tid, name='TUTOR', codigo='TUTOR')
    db_session.add(role_tutor)
    await db_session.flush()

    p = Permission(tenant_id=tid, codigo='encuentros:gestionar', modulo='encuentros', accion='gestionar')
    db_session.add(p)
    await db_session.flush()
    db_session.add(RolePermission(tenant_id=tid, role_id=role_tutor.id, permiso_id=p.id))
    db_session.add(UserRole(tenant_id=tid, user_id=tutor_user.id, role_id=role_tutor.id))
    await db_session.flush()

    coord_user = User(tenant_id=tid, email='coord-gua@t.com', password_hash=hash_password('pass'), roles=['COORDINADOR'])
    db_session.add(coord_user)
    role_coord = Role(tenant_id=tid, name='COORDINADOR', codigo='COORDINADOR')
    db_session.add(role_coord)
    await db_session.flush()
    db_session.add(RolePermission(tenant_id=tid, role_id=role_coord.id, permiso_id=p.id))
    db_session.add(UserRole(tenant_id=tid, user_id=coord_user.id, role_id=role_coord.id))
    await db_session.flush()

    tutor_token = create_access_token(str(tutor_user.id), str(tid), ['TUTOR'])
    coord_token = create_access_token(str(coord_user.id), str(tid), ['COORDINADOR'])

    return {
        'tid': tid,
        'materia': materia,
        'carrera': carrera,
        'cohorte': cohorte,
        'asignacion': asignacion,
        'tutor_user': tutor_user,
        'coord_user': coord_user,
        'tutor_token': tutor_token,
        'coord_token': coord_token,
    }


class TestGuardia:
    async def _client(self, app, db_session, token):
        app.dependency_overrides[get_db] = lambda: db_session
        client = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        client.headers['Authorization'] = f'Bearer {token}'
        return client

    async def test_registrar_guardia_exitoso(self, app, db_session, setup_data):
        async with await self._client(app, db_session, setup_data['tutor_token']) as client:
            resp = await client.post('/api/v1/guardias', json={
                'asignacion_id': str(setup_data['asignacion'].id),
                'materia_id': str(setup_data['materia'].id),
                'carrera_id': str(setup_data['carrera'].id),
                'cohorte_id': str(setup_data['cohorte'].id),
                'dia': 'Lunes',
                'horario': '14:00-14:45',
            })
        assert resp.status_code == 201
        data = resp.json()
        assert data['estado'] == 'Pendiente'
        assert data['horario'] == '14:00-14:45'
        assert data['dia'] == 'Lunes'

    async def test_registrar_guardia_datos_faltantes_retorna_422(self, app, db_session, setup_data):
        async with await self._client(app, db_session, setup_data['tutor_token']) as client:
            resp = await client.post('/api/v1/guardias', json={
                'dia': 'Lunes',
                'horario': '10:00-11:00',
            })
        assert resp.status_code == 422

    async def test_consultar_guardias_coordinador_ve_todas(self, app, db_session, setup_data):
        db_session.add(Guardia(
            tenant_id=setup_data['tid'],
            asignacion_id=setup_data['asignacion'].id,
            materia_id=setup_data['materia'].id,
            carrera_id=setup_data['carrera'].id,
            cohorte_id=setup_data['cohorte'].id,
            dia=DiaSemana.LUNES,
            horario='09:00-10:00',
            estado=EstadoGuardia.PENDIENTE,
        ))
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['coord_token']) as client:
            resp = await client.get('/api/v1/guardias')
        assert resp.status_code == 200
        assert resp.json()['total'] >= 1

    async def test_consultar_guardias_tutor_ve_solo_suyas(self, app, db_session, setup_data):
        otro_tutor = User(tenant_id=setup_data['tid'], email='otro-tutor@t.com', password_hash='hash')
        db_session.add(otro_tutor)
        await db_session.flush()
        otra_asig = Asignacion(
            tenant_id=setup_data['tid'], usuario_id=otro_tutor.id,
            rol='TUTOR', materia_id=setup_data['materia'].id,
        )
        db_session.add(otra_asig)
        await db_session.flush()

        db_session.add(Guardia(
            tenant_id=setup_data['tid'],
            asignacion_id=otra_asig.id,
            materia_id=setup_data['materia'].id,
            dia=DiaSemana.MARTES,
            horario='10:00-11:00',
            estado=EstadoGuardia.PENDIENTE,
        ))
        db_session.add(Guardia(
            tenant_id=setup_data['tid'],
            asignacion_id=setup_data['asignacion'].id,
            materia_id=setup_data['materia'].id,
            dia=DiaSemana.MIERCOLES,
            horario='11:00-12:00',
            estado=EstadoGuardia.PENDIENTE,
        ))
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['tutor_token']) as client:
            resp = await client.get('/api/v1/guardias')
        assert resp.status_code == 200
        data = resp.json()
        assert data['total'] == 1

    async def test_exportar_guardias_csv(self, app, db_session, setup_data):
        db_session.add(Guardia(
            tenant_id=setup_data['tid'],
            asignacion_id=setup_data['asignacion'].id,
            materia_id=setup_data['materia'].id,
            carrera_id=setup_data['carrera'].id,
            cohorte_id=setup_data['cohorte'].id,
            dia=DiaSemana.VIERNES,
            horario='14:00-15:00',
            estado=EstadoGuardia.PENDIENTE,
        ))
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['coord_token']) as client:
            resp = await client.get('/api/v1/guardias/export')
        assert resp.status_code == 200
        assert 'text/csv' in resp.headers['content-type']
        assert 'id' in resp.text
        assert 'Viernes' in resp.text

    async def test_exportar_guardias_sin_resultados_csv_cabecera(self, app, db_session, setup_data):
        async with await self._client(app, db_session, setup_data['coord_token']) as client:
            resp = await client.get(
                f'/api/v1/guardias/export?materia_id={uuid.uuid4()}'
            )
        assert resp.status_code == 200
        lines = resp.text.strip().split('\n')
        assert len(lines) == 1
        assert lines[0] == 'id,tenant_id,asignacion_id,materia_id,carrera_id,cohorte_id,dia,horario,estado,comentarios,creada_at'

    async def test_actualizar_estado_guardia(self, app, db_session, setup_data):
        guardia = Guardia(
            tenant_id=setup_data['tid'],
            asignacion_id=setup_data['asignacion'].id,
            materia_id=setup_data['materia'].id,
            dia=DiaSemana.LUNES,
            horario='08:00-09:00',
            estado=EstadoGuardia.PENDIENTE,
        )
        db_session.add(guardia)
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['coord_token']) as client:
            resp = await client.patch(f'/api/v1/guardias/{guardia.id}', json={
                'estado': 'Realizada',
            })
        assert resp.status_code == 200
        assert resp.json()['estado'] == 'Realizada'

    async def test_permiso_401_sin_token(self, app, db_session, setup_data):
        client = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        resp = await client.get('/api/v1/guardias')
        assert resp.status_code == 401
