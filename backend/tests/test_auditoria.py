import uuid
from datetime import datetime, timedelta, timezone

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.core.audit_codes import CALIFICACIONES_IMPORTAR, COMUNICACION_ENVIAR
from app.core.dependencies import get_current_user, get_db
from app.core.security import create_access_token
from app.main import create_app
from app.models.asignacion import Asignacion
from app.models.audit_log import AuditLog
from app.models.comunicacion import Comunicacion, EstadoComunicacion
from app.models.materia import Materia
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.tenant import Tenant
from app.models.user import User
from app.models.user_role import UserRole
from tests.helpers import _create_tenant, _create_user, _seed_permission_for_role


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def tenant(db_session):
    return await _create_tenant(db_session, nombre='Test', codigo='TST')


@pytest_asyncio.fixture
async def materia_ids(db_session, tenant):
    materias = []
    for i in range(3):
        materia = Materia(
            tenant_id=tenant.id,
            nombre=f'Materia {i}',
            codigo=f'MAT{i:02d}',
        )
        db_session.add(materia)
        materias.append(materia)
    await db_session.flush()
    ids = [m.id for m in materias]
    return ids


@pytest_asyncio.fixture
async def admin_user(db_session, tenant):
    return await _create_user(db_session, tenant.id, email='admin@test.com', roles=['ADMIN'])


@pytest_asyncio.fixture
async def coordinador_user(db_session, tenant):
    return await _create_user(db_session, tenant.id, email='coord@test.com', roles=['COORDINADOR'])


@pytest_asyncio.fixture
async def docente_user(db_session, tenant):
    return await _create_user(db_session, tenant.id, email='docente@test.com', roles=['PROFESOR'])


@pytest_asyncio.fixture
async def auditoria_permiso(db_session, tenant):
    perm = Permission(
        tenant_id=tenant.id,
        codigo='auditoria:ver',
        descripcion='Ver panel de auditoría',
        modulo='auditoria',
        accion='ver',
    )
    db_session.add(perm)
    await db_session.flush()
    return perm


@pytest_asyncio.fixture
async def admin_token(tenant, admin_user, auditoria_permiso, db_session):
    await _seed_permission_for_role(db_session, tenant.id, 'ADMIN', 'auditoria:ver')
    return create_access_token(
        user_id=str(admin_user.id),
        tenant_id=str(tenant.id),
        roles=['ADMIN'],
    )


@pytest_asyncio.fixture
async def coordinador_token(tenant, coordinador_user, auditoria_permiso, db_session):
    await _seed_permission_for_role(db_session, tenant.id, 'COORDINADOR', 'auditoria:ver')
    return create_access_token(
        user_id=str(coordinador_user.id),
        tenant_id=str(tenant.id),
        roles=['COORDINADOR'],
    )


@pytest_asyncio.fixture
async def sample_logs(db_session, tenant, admin_user, materia_ids):
    logs = []
    now = datetime.now(timezone.utc)
    for i, accion in enumerate([CALIFICACIONES_IMPORTAR, COMUNICACION_ENVIAR, CALIFICACIONES_IMPORTAR]):
        log = AuditLog(
            tenant_id=tenant.id,
            actor_id=admin_user.id,
            materia_id=materia_ids[i],
            accion=accion,
            detalle={'test': True},
            filas_afectadas=10 * (i + 1),
            ip='10.0.0.1',
            user_agent='pytest',
            fecha_hora=now - timedelta(days=i),
        )
        db_session.add(log)
        logs.append(log)
    await db_session.flush()
    return logs


@pytest_asyncio.fixture
async def sample_comunicaciones(db_session, tenant, docente_user, materia_ids):
    comms = []
    estados = [
        EstadoComunicacion.PENDIENTE,
        EstadoComunicacion.ENVIADO,
        EstadoComunicacion.ERROR,
    ]
    lote_id = uuid.uuid4()
    for i, estado in enumerate(estados):
        comm = Comunicacion(
            tenant_id=tenant.id,
            enviado_por=docente_user.id,
            materia_id=materia_ids[0],
            destinatario='alumno@test.com',
            asunto='Test',
            cuerpo='Test body',
            estado=estado,
            lote_id=lote_id,
        )
        db_session.add(comm)
        comms.append(comm)
    await db_session.flush()
    return comms


@pytest_asyncio.fixture
async def coordinador_asignacion(db_session, tenant, coordinador_user, materia_ids):
    asignacion = Asignacion(
        tenant_id=tenant.id,
        usuario_id=coordinador_user.id,
        rol='COORDINADOR',
        materia_id=materia_ids[0],
        desde=datetime.now(timezone.utc) - timedelta(days=30),
        hasta=datetime.now(timezone.utc) + timedelta(days=30),
    )
    db_session.add(asignacion)
    await db_session.flush()
    return asignacion


# ---------------------------------------------------------------------------
# Group 5: Tests — Agregaciones y log detallado
# ---------------------------------------------------------------------------

class TestAccionesPorDia:
    @pytest.mark.asyncio
    async def test_acciones_agrupadas_por_fecha(
        self, db_session, tenant, admin_token, sample_logs,
    ):
        app = create_app()
        app.dependency_overrides[get_db] = lambda: db_session
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.get(
                '/api/v1/auditoria/acciones-por-dia',
                headers={'Authorization': f'Bearer {admin_token}'},
            )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3

        acciones_por_fecha = {}
        for item in data:
            key = (item['fecha'], item['accion'])
            acciones_por_fecha[key] = item['total']

        for log in sample_logs:
            fecha_str = log.fecha_hora.date().isoformat()
            key = (fecha_str, log.accion)
            assert key in acciones_por_fecha, f'{key} not in response'


class TestComunicacionesPorDocente:
    @pytest.mark.asyncio
    async def test_distribucion_estados(
        self, db_session, tenant, admin_token, docente_user, sample_comunicaciones, materia_ids,
    ):
        app = create_app()
        app.dependency_overrides[get_db] = lambda: db_session
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.get(
                '/api/v1/auditoria/comunicaciones-por-docente',
                headers={'Authorization': f'Bearer {admin_token}'},
            )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

        docente_data = next(
            (d for d in data if d['usuario_id'] == str(docente_user.id)),
            None,
        )
        assert docente_data is not None
        assert docente_data['pendientes'] >= 1
        assert docente_data['enviadas'] >= 1
        assert docente_data['fallidas'] >= 1

    @pytest.mark.asyncio
    async def test_filtro_por_materia(
        self, db_session, tenant, admin_token, docente_user, sample_comunicaciones, materia_ids,
    ):
        app = create_app()
        app.dependency_overrides[get_db] = lambda: db_session
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.get(
                '/api/v1/auditoria/comunicaciones-por-docente',
                params={'materia_id': str(materia_ids[0])},
                headers={'Authorization': f'Bearer {admin_token}'},
            )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        for item in data:
            assert item.get('materia_id') == str(materia_ids[0]) or item.get('materia_id') is None


class TestInteraccionesPorDocenteMateria:
    @pytest.mark.asyncio
    async def test_conteo_por_accion(
        self, db_session, tenant, admin_token, admin_user, sample_logs,
    ):
        app = create_app()
        app.dependency_overrides[get_db] = lambda: db_session
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.get(
                '/api/v1/auditoria/interacciones-por-docente-materia',
                headers={'Authorization': f'Bearer {admin_token}'},
            )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2

        calif_entries = [
            d for d in data
            if d['usuario_id'] == str(admin_user.id)
            and d['accion'] == CALIFICACIONES_IMPORTAR
        ]
        assert len(calif_entries) >= 1


class TestListLog:
    @pytest.mark.asyncio
    async def test_default_limit_200(
        self, db_session, tenant, admin_token, sample_logs,
    ):
        app = create_app()
        app.dependency_overrides[get_db] = lambda: db_session
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.get(
                '/api/v1/auditoria/log',
                headers={'Authorization': f'Bearer {admin_token}'},
            )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 200
        assert len(data) == 3

    @pytest.mark.asyncio
    async def test_respects_max_1000(
        self, db_session, tenant, admin_token, sample_logs,
    ):
        app = create_app()
        app.dependency_overrides[get_db] = lambda: db_session
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.get(
                '/api/v1/auditoria/log',
                params={'max_records': 5000},
                headers={'Authorization': f'Bearer {admin_token}'},
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    @pytest.mark.asyncio
    async def test_filtros_combinados(
        self, db_session, tenant, admin_token, admin_user, materia_ids, sample_logs,
    ):
        app = create_app()
        app.dependency_overrides[get_db] = lambda: db_session
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.get(
                '/api/v1/auditoria/log',
                params={
                    'materia_id': str(materia_ids[0]),
                    'usuario_id': str(admin_user.id),
                    'accion': CALIFICACIONES_IMPORTAR,
                },
                headers={'Authorization': f'Bearer {admin_token}'},
            )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if data:
            for entry in data:
                assert entry['materia_id'] == str(materia_ids[0])
                assert entry['actor_id'] == str(admin_user.id)
                assert entry['accion'] == CALIFICACIONES_IMPORTAR

    @pytest.mark.asyncio
    async def test_filtro_fechas(
        self, db_session, tenant, admin_token, sample_logs,
    ):
        hoy = datetime.now(timezone.utc).date()
        ayer = hoy - timedelta(days=1)

        app = create_app()
        app.dependency_overrides[get_db] = lambda: db_session
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.get(
                '/api/v1/auditoria/log',
                params={
                    'fecha_desde': ayer.isoformat(),
                    'fecha_hasta': hoy.isoformat(),
                },
                headers={'Authorization': f'Bearer {admin_token}'},
            )

        assert response.status_code == 200
        data = response.json()
        for entry in data:
            entry_date = datetime.fromisoformat(entry['fecha_hora']).date()
            assert ayer <= entry_date <= hoy


# ---------------------------------------------------------------------------
# Group 6: Tests — Scope del coordinador
# ---------------------------------------------------------------------------

class TestScopeCoordinador:
    @pytest.mark.asyncio
    async def test_coordinador_ve_solo_sus_materias(
        self, db_session, tenant, coordinador_token, coordinador_user,
        admin_user, materia_ids, coordinador_asignacion,
    ):
        now = datetime.now(timezone.utc)
        log_en_materia = AuditLog(
            tenant_id=tenant.id,
            actor_id=admin_user.id,
            materia_id=materia_ids[0],
            accion=CALIFICACIONES_IMPORTAR,
            detalle=None,
            filas_afectadas=1,
            ip='10.0.0.1',
            user_agent='pytest',
            fecha_hora=now,
        )
        log_otra_materia = AuditLog(
            tenant_id=tenant.id,
            actor_id=admin_user.id,
            materia_id=materia_ids[1],
            accion=COMUNICACION_ENVIAR,
            detalle=None,
            filas_afectadas=1,
            ip='10.0.0.1',
            user_agent='pytest',
            fecha_hora=now,
        )
        db_session.add_all([log_en_materia, log_otra_materia])
        await db_session.flush()

        app = create_app()
        app.dependency_overrides[get_db] = lambda: db_session
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.get(
                '/api/v1/auditoria/log',
                headers={'Authorization': f'Bearer {coordinador_token}'},
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]['materia_id'] == str(materia_ids[0])

    @pytest.mark.asyncio
    async def test_admin_ve_todos_los_registros(
        self, db_session, tenant, admin_token, admin_user, materia_ids,
    ):
        now = datetime.now(timezone.utc)
        logs = []
        for mid in materia_ids[:2]:
            log = AuditLog(
                tenant_id=tenant.id,
                actor_id=admin_user.id,
                materia_id=mid,
                accion=CALIFICACIONES_IMPORTAR,
                detalle=None,
                filas_afectadas=1,
                ip='10.0.0.1',
                user_agent='pytest',
                fecha_hora=now,
            )
            db_session.add(log)
            logs.append(log)
        await db_session.flush()

        app = create_app()
        app.dependency_overrides[get_db] = lambda: db_session
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.get(
                '/api/v1/auditoria/log',
                headers={'Authorization': f'Bearer {admin_token}'},
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    @pytest.mark.asyncio
    async def test_coordinador_sin_asignaciones_retorna_vacio(
        self, db_session, tenant, coordinador_token, admin_user, materia_ids,
    ):
        now = datetime.now(timezone.utc)
        log = AuditLog(
            tenant_id=tenant.id,
            actor_id=admin_user.id,
            materia_id=materia_ids[0],
            accion=CALIFICACIONES_IMPORTAR,
            detalle=None,
            filas_afectadas=1,
            ip='10.0.0.1',
            user_agent='pytest',
            fecha_hora=now,
        )
        db_session.add(log)
        await db_session.flush()

        app = create_app()
        app.dependency_overrides[get_db] = lambda: db_session
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.get(
                '/api/v1/auditoria/log',
                headers={'Authorization': f'Bearer {coordinador_token}'},
            )

        assert response.status_code == 200
        data = response.json()
        assert data == []

    @pytest.mark.asyncio
    async def test_scope_aplicado_a_metricas(
        self, db_session, tenant, coordinador_token, coordinador_user,
        admin_user, materia_ids, coordinador_asignacion,
    ):
        now = datetime.now(timezone.utc)
        log_en_materia = AuditLog(
            tenant_id=tenant.id,
            actor_id=admin_user.id,
            materia_id=materia_ids[0],
            accion=CALIFICACIONES_IMPORTAR,
            detalle=None,
            filas_afectadas=1,
            ip='10.0.0.1',
            user_agent='pytest',
            fecha_hora=now,
        )
        log_otra_materia = AuditLog(
            tenant_id=tenant.id,
            actor_id=admin_user.id,
            materia_id=materia_ids[1],
            accion=COMUNICACION_ENVIAR,
            detalle=None,
            filas_afectadas=1,
            ip='10.0.0.1',
            user_agent='pytest',
            fecha_hora=now,
        )
        db_session.add_all([log_en_materia, log_otra_materia])
        await db_session.flush()

        app = create_app()
        app.dependency_overrides[get_db] = lambda: db_session
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.get(
                '/api/v1/auditoria/interacciones-por-docente-materia',
                headers={'Authorization': f'Bearer {coordinador_token}'},
            )

        assert response.status_code == 200
        data = response.json()
        for item in data:
            assert item['materia_id'] == str(materia_ids[0])
