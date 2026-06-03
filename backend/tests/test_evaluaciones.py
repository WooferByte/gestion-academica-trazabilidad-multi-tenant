import uuid
from datetime import date

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.core.security import create_access_token, hash_password
from app.main import create_app
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.coloquio_alumno import ColoquioAlumno
from app.models.evaluacion import EstadoEvaluacion, Evaluacion, TipoEvaluacion
from app.models.materia import Materia
from app.models.permission import Permission
from app.models.reserva_evaluacion import EstadoReserva, ReservaEvaluacion
from app.models.resultado_evaluacion import ResultadoEvaluacion
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.tenant import Tenant
from app.models.turno_coloquio import TurnoColoquio
from app.models.user import User
from app.models.user_role import UserRole


@pytest_asyncio.fixture
async def setup_data(db_session):
    tid = uuid.uuid4()
    tenant = Tenant(id=tid, nombre='Test', codigo='TST-EVAL', estado='Activo')
    db_session.add(tenant)
    await db_session.flush()

    materia = Materia(tenant_id=tid, codigo='MAT-EVAL', nombre='Programacion I', estado='Activa')
    db_session.add(materia)
    await db_session.flush()

    carrera = Carrera(tenant_id=tid, nombre='Tecnicatura', codigo='TEC')
    db_session.add(carrera)
    await db_session.flush()

    cohorte = Cohorte(tenant_id=tid, carrera_id=carrera.id, nombre='2026', anio=2026, vig_desde=date(2026, 3, 1), vig_hasta=date(2026, 12, 31))
    db_session.add(cohorte)
    await db_session.flush()

    coord_user = User(tenant_id=tid, email='coord-eval@t.com', password_hash=hash_password('pass'), roles=['COORDINADOR'])
    db_session.add(coord_user)
    await db_session.flush()

    alumno_user = User(tenant_id=tid, email='alumno-eval@t.com', password_hash=hash_password('pass'), roles=['ALUMNO'])
    db_session.add(alumno_user)
    await db_session.flush()

    alumno2_user = User(tenant_id=tid, email='alumno2-eval@t.com', password_hash=hash_password('pass'), roles=['ALUMNO'])
    db_session.add(alumno2_user)
    await db_session.flush()

    not_alumno_user = User(tenant_id=tid, email='prof-eval@t.com', password_hash=hash_password('pass'), roles=['PROFESOR'])
    db_session.add(not_alumno_user)
    await db_session.flush()

    role_coord = Role(tenant_id=tid, name='COORDINADOR', codigo='COORDINADOR')
    db_session.add(role_coord)
    await db_session.flush()

    role_alumno = Role(tenant_id=tid, name='ALUMNO', codigo='ALUMNO')
    db_session.add(role_alumno)
    await db_session.flush()

    p_gestionar = Permission(tenant_id=tid, codigo='coloquios:gestionar', modulo='coloquios', accion='gestionar')
    db_session.add(p_gestionar)
    p_reservar = Permission(tenant_id=tid, codigo='coloquios:reservar', modulo='coloquios', accion='reservar')
    db_session.add(p_reservar)
    await db_session.flush()

    db_session.add(RolePermission(tenant_id=tid, role_id=role_coord.id, permiso_id=p_gestionar.id))
    db_session.add(RolePermission(tenant_id=tid, role_id=role_coord.id, permiso_id=p_reservar.id))
    db_session.add(RolePermission(tenant_id=tid, role_id=role_alumno.id, permiso_id=p_reservar.id))
    db_session.add(UserRole(tenant_id=tid, user_id=coord_user.id, role_id=role_coord.id))
    db_session.add(UserRole(tenant_id=tid, user_id=alumno_user.id, role_id=role_alumno.id))
    db_session.add(UserRole(tenant_id=tid, user_id=alumno2_user.id, role_id=role_alumno.id))
    await db_session.flush()

    coord_token = create_access_token(str(coord_user.id), str(tid), ['COORDINADOR'])
    alumno_token = create_access_token(str(alumno_user.id), str(tid), ['ALUMNO'])
    alumno2_token = create_access_token(str(alumno2_user.id), str(tid), ['ALUMNO'])

    return {
        'tid': tid,
        'materia': materia,
        'carrera': carrera,
        'cohorte': cohorte,
        'coord_user': coord_user,
        'alumno_user': alumno_user,
        'alumno2_user': alumno2_user,
        'not_alumno_user': not_alumno_user,
        'coord_token': coord_token,
        'alumno_token': alumno_token,
        'alumno2_token': alumno2_token,
    }


class TestCrearConvocatoria:
    async def _client(self, app, db_session, token):
        app.dependency_overrides[get_db] = lambda: db_session
        client = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        client.headers['Authorization'] = f'Bearer {token}'
        return client

    async def test_crear_convocatoria_exitosa_con_turnos(self, app, db_session, setup_data):
        """1.1 Crear convocatoria exitosa con turnos"""
        async with await self._client(app, db_session, setup_data['coord_token']) as client:
            resp = await client.post('/api/v1/coloquios/', json={
                'materia_id': str(setup_data['materia'].id),
                'cohorte_id': str(setup_data['cohorte'].id),
                'instancia': 'Coloquio Final',
                'tipo': 'Coloquio',
                'turnos': [
                    {'fecha': '2026-07-15', 'hora_inicio': '14:00', 'hora_fin': '18:00', 'cupo': 20},
                    {'fecha': '2026-07-16', 'hora_inicio': '14:00', 'hora_fin': '18:00', 'cupo': 15},
                    {'fecha': '2026-07-17', 'hora_inicio': '09:00', 'hora_fin': '13:00', 'cupo': 10},
                ],
            })
        assert resp.status_code == 201
        data = resp.json()
        assert data['instancia'] == 'Coloquio Final'
        assert data['tipo'] == 'Coloquio'
        assert data['estado'] == 'Activa'
        assert data['dias_disponibles'] == 3
        assert len(data['turnos']) == 3

    async def test_crear_convocatoria_sin_turnos_falla(self, app, db_session, setup_data):
        """1.2 Crear convocatoria sin turnos falla"""
        async with await self._client(app, db_session, setup_data['coord_token']) as client:
            resp = await client.post('/api/v1/coloquios/', json={
                'materia_id': str(setup_data['materia'].id),
                'cohorte_id': str(setup_data['cohorte'].id),
                'instancia': 'Sin Turnos',
                'tipo': 'Coloquio',
                'turnos': [],
            })
        assert resp.status_code == 422

    async def test_crear_convocatoria_sin_token_401(self, app, db_session, setup_data):
        client = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        resp = await client.post('/api/v1/coloquios/', json={
            'materia_id': str(setup_data['materia'].id),
            'cohorte_id': str(setup_data['cohorte'].id),
            'instancia': 'Test',
            'tipo': 'Coloquio',
            'turnos': [{'fecha': '2026-07-15', 'hora_inicio': '14:00', 'hora_fin': '18:00', 'cupo': 20}],
        })
        assert resp.status_code == 401


class TestImportarAlumnos:
    async def _client(self, app, db_session, token):
        app.dependency_overrides[get_db] = lambda: db_session
        client = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        client.headers['Authorization'] = f'Bearer {token}'
        return client

    async def _crear_evaluacion(self, db_session, setup_data) -> Evaluacion:
        ev = Evaluacion(
            tenant_id=setup_data['tid'],
            materia_id=setup_data['materia'].id,
            cohorte_id=setup_data['cohorte'].id,
            tipo=TipoEvaluacion.COLOQUIO,
            instancia='Coloquio Test',
            estado=EstadoEvaluacion.ACTIVA,
            dias_disponibles=1,
        )
        db_session.add(ev)
        await db_session.flush()
        return ev

    async def test_importar_alumnos_exitoso(self, app, db_session, setup_data):
        """2.1 Importar alumnos a convocatoria"""
        ev = await self._crear_evaluacion(db_session, setup_data)
        async with await self._client(app, db_session, setup_data['coord_token']) as client:
            resp = await client.post(f'/api/v1/coloquios/{ev.id}/alumnos', json={
                'alumno_ids': [str(setup_data['alumno_user'].id), str(setup_data['alumno2_user'].id)],
            })
        assert resp.status_code == 204

        result = await db_session.execute(
            select(ColoquioAlumno).where(
                ColoquioAlumno.evaluacion_id == ev.id,
                ColoquioAlumno.deleted_at.is_(None),
            )
        )
        alumnos = result.scalars().all()
        assert len(alumnos) == 2

    async def test_importar_alumnos_id_inexistente_falla(self, app, db_session, setup_data):
        """2.2 Importar con ID inexistente falla"""
        ev = await self._crear_evaluacion(db_session, setup_data)
        fake_id = uuid.uuid4()
        async with await self._client(app, db_session, setup_data['coord_token']) as client:
            resp = await client.post(f'/api/v1/coloquios/{ev.id}/alumnos', json={
                'alumno_ids': [str(fake_id)],
            })
        assert resp.status_code == 422

    async def test_importar_usuario_no_alumno_falla(self, app, db_session, setup_data):
        ev = await self._crear_evaluacion(db_session, setup_data)
        async with await self._client(app, db_session, setup_data['coord_token']) as client:
            resp = await client.post(f'/api/v1/coloquios/{ev.id}/alumnos', json={
                'alumno_ids': [str(setup_data['not_alumno_user'].id)],
            })
        assert resp.status_code == 422


class TestListarConvocatorias:
    async def _client(self, app, db_session, token):
        app.dependency_overrides[get_db] = lambda: db_session
        client = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        client.headers['Authorization'] = f'Bearer {token}'
        return client

    async def test_coordinador_lista_todas(self, app, db_session, setup_data):
        """3.1 COORDINADOR lista con metricas"""
        ev = Evaluacion(
            tenant_id=setup_data['tid'],
            materia_id=setup_data['materia'].id,
            cohorte_id=setup_data['cohorte'].id,
            tipo=TipoEvaluacion.COLOQUIO,
            instancia='Coloquio A',
            estado=EstadoEvaluacion.ACTIVA,
            dias_disponibles=1,
        )
        db_session.add(ev)
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['coord_token']) as client:
            resp = await client.get('/api/v1/coloquios/')
        assert resp.status_code == 200
        data = resp.json()
        assert data['total'] >= 1
        assert len(data['items']) >= 1

    async def test_alumno_lista_solo_habilitadas(self, app, db_session, setup_data):
        """3.2 ALUMNO lista solo sus convocatorias"""
        ev = Evaluacion(
            tenant_id=setup_data['tid'],
            materia_id=setup_data['materia'].id,
            cohorte_id=setup_data['cohorte'].id,
            tipo=TipoEvaluacion.COLOQUIO,
            instancia='Coloquio B',
            estado=EstadoEvaluacion.ACTIVA,
            dias_disponibles=1,
        )
        db_session.add(ev)
        await db_session.flush()

        ca = ColoquioAlumno(
            tenant_id=setup_data['tid'],
            evaluacion_id=ev.id,
            alumno_id=setup_data['alumno_user'].id,
        )
        db_session.add(ca)
        await db_session.flush()

        ev2 = Evaluacion(
            tenant_id=setup_data['tid'],
            materia_id=setup_data['materia'].id,
            cohorte_id=setup_data['cohorte'].id,
            tipo=TipoEvaluacion.COLOQUIO,
            instancia='Coloquio C (no habilitada)',
            estado=EstadoEvaluacion.ACTIVA,
            dias_disponibles=1,
        )
        db_session.add(ev2)
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['alumno_token']) as client:
            resp = await client.get('/api/v1/coloquios/')
        assert resp.status_code == 200
        data = resp.json()
        assert data['total'] == 1
        assert data['items'][0]['instancia'] == 'Coloquio B'


class TestMetricas:
    async def _client(self, app, db_session, token):
        app.dependency_overrides[get_db] = lambda: db_session
        client = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        client.headers['Authorization'] = f'Bearer {token}'
        return client

    async def test_metricas_globales(self, app, db_session, setup_data):
        ev = Evaluacion(
            tenant_id=setup_data['tid'],
            materia_id=setup_data['materia'].id,
            cohorte_id=setup_data['cohorte'].id,
            tipo=TipoEvaluacion.COLOQUIO,
            instancia='Metricas Test',
            estado=EstadoEvaluacion.ACTIVA,
            dias_disponibles=1,
        )
        db_session.add(ev)
        await db_session.flush()

        ca = ColoquioAlumno(
            tenant_id=setup_data['tid'],
            evaluacion_id=ev.id,
            alumno_id=setup_data['alumno_user'].id,
        )
        db_session.add(ca)
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['coord_token']) as client:
            resp = await client.get('/api/v1/coloquios/metricas')
        assert resp.status_code == 200
        data = resp.json()
        assert data['total_convocatorias_activas'] >= 1
        assert data['total_alumnos_convocados'] >= 1


class TestReserva:
    async def _client(self, app, db_session, token):
        app.dependency_overrides[get_db] = lambda: db_session
        client = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        client.headers['Authorization'] = f'Bearer {token}'
        return client

    async def _setup_convocatoria(self, db_session, setup_data, cupo=1) -> tuple[Evaluacion, TurnoColoquio]:
        ev = Evaluacion(
            tenant_id=setup_data['tid'],
            materia_id=setup_data['materia'].id,
            cohorte_id=setup_data['cohorte'].id,
            tipo=TipoEvaluacion.COLOQUIO,
            instancia='Coloquio Reserva',
            estado=EstadoEvaluacion.ACTIVA,
            dias_disponibles=1,
        )
        db_session.add(ev)
        await db_session.flush()

        turno = TurnoColoquio(
            tenant_id=setup_data['tid'],
            evaluacion_id=ev.id,
            fecha=date(2026, 7, 15),
            hora_inicio=eval('__import__("datetime").time(14, 0)'),
            hora_fin=eval('__import__("datetime").time(18, 0)'),
            cupo=cupo,
            ocupados=0,
        )
        db_session.add(turno)
        await db_session.flush()

        ca = ColoquioAlumno(
            tenant_id=setup_data['tid'],
            evaluacion_id=ev.id,
            alumno_id=setup_data['alumno_user'].id,
        )
        db_session.add(ca)
        await db_session.flush()

        return ev, turno

    async def test_reserva_exitosa_resta_cupo(self, app, db_session, setup_data):
        """5.1 Reserva exitosa resta cupo atomicamente"""
        ev, turno = await self._setup_convocatoria(db_session, setup_data, cupo=5)
        async with await self._client(app, db_session, setup_data['alumno_token']) as client:
            resp = await client.post(f'/api/v1/coloquios/{ev.id}/reservas', json={
                'turno_id': str(turno.id),
            })
        assert resp.status_code == 201
        data = resp.json()
        assert data['estado'] == 'Activa'

        await db_session.refresh(turno)
        assert turno.ocupados == 1

    async def test_reserva_sin_cupo_rechaza_409(self, app, db_session, setup_data):
        """5.2 Sin cupo rechaza 409"""
        ev, turno = await self._setup_convocatoria(db_session, setup_data, cupo=1)
        turno.ocupados = 1
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['alumno_token']) as client:
            resp = await client.post(f'/api/v1/coloquios/{ev.id}/reservas', json={
                'turno_id': str(turno.id),
            })
        assert resp.status_code == 409

    async def test_alumno_no_habilitado_rechaza_403(self, app, db_session, setup_data):
        """5.3 Alumno no habilitado rechaza 403"""
        ev, turno = await self._setup_convocatoria(db_session, setup_data)
        async with await self._client(app, db_session, setup_data['alumno2_token']) as client:
            resp = await client.post(f'/api/v1/coloquios/{ev.id}/reservas', json={
                'turno_id': str(turno.id),
            })
        assert resp.status_code == 403

    async def test_doble_reserva_activa_rechaza_409(self, app, db_session, setup_data):
        """5.4 Doble reserva en misma convocatoria rechaza 409"""
        ev, turno = await self._setup_convocatoria(db_session, setup_data, cupo=5)
        async with await self._client(app, db_session, setup_data['alumno_token']) as client:
            resp1 = await client.post(f'/api/v1/coloquios/{ev.id}/reservas', json={
                'turno_id': str(turno.id),
            })
            assert resp1.status_code == 201

            turno2 = TurnoColoquio(
                tenant_id=setup_data['tid'],
                evaluacion_id=ev.id,
                fecha=date(2026, 7, 16),
                hora_inicio=eval('__import__("datetime").time(14, 0)'),
                hora_fin=eval('__import__("datetime").time(18, 0)'),
                cupo=5,
                ocupados=0,
            )
            db_session.add(turno2)
            await db_session.flush()

            resp2 = await client.post(f'/api/v1/coloquios/{ev.id}/reservas', json={
                'turno_id': str(turno2.id),
            })
        assert resp2.status_code == 409


class TestCancelacion:
    async def _client(self, app, db_session, token):
        app.dependency_overrides[get_db] = lambda: db_session
        client = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        client.headers['Authorization'] = f'Bearer {token}'
        return client

    async def test_cancelacion_libera_cupo(self, app, db_session, setup_data):
        """6.1 Cancelacion libera cupo"""
        ev = Evaluacion(
            tenant_id=setup_data['tid'],
            materia_id=setup_data['materia'].id,
            cohorte_id=setup_data['cohorte'].id,
            tipo=TipoEvaluacion.COLOQUIO,
            instancia='Cancelacion Test',
            estado=EstadoEvaluacion.ACTIVA,
            dias_disponibles=1,
        )
        db_session.add(ev)
        await db_session.flush()

        turno = TurnoColoquio(
            tenant_id=setup_data['tid'],
            evaluacion_id=ev.id,
            fecha=date(2026, 7, 15),
            hora_inicio=eval('__import__("datetime").time(14, 0)'),
            hora_fin=eval('__import__("datetime").time(18, 0)'),
            cupo=5,
            ocupados=1,
        )
        db_session.add(turno)
        await db_session.flush()

        reserva = ReservaEvaluacion(
            tenant_id=setup_data['tid'],
            turno_id=turno.id,
            alumno_id=setup_data['alumno_user'].id,
            evaluacion_id=ev.id,
            estado=EstadoReserva.ACTIVA,
        )
        db_session.add(reserva)
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['alumno_token']) as client:
            resp = await client.delete(f'/api/v1/coloquios/reservas/{reserva.id}')
        assert resp.status_code == 200
        data = resp.json()
        assert data['mensaje'] == 'Reserva cancelada exitosamente'

        await db_session.refresh(turno)
        assert turno.ocupados == 0

    async def test_cancelar_reserva_ajena_falla(self, app, db_session, setup_data):
        """6.2 Cancelar reserva ajena falla 404"""
        ev = Evaluacion(
            tenant_id=setup_data['tid'],
            materia_id=setup_data['materia'].id,
            cohorte_id=setup_data['cohorte'].id,
            tipo=TipoEvaluacion.COLOQUIO,
            instancia='Cancelacion Ajena',
            estado=EstadoEvaluacion.ACTIVA,
            dias_disponibles=1,
        )
        db_session.add(ev)
        await db_session.flush()

        turno = TurnoColoquio(
            tenant_id=setup_data['tid'],
            evaluacion_id=ev.id,
            fecha=date(2026, 7, 15),
            hora_inicio=eval('__import__("datetime").time(14, 0)'),
            hora_fin=eval('__import__("datetime").time(18, 0)'),
            cupo=5,
            ocupados=1,
        )
        db_session.add(turno)
        await db_session.flush()

        reserva = ReservaEvaluacion(
            tenant_id=setup_data['tid'],
            turno_id=turno.id,
            alumno_id=setup_data['alumno2_user'].id,
            evaluacion_id=ev.id,
            estado=EstadoReserva.ACTIVA,
        )
        db_session.add(reserva)
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['alumno_token']) as client:
            resp = await client.delete(f'/api/v1/coloquios/reservas/{reserva.id}')
        assert resp.status_code == 404


class TestCerrarConvocatoria:
    async def _client(self, app, db_session, token):
        app.dependency_overrides[get_db] = lambda: db_session
        client = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        client.headers['Authorization'] = f'Bearer {token}'
        return client

    async def test_cerrar_convocatoria(self, app, db_session, setup_data):
        """7.1 Cerrar convocatoria"""
        ev = Evaluacion(
            tenant_id=setup_data['tid'],
            materia_id=setup_data['materia'].id,
            cohorte_id=setup_data['cohorte'].id,
            tipo=TipoEvaluacion.COLOQUIO,
            instancia='Cerrar Test',
            estado=EstadoEvaluacion.ACTIVA,
            dias_disponibles=1,
        )
        db_session.add(ev)
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['coord_token']) as client:
            resp = await client.patch(f'/api/v1/coloquios/{ev.id}/cerrar')
        assert resp.status_code == 200
        data = resp.json()
        assert data['estado'] == 'Cerrada'


class TestResultados:
    async def _client(self, app, db_session, token):
        app.dependency_overrides[get_db] = lambda: db_session
        client = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        client.headers['Authorization'] = f'Bearer {token}'
        return client

    async def test_registrar_nota_final(self, app, db_session, setup_data):
        """8.1 Registrar nota final"""
        ev = Evaluacion(
            tenant_id=setup_data['tid'],
            materia_id=setup_data['materia'].id,
            cohorte_id=setup_data['cohorte'].id,
            tipo=TipoEvaluacion.COLOQUIO,
            instancia='Nota Test',
            estado=EstadoEvaluacion.ACTIVA,
            dias_disponibles=1,
        )
        db_session.add(ev)
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['coord_token']) as client:
            resp = await client.put(f'/api/v1/coloquios/{ev.id}/resultados/{setup_data["alumno_user"].id}', json={
                'nota_final': 'Aprobado',
            })
        assert resp.status_code == 200
        data = resp.json()
        assert data['nota_final'] == 'Aprobado'
        assert data['alumno_id'] == str(setup_data['alumno_user'].id)

    async def test_listar_resultados_consolidados(self, app, db_session, setup_data):
        """8.2 Listar resultados consolidados"""
        ev = Evaluacion(
            tenant_id=setup_data['tid'],
            materia_id=setup_data['materia'].id,
            cohorte_id=setup_data['cohorte'].id,
            tipo=TipoEvaluacion.COLOQUIO,
            instancia='Listar Resultados',
            estado=EstadoEvaluacion.ACTIVA,
            dias_disponibles=1,
        )
        db_session.add(ev)
        await db_session.flush()

        r1 = ResultadoEvaluacion(
            tenant_id=setup_data['tid'],
            evaluacion_id=ev.id,
            alumno_id=setup_data['alumno_user'].id,
            nota_final='Aprobado',
        )
        db_session.add(r1)
        r2 = ResultadoEvaluacion(
            tenant_id=setup_data['tid'],
            evaluacion_id=ev.id,
            alumno_id=setup_data['alumno2_user'].id,
            nota_final='Regular',
        )
        db_session.add(r2)
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['coord_token']) as client:
            resp = await client.get(f'/api/v1/coloquios/{ev.id}/resultados')
        assert resp.status_code == 200
        data = resp.json()
        assert data['total'] == 2

    async def test_actualizar_nota_existente(self, app, db_session, setup_data):
        ev = Evaluacion(
            tenant_id=setup_data['tid'],
            materia_id=setup_data['materia'].id,
            cohorte_id=setup_data['cohorte'].id,
            tipo=TipoEvaluacion.COLOQUIO,
            instancia='Actualizar Nota',
            estado=EstadoEvaluacion.ACTIVA,
            dias_disponibles=1,
        )
        db_session.add(ev)
        await db_session.flush()

        r = ResultadoEvaluacion(
            tenant_id=setup_data['tid'],
            evaluacion_id=ev.id,
            alumno_id=setup_data['alumno_user'].id,
            nota_final='Regular',
        )
        db_session.add(r)
        await db_session.flush()

        async with await self._client(app, db_session, setup_data['coord_token']) as client:
            resp = await client.put(f'/api/v1/coloquios/{ev.id}/resultados/{setup_data["alumno_user"].id}', json={
                'nota_final': 'Aprobado',
            })
        assert resp.status_code == 200
        assert resp.json()['nota_final'] == 'Aprobado'


class TestMultiTenant:
    async def _client(self, app, db_session, token):
        app.dependency_overrides[get_db] = lambda: db_session
        client = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        client.headers['Authorization'] = f'Bearer {token}'
        return client

    async def test_aislamiento_multi_tenant(self, app, db_session, setup_data):
        """Tenant A no ve datos de tenant B"""
        tid_b = uuid.uuid4()
        tenant_b = Tenant(id=tid_b, nombre='Otro', codigo='OTRO', estado='Activo')
        db_session.add(tenant_b)
        await db_session.flush()

        role_b = Role(tenant_id=tid_b, name='COORDINADOR', codigo='COORDINADOR')
        db_session.add(role_b)
        await db_session.flush()

        user_b = User(tenant_id=tid_b, email='coord-b@t.com', password_hash=hash_password('pass'), roles=['COORDINADOR'])
        db_session.add(user_b)
        await db_session.flush()

        p = Permission(tenant_id=tid_b, codigo='coloquios:gestionar', modulo='coloquios', accion='gestionar')
        db_session.add(p)
        await db_session.flush()

        db_session.add(RolePermission(tenant_id=tid_b, role_id=role_b.id, permiso_id=p.id))
        db_session.add(UserRole(tenant_id=tid_b, user_id=user_b.id, role_id=role_b.id))
        await db_session.flush()

        ev_b = Evaluacion(
            tenant_id=tid_b,
            materia_id=setup_data['materia'].id,
            cohorte_id=setup_data['cohorte'].id,
            tipo=TipoEvaluacion.COLOQUIO,
            instancia='Solo Tenant B',
            estado=EstadoEvaluacion.ACTIVA,
            dias_disponibles=1,
        )
        db_session.add(ev_b)
        await db_session.flush()

        token_b = create_access_token(str(user_b.id), str(tid_b), ['COORDINADOR'])

        async with await self._client(app, db_session, setup_data['coord_token']) as client:
            resp = await client.get('/api/v1/coloquios/')
        assert resp.status_code == 200
        data = resp.json()

        for item in data['items']:
            assert item['instancia'] != 'Solo Tenant B'


class TestRaceCondition:
    async def test_race_condition_ultimo_cupo(self, app, db_session, setup_data):
        tid = setup_data['tid']
        ev = Evaluacion(
            tenant_id=tid, materia_id=setup_data['materia'].id,
            cohorte_id=setup_data['cohorte'].id,
            tipo=TipoEvaluacion.COLOQUIO, instancia='Race',
            estado=EstadoEvaluacion.ACTIVA, dias_disponibles=1,
        )
        db_session.add(ev)
        await db_session.flush()

        turno = TurnoColoquio(
            tenant_id=tid, evaluacion_id=ev.id,
            fecha=date(2026, 7, 15),
            hora_inicio=eval('__import__("datetime").time(14, 0)'),
            hora_fin=eval('__import__("datetime").time(18, 0)'),
            cupo=1, ocupados=0,
        )
        db_session.add(turno)
        await db_session.flush()

        ca = ColoquioAlumno(tenant_id=tid, evaluacion_id=ev.id, alumno_id=setup_data['alumno_user'].id)
        db_session.add(ca)
        ca2 = ColoquioAlumno(tenant_id=tid, evaluacion_id=ev.id, alumno_id=setup_data['alumno2_user'].id)
        db_session.add(ca2)
        await db_session.flush()

        from app.repositories.evaluacion_repository import TurnoColoquioRepository
        repo = TurnoColoquioRepository(db_session, tid)

        r1 = await repo.atomic_reserve(turno.id)
        assert r1 == 1

        r2 = await repo.atomic_reserve(turno.id)
        assert r2 == 0


class TestSoftDelete:
    async def test_soft_delete_evaluacion(self, app, db_session, setup_data):
        ev = Evaluacion(
            tenant_id=setup_data['tid'],
            materia_id=setup_data['materia'].id,
            cohorte_id=setup_data['cohorte'].id,
            tipo=TipoEvaluacion.COLOQUIO,
            instancia='Soft Delete',
            estado=EstadoEvaluacion.ACTIVA,
            dias_disponibles=1,
        )
        db_session.add(ev)
        await db_session.flush()

        from app.repositories.evaluacion_repository import EvaluacionRepository
        repo = EvaluacionRepository(db_session, setup_data['tid'])
        await repo.soft_delete(ev)

        deleted = await repo.get_with_deleted(ev.id)
        assert deleted is not None
        assert deleted.deleted_at is not None

        not_found = await repo.get(ev.id)
        assert not_found is None
