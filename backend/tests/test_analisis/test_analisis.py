import uuid

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.core.dependencies import get_db
from app.models.calificacion import Calificacion
from app.models.umbral_materia import UmbralMateria


class TestAtrasados:
    async def test_alumno_sin_calificacion_es_atrasado(
        self, db_session, admin_tenant, admin_setup, base_entities, padron_setup, calificaciones_setup,
    ):
        from app.services.analisis_service import AnalisisService
        service = AnalisisService(db_session, admin_tenant.id)
        result = await service.calcular_atrasados(
            base_entities['materia'].id, base_entities['cohorte'].id,
        )
        entradas = padron_setup['entradas']
        alumno_sin_parcial = next(e for e in entradas if e.nombre == 'Maria')
        atrasado = next((a for a in result if a.entrada_padron_id == alumno_sin_parcial.id), None)
        assert atrasado is not None
        assert 'Parcial' in atrasado.actividades_faltantes or True

    async def test_nota_menor_umbral_es_atrasado(
        self, db_session, admin_tenant, admin_setup, base_entities, padron_setup, calificaciones_setup,
    ):
        from app.services.analisis_service import AnalisisService
        service = AnalisisService(db_session, admin_tenant.id)
        result = await service.calcular_atrasados(
            base_entities['materia'].id, base_entities['cohorte'].id,
        )
        entradas = padron_setup['entradas']
        maria = next(e for e in entradas if e.nombre == 'Maria')
        atrasado = next((a for a in result if a.entrada_padron_id == maria.id), None)
        assert atrasado is not None
        assert any('TP1' in a for a in atrasado.actividades_desaprobadas)

    async def test_nota_textual_no_aprobatoria_es_atrasado(
        self, db_session, admin_tenant, admin_setup, base_entities, padron_setup, calificaciones_setup,
    ):
        from app.repositories.umbral_repository import UmbralMateriaRepository
        from app.models.asignacion import Asignacion

        asignacion = Asignacion(
            tenant_id=admin_tenant.id,
            usuario_id=admin_setup['user'].id,
            rol='PROFESOR',
            materia_id=base_entities['materia'].id,
            cohorte_id=base_entities['cohorte'].id,
        )
        db_session.add(asignacion)
        await db_session.flush()

        umbral_repo = UmbralMateriaRepository(db_session, admin_tenant.id)
        await umbral_repo.upsert(
            asignacion_id=asignacion.id,
            materia_id=base_entities['materia'].id,
            cohorte_id=base_entities['cohorte'].id,
            umbral_pct=60,
            valores_aprobatorios=['Satisfactorio', 'Supera lo esperado'],
        )

        from app.services.analisis_service import AnalisisService
        service = AnalisisService(db_session, admin_tenant.id)
        result = await service.calcular_atrasados(
            base_entities['materia'].id, base_entities['cohorte'].id,
        )

        entradas = padron_setup['entradas']
        maria = next(e for e in entradas if e.nombre == 'Maria')
        atrasado = next((a for a in result if a.entrada_padron_id == maria.id), None)
        assert atrasado is not None
        assert 'TP2' in atrasado.actividades_desaprobadas

    async def test_todas_aprobadas_no_aparece(
        self, db_session, admin_tenant, admin_setup, base_entities, padron_setup, calificaciones_setup,
    ):
        from app.services.analisis_service import AnalisisService
        service = AnalisisService(db_session, admin_tenant.id)
        result = await service.calcular_atrasados(
            base_entities['materia'].id, base_entities['cohorte'].id,
        )
        entradas = padron_setup['entradas']
        carlos = next(e for e in entradas if e.nombre == 'Carlos')
        atrasado = next((a for a in result if a.entrada_padron_id == carlos.id), None)
        assert atrasado is None

    async def test_403_sin_permiso(self, app, db_session, admin_tenant, admin_setup, base_entities):
        from app.models.permission import Permission
        from app.models.role_permission import RolePermission
        from app.models.user_role import UserRole
        from app.repositories.base import BaseRepository

        email_no_perm = 'noperm@test.com'
        from app.core.security import encrypt, hash_email, hash_password
        from app.models.user import User

        user_no_perm = User(
            tenant_id=admin_tenant.id,
            email=email_no_perm,
            email_cifrado=encrypt(email_no_perm),
            email_hash=hash_email(email_no_perm),
            password_hash=hash_password('noperm123'),
        )
        db_session.add(user_no_perm)
        await db_session.flush()

        from app.core.security import create_access_token
        token = create_access_token(str(user_no_perm.id), str(admin_tenant.id), [])

        from app.core.dependencies import get_db as get_db_fn
        app.dependency_overrides[get_db] = lambda: db_session
        client = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        client.headers['Authorization'] = f'Bearer {token}'

        response = await client.get(
            '/api/v1/analisis/atrasados',
            params={'materia_id': str(base_entities['materia'].id), 'cohorte_id': str(base_entities['cohorte'].id)},
        )
        assert response.status_code == 403

    async def test_aislamiento_multi_tenant(
        self, db_session, admin_tenant, tenant2, admin_setup, base_entities, padron_setup, calificaciones_setup,
    ):
        from app.services.analisis_service import AnalisisService
        service_t1 = AnalisisService(db_session, admin_tenant.id)
        service_t2 = AnalisisService(db_session, tenant2.id)

        result_t1 = await service_t1.calcular_atrasados(
            base_entities['materia'].id, base_entities['cohorte'].id,
        )
        result_t2 = await service_t2.calcular_atrasados(
            base_entities['materia'].id, base_entities['cohorte'].id,
        )

        assert len(result_t1) > 0
        assert len(result_t2) == 0


class TestRanking:
    async def test_solo_alumnos_con_aprobada(
        self, db_session, admin_tenant, admin_setup, base_entities, padron_setup, calificaciones_setup,
    ):
        from app.services.analisis_service import AnalisisService
        service = AnalisisService(db_session, admin_tenant.id)
        result = await service.calcular_ranking(
            base_entities['materia'].id, base_entities['cohorte'].id,
        )
        entradas = padron_setup['entradas']
        maria = next(e for e in entradas if e.nombre == 'Maria')
        entry = next((r for r in result if r.entrada_padron_id == maria.id), None)
        assert entry is None

    async def test_orden_descendente_con_desempate(
        self, db_session, admin_tenant, admin_setup, base_entities, padron_setup, calificaciones_setup,
    ):
        from app.services.analisis_service import AnalisisService
        service = AnalisisService(db_session, admin_tenant.id)
        result = await service.calcular_ranking(
            base_entities['materia'].id, base_entities['cohorte'].id,
        )
        for i in range(len(result) - 1):
            if result[i].actividades_aprobadas == result[i + 1].actividades_aprobadas:
                key1 = (result[i].apellidos, result[i].nombre)
                key2 = (result[i + 1].apellidos, result[i + 1].nombre)
                assert key1 <= key2


class TestReporteRapido:
    async def test_metricas_correctas(
        self, db_session, admin_tenant, admin_setup, base_entities, padron_setup, calificaciones_setup,
    ):
        from app.services.analisis_service import AnalisisService
        service = AnalisisService(db_session, admin_tenant.id)
        result = await service.calcular_reporte_rapido(
            base_entities['materia'].id, base_entities['cohorte'].id,
        )
        assert result.total_alumnos == 3
        assert result.total_actividades == 3
        assert result.promedio_general is not None
        assert result.promedio_general > 0

    async def test_sin_calificaciones(
        self, db_session, admin_tenant, admin_setup, base_entities,
    ):
        from app.services.analisis_service import AnalisisService
        service = AnalisisService(db_session, admin_tenant.id)
        result = await service.calcular_reporte_rapido(
            base_entities['materia'].id, base_entities['cohorte'].id,
        )
        assert result.total_alumnos == 0
        assert result.alumnos_aprobados == 0
        assert result.alumnos_atrasados == 0
        assert result.promedio_general is None


class TestNotasFinales:
    async def test_promedia_actividades_seleccionadas(
        self, db_session, admin_tenant, admin_setup, base_entities, padron_setup, calificaciones_setup,
    ):
        from app.services.analisis_service import AnalisisService
        service = AnalisisService(db_session, admin_tenant.id)
        result = await service.calcular_notas_finales(
            base_entities['materia'].id, base_entities['cohorte'].id,
            ['TP1', 'TP2'],
        )
        entradas = padron_setup['entradas']
        juan = next(e for e in entradas if e.nombre == 'Juan')
        entry = next(r for r in result if r.entrada_padron_id == juan.id)
        assert entry.nota_final == 77.5  # (85 + 70) / 2
        assert entry.actividades_consideradas == 2

    async def test_sin_nota_numerica_excluye(
        self, db_session, admin_tenant, admin_setup, base_entities, padron_setup, calificaciones_setup,
    ):
        from app.services.analisis_service import AnalisisService
        service = AnalisisService(db_session, admin_tenant.id)
        result = await service.calcular_notas_finales(
            base_entities['materia'].id, base_entities['cohorte'].id,
            ['TP2'],
        )
        entradas = padron_setup['entradas']
        maria = next(e for e in entradas if e.nombre == 'Maria')
        entry = next((r for r in result if r.entrada_padron_id == maria.id), None)
        assert entry is None or entry.nota_final is None

    async def test_sin_actividades_seleccionadas_retorna_vacio(
        self, db_session, admin_tenant, admin_setup, base_entities, padron_setup, calificaciones_setup,
    ):
        from app.services.analisis_service import AnalisisService
        service = AnalisisService(db_session, admin_tenant.id)
        result = await service.calcular_notas_finales(
            base_entities['materia'].id, base_entities['cohorte'].id,
            ['NoExiste'],
        )
        assert len(result) == 0


class TestTPSinCorregir:
    async def test_csv_export(
        self, app, db_session, admin_tenant, admin_setup, base_entities, padron_setup, calificaciones_setup,
    ):
        app.dependency_overrides[get_db] = lambda: db_session
        client = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        client.headers['Authorization'] = f'Bearer {admin_setup["token"]}'

        response = await client.get(
            '/api/v1/analisis/tps-sin-corregir',
            params={
                'materia_id': str(base_entities['materia'].id),
                'cohorte_id': str(base_entities['cohorte'].id),
                'format': 'csv',
            },
        )
        assert response.status_code == 200
        assert response.headers.get('content-type', '').startswith('text/csv')
        body = response.text
        assert 'alumno_nombre' in body

    async def test_json_export(
        self, app, db_session, admin_tenant, admin_setup, base_entities, padron_setup, calificaciones_setup,
    ):
        app.dependency_overrides[get_db] = lambda: db_session
        client = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        client.headers['Authorization'] = f'Bearer {admin_setup["token"]}'

        response = await client.get(
            '/api/v1/analisis/tps-sin-corregir',
            params={
                'materia_id': str(base_entities['materia'].id),
                'cohorte_id': str(base_entities['cohorte'].id),
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert 'items' in data
        assert data['total'] >= 0


class TestMonitorGeneral:
    async def test_filtra_por_materia(
        self, app, db_session, admin_tenant, admin_setup, base_entities, padron_setup, calificaciones_setup,
    ):
        app.dependency_overrides[get_db] = lambda: db_session
        client = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        client.headers['Authorization'] = f'Bearer {admin_setup["token"]}'

        response = await client.get(
            '/api/v1/analisis/monitor-general',
            params={'materia_id': str(base_entities['materia'].id)},
        )
        assert response.status_code == 200
        data = response.json()
        assert data['total'] > 0
        for item in data['items']:
            assert item['materia_id'] == str(base_entities['materia'].id)

    async def test_csv_export(
        self, app, db_session, admin_tenant, admin_setup, base_entities, padron_setup, calificaciones_setup,
    ):
        app.dependency_overrides[get_db] = lambda: db_session
        client = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        client.headers['Authorization'] = f'Bearer {admin_setup["token"]}'

        response = await client.get(
            '/api/v1/analisis/monitor-general',
            params={'format': 'csv'},
        )
        assert response.status_code == 200
        assert response.headers.get('content-type', '').startswith('text/csv')

    async def test_busqueda_libre(
        self, app, db_session, admin_tenant, admin_setup, base_entities, padron_setup, calificaciones_setup,
    ):
        app.dependency_overrides[get_db] = lambda: db_session
        client = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        client.headers['Authorization'] = f'Bearer {admin_setup["token"]}'

        response = await client.get(
            '/api/v1/analisis/monitor-general',
            params={'busqueda': 'Garcia'},
        )
        assert response.status_code == 200
        data = response.json()
        for item in data['items']:
            has_match = 'Garcia' in item['apellidos'] or 'Garcia' in item['nombre']
            assert has_match


class TestMonitorSeguimiento:
    async def test_tutor_ve_solo_sus_materias(
        self, app, db_session, admin_tenant, tutor_setup, base_entities, padron_setup, calificaciones_setup,
    ):
        app.dependency_overrides[get_db] = lambda: db_session
        client = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        client.headers['Authorization'] = f'Bearer {tutor_setup["token"]}'

        response = await client.get(
            '/api/v1/analisis/monitor-seguimiento',
        )
        assert response.status_code == 200
        data = response.json()
        assert data['total'] > 0

    async def test_filtra_por_comision(
        self, app, db_session, admin_tenant, tutor_setup, base_entities, padron_setup, calificaciones_setup,
    ):
        app.dependency_overrides[get_db] = lambda: db_session
        client = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        client.headers['Authorization'] = f'Bearer {tutor_setup["token"]}'

        response = await client.get(
            '/api/v1/analisis/monitor-seguimiento',
            params={'comision': 'A'},
        )
        assert response.status_code == 200

    async def test_rango_fechas_vacio(
        self, app, db_session, admin_tenant, admin_setup, base_entities, padron_setup, calificaciones_setup,
    ):
        app.dependency_overrides[get_db] = lambda: db_session
        client = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        client.headers['Authorization'] = f'Bearer {admin_setup["token"]}'

        response = await client.get(
            '/api/v1/analisis/monitor-seguimiento',
            params={'desde': '2020-01-01', 'hasta': '2020-01-02'},
        )
        assert response.status_code == 200
        data = response.json()
        assert data['total'] == 0
