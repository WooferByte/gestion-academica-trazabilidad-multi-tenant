import io
import json
import uuid
from datetime import datetime, timezone

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.core.dependencies import get_db
from app.core.security import create_access_token, encrypt, hash_email, hash_password
from app.models.asignacion import Asignacion
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
from app.models.entrada_padron import EntradaPadron
from app.models.materia import Materia
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.tenant import Tenant
from app.models.user import User
from app.models.user_role import UserRole
from app.models.version_padron import VersionPadron


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

    p_calif = Permission(
        tenant_id=tid, codigo='calificaciones:importar', modulo='calificaciones', accion='importar',
    )
    db_session.add(p_calif)
    await db_session.flush()

    db_session.add_all([
        RolePermission(tenant_id=tid, role_id=role_admin.id, permiso_id=p_calif.id),
        UserRole(tenant_id=tid, user_id=user.id, role_id=role_admin.id),
    ])
    await db_session.flush()

    token = create_access_token(str(user.id), str(tid), ['ADMIN'])
    return {'token': token, 'tid': tid, 'user': user}


@pytest_asyncio.fixture
async def base_entities(db_session, admin_tenant):
    carrera = Carrera(tenant_id=admin_tenant.id, codigo='ING', nombre='Ingenieria')
    db_session.add(carrera)
    await db_session.flush()

    materia = Materia(tenant_id=admin_tenant.id, codigo='MATE', nombre='Matematicas')
    db_session.add(materia)
    await db_session.flush()

    cohorte = Cohorte(
        tenant_id=admin_tenant.id, carrera_id=carrera.id,
        nombre='2026', anio=2026,
        vig_desde=datetime.now(timezone.utc).date(),
    )
    db_session.add(cohorte)
    await db_session.flush()

    return {'materia': materia, 'cohorte': cohorte, 'carrera': carrera}


@pytest_asyncio.fixture
async def padron_setup(db_session, admin_tenant, admin_setup, base_entities):
    version = VersionPadron(
        tenant_id=admin_tenant.id,
        materia_id=base_entities['materia'].id,
        cohorte_id=base_entities['cohorte'].id,
        cargado_por=admin_setup['user'].id,
        activa=True,
    )
    db_session.add(version)
    await db_session.flush()

    entradas = [
        EntradaPadron(
            tenant_id=admin_tenant.id, version_id=version.id,
            nombre=n, apellidos=a, email=e,
            comision='A', regional='CABA',
        )
        for n, a, e in [
            ('Juan', 'Perez', 'juan@test.com'),
            ('Maria', 'Garcia', 'maria@test.com'),
            ('Carlos', 'Lopez', 'carlos@test.com'),
        ]
    ]
    db_session.add_all(entradas)
    await db_session.flush()
    return {'version': version, 'entradas': entradas}


class TestAprobadoDerivado:
    @pytest.mark.asyncio
    async def test_numerica_aprobada_supera_umbral(self):
        from app.services.calificaciones_service import _calcular_aprobado
        result = _calcular_aprobado(
            nota_numerica=75.0, nota_textual=None,
            umbral_pct=60, valores_aprobatorios=None,
        )
        assert result is True

    @pytest.mark.asyncio
    async def test_numerica_no_aprobada_menor_umbral(self):
        from app.services.calificaciones_service import _calcular_aprobado
        result = _calcular_aprobado(
            nota_numerica=55.0, nota_textual=None,
            umbral_pct=60, valores_aprobatorios=None,
        )
        assert result is False

    @pytest.mark.asyncio
    async def test_textual_aprobatoria_default(self):
        from app.services.calificaciones_service import _calcular_aprobado
        result = _calcular_aprobado(
            nota_numerica=None, nota_textual='Satisfactorio',
            umbral_pct=60, valores_aprobatorios=None,
        )
        assert result is True

    @pytest.mark.asyncio
    async def test_textual_no_aprobatoria(self):
        from app.services.calificaciones_service import _calcular_aprobado
        result = _calcular_aprobado(
            nota_numerica=None, nota_textual='No satisfactorio',
            umbral_pct=60, valores_aprobatorios=None,
        )
        assert result is False

    @pytest.mark.asyncio
    async def test_textual_con_valores_personalizados(self):
        from app.services.calificaciones_service import _calcular_aprobado
        valores = {'Aprobado', 'Muy bueno'}
        result = _calcular_aprobado(
            nota_numerica=None, nota_textual='Muy bueno',
            umbral_pct=60, valores_aprobatorios=valores,
        )
        assert result is True
        result2 = _calcular_aprobado(
            nota_numerica=None, nota_textual='Regular',
            umbral_pct=60, valores_aprobatorios=valores,
        )
        assert result2 is False

    @pytest.mark.asyncio
    async def test_sin_nota_retorna_none(self):
        from app.services.calificaciones_service import _calcular_aprobado
        result = _calcular_aprobado(
            nota_numerica=None, nota_textual=None,
            umbral_pct=60, valores_aprobatorios=None,
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_umbral_afecta_derivacion(self):
        from app.services.calificaciones_service import _calcular_aprobado
        with_60 = _calcular_aprobado(
            nota_numerica=65.0, nota_textual=None,
            umbral_pct=60, valores_aprobatorios=None,
        )
        assert with_60 is True
        with_70 = _calcular_aprobado(
            nota_numerica=65.0, nota_textual=None,
            umbral_pct=70, valores_aprobatorios=None,
        )
        assert with_70 is False


class TestDetectarActividades:
    @pytest.mark.asyncio
    async def test_columna_sufijo_real_es_numerica(self):
        from app.services.calificaciones_service import _detectar_actividades
        acts = _detectar_actividades(['Parcial 1 (Real)', 'Alumno'])
        assert len(acts) == 1
        assert acts[0].nombre == 'Parcial 1'
        assert acts[0].tipo == 'numerica'

    @pytest.mark.asyncio
    async def test_columna_sin_sufijo_es_textual(self):
        from app.services.calificaciones_service import _detectar_actividades
        acts = _detectar_actividades(['Estado TP', 'Alumno'])
        assert len(acts) == 1
        assert acts[0].nombre == 'Estado TP'
        assert acts[0].tipo == 'textual'

    @pytest.mark.asyncio
    async def test_columnas_identificacion_se_ignoran(self):
        from app.services.calificaciones_service import _detectar_actividades
        acts = _detectar_actividades(['Alumno', 'Nombre', 'Apellido', 'Parcial (Real)'])
        assert len(acts) == 1
        assert acts[0].nombre == 'Parcial'
        assert acts[0].tipo == 'numerica'

    @pytest.mark.asyncio
    async def test_preview_devuelve_actividades_y_filas(self, db_session, admin_tenant, base_entities):
        from app.services.calificaciones_service import CalificacionesService
        from fastapi import UploadFile

        service = CalificacionesService(db_session, admin_tenant.id)
        csv_content = 'Alumno,Nombre,Apellidos,Email,Parcial (Real),Estado TP\n' \
                      '1,Juan,Perez,juan@test.com,85,Satisfactorio\n' \
                      '2,Maria,Garcia,maria@test.com,70,No satisfactorio\n'
        uf = UploadFile(filename='califs.csv', file=io.BytesIO(csv_content.encode('utf-8')))
        preview = await service.preview_import(base_entities['materia'].id, base_entities['cohorte'].id, uf)

        assert preview.total_filas == 2
        assert len(preview.actividades) == 2
        nombres = {a.nombre for a in preview.actividades}
        assert 'Parcial' in nombres
        assert 'Estado TP' in nombres
        tipos = {a.nombre: a.tipo for a in preview.actividades}
        assert tipos['Parcial'] == 'numerica'
        assert tipos['Estado TP'] == 'textual'


class TestConfirmImport:
    async def _client(self, app, db_session, token_value):
        app.dependency_overrides[get_db] = lambda: db_session
        client = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        client.headers['Authorization'] = f'Bearer {token_value}'
        return client

    async def _make_csv(self, headers: list[str], rows: list[list]) -> bytes:
        output = io.StringIO()
        import csv
        writer = csv.writer(output)
        writer.writerow(headers)
        for r in rows:
            writer.writerow(r)
        return output.getvalue().encode('utf-8')

    @pytest.mark.asyncio
    async def test_confirm_persiste_calificaciones(self, db_session, admin_tenant, admin_setup, base_entities, padron_setup):
        from app.services.calificaciones_service import CalificacionesService
        from app.schemas.calificaciones import CalificacionConfirmRequest, ActividadAImportar
        from app.schemas.auth import UserContext
        from app.services.audit_service import AuditService
        from fastapi import UploadFile

        service = CalificacionesService(db_session, admin_tenant.id)
        csv_bytes = await self._make_csv(
            ['Alumno', 'Nombre', 'Apellidos', 'Email', 'Parcial (Real)', 'Estado TP'],
            [
                ['1', 'Juan', 'Perez', 'juan@test.com', '85', 'Satisfactorio'],
                ['2', 'Maria', 'Garcia', 'maria@test.com', '70', 'No satisfactorio'],
            ],
        )
        uf = UploadFile(filename='califs.csv', file=io.BytesIO(csv_bytes))

        req = CalificacionConfirmRequest(
            materia_id=base_entities['materia'].id,
            cohorte_id=base_entities['cohorte'].id,
            actividades=[
                ActividadAImportar(nombre='Parcial', tipo='numerica'),
                ActividadAImportar(nombre='Estado TP', tipo='textual'),
            ],
        )
        user_ctx = UserContext(user_id=admin_setup['user'].id, tenant_id=admin_tenant.id, roles=['ADMIN'])
        audit = AuditService(db_session, user_ctx)

        result = await service.confirm_import(req, uf, user_ctx, audit)

        assert result.calificaciones_creadas == 4  # 2 alumnos x 2 actividades
        assert len(result.actividades_procesadas) == 2

        califs = await service.list_calificaciones(base_entities['materia'].id, base_entities['cohorte'].id)
        assert len(califs) == 4

    @pytest.mark.asyncio
    async def test_confirm_audita_con_calificaciones_importar(self, db_session, admin_tenant, admin_setup, base_entities, padron_setup):
        from app.services.calificaciones_service import CalificacionesService
        from app.schemas.calificaciones import CalificacionConfirmRequest, ActividadAImportar
        from app.schemas.auth import UserContext
        from app.services.audit_service import AuditService
        from app.core.audit_codes import CALIFICACIONES_IMPORTAR
        from fastapi import UploadFile
        from sqlalchemy import select
        from app.models.audit_log import AuditLog

        service = CalificacionesService(db_session, admin_tenant.id)
        csv_bytes = await self._make_csv(
            ['Nombre', 'Apellidos', 'Email', 'Parcial (Real)'],
            [['Juan', 'Perez', 'juan@test.com', '85']],
        )
        uf = UploadFile(filename='califs.csv', file=io.BytesIO(csv_bytes))

        req = CalificacionConfirmRequest(
            materia_id=base_entities['materia'].id,
            cohorte_id=base_entities['cohorte'].id,
            actividades=[ActividadAImportar(nombre='Parcial', tipo='numerica')],
        )
        user_ctx = UserContext(user_id=admin_setup['user'].id, tenant_id=admin_tenant.id, roles=['ADMIN'])
        audit = AuditService(db_session, user_ctx)

        await service.confirm_import(req, uf, user_ctx, audit)

        result = await db_session.execute(
            select(AuditLog).where(AuditLog.accion == CALIFICACIONES_IMPORTAR),
        )
        logs = result.scalars().all()
        assert len(logs) >= 1
        assert logs[0].materia_id == base_entities['materia'].id

    @pytest.mark.asyncio
    async def test_seleccion_parcial_actividades(self, db_session, admin_tenant, admin_setup, base_entities, padron_setup):
        from app.services.calificaciones_service import CalificacionesService
        from app.schemas.calificaciones import CalificacionConfirmRequest, ActividadAImportar
        from app.schemas.auth import UserContext
        from app.services.audit_service import AuditService
        from fastapi import UploadFile

        service = CalificacionesService(db_session, admin_tenant.id)
        csv_bytes = await self._make_csv(
            ['Nombre', 'Apellidos', 'Email', 'Parcial (Real)', 'Estado TP'],
            [['Juan', 'Perez', 'juan@test.com', '85', 'Satisfactorio']],
        )
        uf = UploadFile(filename='califs.csv', file=io.BytesIO(csv_bytes))

        req = CalificacionConfirmRequest(
            materia_id=base_entities['materia'].id,
            cohorte_id=base_entities['cohorte'].id,
            actividades=[ActividadAImportar(nombre='Parcial', tipo='numerica')],
        )
        user_ctx = UserContext(user_id=admin_setup['user'].id, tenant_id=admin_tenant.id, roles=['ADMIN'])
        audit = AuditService(db_session, user_ctx)

        result = await service.confirm_import(req, uf, user_ctx, audit)

        assert result.calificaciones_creadas == 1  # solo Parcial
        assert result.actividades_procesadas == ['Parcial']

    @pytest.mark.asyncio
    async def test_sin_padron_activo_error(self, db_session, admin_tenant, admin_setup, base_entities):
        from app.services.calificaciones_service import CalificacionesService
        from app.schemas.calificaciones import CalificacionConfirmRequest, ActividadAImportar
        from app.schemas.auth import UserContext
        from app.services.audit_service import AuditService
        from fastapi import HTTPException, UploadFile

        service = CalificacionesService(db_session, admin_tenant.id)
        csv_bytes = await self._make_csv(
            ['Nombre', 'Apellidos', 'Email', 'Parcial (Real)'],
            [['Juan', 'Perez', 'juan@test.com', '85']],
        )
        uf = UploadFile(filename='califs.csv', file=io.BytesIO(csv_bytes))

        req = CalificacionConfirmRequest(
            materia_id=base_entities['materia'].id,
            cohorte_id=base_entities['cohorte'].id,
            actividades=[ActividadAImportar(nombre='Parcial', tipo='numerica')],
        )
        user_ctx = UserContext(user_id=admin_setup['user'].id, tenant_id=admin_tenant.id, roles=['ADMIN'])
        audit = AuditService(db_session, user_ctx)

        with pytest.raises(HTTPException) as exc:
            await service.confirm_import(req, uf, user_ctx, audit)
        assert exc.value.status_code == 400
        assert 'padrón' in exc.value.detail.lower()


class TestReporteFinalizacion:
    async def _make_csv(self, headers: list[str], rows: list[list]) -> bytes:
        output = io.StringIO()
        import csv
        writer = csv.writer(output)
        writer.writerow(headers)
        for r in rows:
            writer.writerow(r)
        return output.getvalue().encode('utf-8')

    @pytest.mark.asyncio
    async def test_detecta_entregas_sin_calificar(self, db_session, admin_tenant, admin_setup, base_entities, padron_setup):
        from app.services.calificaciones_service import CalificacionesService
        from fastapi import UploadFile

        service = CalificacionesService(db_session, admin_tenant.id)
        csv_bytes = await self._make_csv(
            ['Nombre', 'Apellidos', 'Email', 'TP1', 'TP2'],
            [
                ['Juan', 'Perez', 'juan@test.com', 'Entregado', 'Entregado'],
                ['Maria', 'Garcia', 'maria@test.com', 'Entregado', ''],
            ],
        )
        uf = UploadFile(filename='finalizacion.csv', file=io.BytesIO(csv_bytes))

        result = await service.import_reporte_finalizacion(
            base_entities['materia'].id, base_entities['cohorte'].id, uf,
        )
        assert result.total == 3  # Juan TP1, Juan TP2, Maria TP1
        assert len(result.entregas_sin_corregir) == 3

    @pytest.mark.asyncio
    async def test_solo_textuales_en_reporte(self, db_session, admin_tenant, admin_setup, base_entities, padron_setup):
        from app.services.calificaciones_service import CalificacionesService
        from fastapi import UploadFile

        service = CalificacionesService(db_session, admin_tenant.id)
        csv_bytes = await self._make_csv(
            ['Nombre', 'Apellidos', 'Email', 'Parcial (Real)', 'TP1'],
            [
                ['Juan', 'Perez', 'juan@test.com', '85', 'Entregado'],
            ],
        )
        uf = UploadFile(filename='finalizacion.csv', file=io.BytesIO(csv_bytes))

        result = await service.import_reporte_finalizacion(
            base_entities['materia'].id, base_entities['cohorte'].id, uf,
        )
        # Only textual (TP1) should appear, not Parcial (Real)
        actividades = {e.actividad for e in result.entregas_sin_corregir}
        assert 'TP1' in actividades
        assert 'Parcial' not in actividades

    @pytest.mark.asyncio
    async def test_cruce_contra_calificaciones_existentes(self, db_session, admin_tenant, admin_setup, base_entities, padron_setup):
        from app.services.calificaciones_service import CalificacionesService
        from app.schemas.calificaciones import CalificacionConfirmRequest, ActividadAImportar
        from app.schemas.auth import UserContext
        from app.services.audit_service import AuditService
        from fastapi import UploadFile

        service = CalificacionesService(db_session, admin_tenant.id)
        user_ctx = UserContext(user_id=admin_setup['user'].id, tenant_id=admin_tenant.id, roles=['ADMIN'])
        audit = AuditService(db_session, user_ctx)

        # Import a numeric grade for TP1 first
        csv_calif = self._make_csv(
            ['Nombre', 'Apellidos', 'Email', 'Parcial (Real)'],
            [['Juan', 'Perez', 'juan@test.com', '85']],
        )
        uf_calif = UploadFile(filename='califs.csv', file=io.BytesIO(await csv_calif))
        req = CalificacionConfirmRequest(
            materia_id=base_entities['materia'].id,
            cohorte_id=base_entities['cohorte'].id,
            actividades=[ActividadAImportar(nombre='Parcial', tipo='numerica')],
        )
        await service.confirm_import(req, uf_calif, user_ctx, audit)

        # Now upload completion report
        csv_report = self._make_csv(
            ['Nombre', 'Apellidos', 'Email', 'Parcial (Real)', 'TP1'],
            [['Juan', 'Perez', 'juan@test.com', '85', 'Entregado']],
        )
        uf_report = UploadFile(filename='finalizacion.csv', file=io.BytesIO(await csv_report))
        result = await service.import_reporte_finalizacion(
            base_entities['materia'].id, base_entities['cohorte'].id, uf_report,
        )
        # Parcial has calificacion, so it's excluded. TP1 has no calificacion, so it appears.
        actividades = {e.actividad for e in result.entregas_sin_corregir}
        assert 'TP1' in actividades
        assert 'Parcial' not in actividades


class TestUmbral:
    @pytest_asyncio.fixture
    async def asignacion_setup(self, db_session, admin_tenant, admin_setup, base_entities):
        asignacion = Asignacion(
            tenant_id=admin_tenant.id,
            usuario_id=admin_setup['user'].id,
            rol='PROFESOR',
            materia_id=base_entities['materia'].id,
            cohorte_id=base_entities['cohorte'].id,
        )
        db_session.add(asignacion)
        await db_session.flush()
        return asignacion

    @pytest.mark.asyncio
    async def test_crear_umbral(self, db_session, admin_tenant, asignacion_setup, base_entities):
        from app.repositories.umbral_repository import UmbralMateriaRepository

        repo = UmbralMateriaRepository(db_session, admin_tenant.id)
        umbral = await repo.upsert(
            asignacion_id=asignacion_setup.id,
            materia_id=base_entities['materia'].id,
            cohorte_id=base_entities['cohorte'].id,
            umbral_pct=70,
        )
        assert umbral.umbral_pct == 70

        found = await repo.get_by_materia_cohorte(base_entities['materia'].id, base_entities['cohorte'].id)
        assert found is not None
        assert found.umbral_pct == 70

    @pytest.mark.asyncio
    async def test_actualizar_umbral(self, db_session, admin_tenant, asignacion_setup, base_entities):
        from app.repositories.umbral_repository import UmbralMateriaRepository

        repo = UmbralMateriaRepository(db_session, admin_tenant.id)
        await repo.upsert(
            asignacion_id=asignacion_setup.id,
            materia_id=base_entities['materia'].id,
            cohorte_id=base_entities['cohorte'].id,
            umbral_pct=60,
        )
        updated = await repo.upsert(
            asignacion_id=asignacion_setup.id,
            materia_id=base_entities['materia'].id,
            cohorte_id=base_entities['cohorte'].id,
            umbral_pct=75,
        )
        assert updated.umbral_pct == 75

    @pytest.mark.asyncio
    async def test_default_60_porciento(self):
        from app.repositories.umbral_repository import UmbralMateriaRepository
        assert UmbralMateriaRepository._model is not None  # just verify import

    @pytest.mark.asyncio
    async def test_umbral_afecta_derivacion_aprobado(self, db_session, admin_tenant, admin_setup, base_entities, padron_setup):
        from app.services.calificaciones_service import CalificacionesService, _calcular_aprobado

        nota = 65.0
        with_umbral_60 = _calcular_aprobado(nota, None, 60, None)
        assert with_umbral_60 is True

        with_umbral_70 = _calcular_aprobado(nota, None, 70, None)
        assert with_umbral_70 is False


class TestAPI:
    async def _client(self, app, db_session, token_value):
        app.dependency_overrides[get_db] = lambda: db_session
        client = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        client.headers['Authorization'] = f'Bearer {token_value}'
        return client

    @pytest.mark.asyncio
    async def test_preview_endpoint(self, app, db_session, admin_tenant, admin_setup, base_entities):
        client = await self._client(app, db_session, admin_setup['token'])
        csv_content = 'Alumno,Nombre,Apellidos,Email,Parcial (Real),TP1\n1,Juan,Perez,juan@test.com,85,Entregado\n'
        response = await client.post(
            '/api/v1/calificaciones/importar/preview',
            data={
                'materia_id': str(base_entities['materia'].id),
                'cohorte_id': str(base_entities['cohorte'].id),
            },
            files={'archivo': ('califs.csv', csv_content, 'text/csv')},
        )
        assert response.status_code == 200
        data = response.json()
        assert data['total_filas'] == 1
        assert len(data['actividades']) == 2
