import io
import uuid
from datetime import datetime, timezone

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.core.audit_codes import PADRON_CARGAR
from app.core.dependencies import get_db
from app.core.security import create_access_token, encrypt, hash_email, hash_password
from app.models.audit_log import AuditLog
from app.models.carrera import Carrera
from app.models.cohorte import Cohorte
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

    p_padron = Permission(
        tenant_id=tid, codigo='padron:cargar', modulo='padron', accion='cargar',
    )
    db_session.add(p_padron)
    await db_session.flush()

    db_session.add_all([
        RolePermission(tenant_id=tid, role_id=role_admin.id, permiso_id=p_padron.id),
        UserRole(tenant_id=tid, user_id=user.id, role_id=role_admin.id),
    ])
    await db_session.flush()

    token = create_access_token(str(user.id), str(tid), ['ADMIN'])
    return {'token': token, 'tid': tid, 'user': user}


@pytest_asyncio.fixture
async def base_entiites(db_session, admin_tenant):
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


class TestVersionado:
    async def _client(self, app, db_session, token_value):
        app.dependency_overrides[get_db] = lambda: db_session
        client = AsyncClient(transport=ASGITransport(app=app), base_url='http://test')
        client.headers['Authorization'] = f'Bearer {token_value}'
        return client

    @pytest.mark.asyncio
    async def test_crear_version_activa(self, db_session, admin_tenant, admin_setup, base_entiites):
        from app.repositories.padron_repository import VersionPadronRepository
        repo = VersionPadronRepository(db_session, admin_tenant.id)

        v1 = await repo.create(
            materia_id=base_entiites['materia'].id,
            cohorte_id=base_entiites['cohorte'].id,
            cargado_por=admin_setup['user'].id,
            activa=True,
        )
        assert v1.activa is True
        assert v1.materia_id == base_entiites['materia'].id
        assert v1.cohorte_id == base_entiites['cohorte'].id

        activa = await repo.get_activa(base_entiites['materia'].id, base_entiites['cohorte'].id)
        assert activa is not None
        assert activa.id == v1.id

    @pytest.mark.asyncio
    async def test_crear_segunda_version_desactiva_primera(self, db_session, admin_tenant, admin_setup, base_entiites):
        from app.repositories.padron_repository import VersionPadronRepository
        repo = VersionPadronRepository(db_session, admin_tenant.id)

        v1 = await repo.create(
            materia_id=base_entiites['materia'].id,
            cohorte_id=base_entiites['cohorte'].id,
            cargado_por=admin_setup['user'].id,
            activa=True,
        )
        await repo.desactivar_version(v1.id)

        v2 = await repo.create(
            materia_id=base_entiites['materia'].id,
            cohorte_id=base_entiites['cohorte'].id,
            cargado_por=admin_setup['user'].id,
            activa=True,
        )

        await db_session.refresh(v1)
        assert v1.activa is False
        assert v2.activa is True

        activa = await repo.get_activa(base_entiites['materia'].id, base_entiites['cohorte'].id)
        assert activa.id == v2.id

    @pytest.mark.asyncio
    async def test_aislamiento_entre_pares_materia_cohorte(self, db_session, admin_tenant, admin_setup, base_entiites):
        from app.repositories.padron_repository import VersionPadronRepository
        repo = VersionPadronRepository(db_session, admin_tenant.id)

        cohorte2 = Cohorte(
            tenant_id=admin_tenant.id, carrera_id=base_entiites['carrera'].id,
            nombre='2027', anio=2027,
            vig_desde=datetime.now(timezone.utc).date(),
        )
        db_session.add(cohorte2)
        await db_session.flush()

        v1 = await repo.create(
            materia_id=base_entiites['materia'].id,
            cohorte_id=base_entiites['cohorte'].id,
            cargado_por=admin_setup['user'].id,
            activa=True,
        )

        v2 = await repo.create(
            materia_id=base_entiites['materia'].id,
            cohorte_id=cohorte2.id,
            cargado_por=admin_setup['user'].id,
            activa=True,
        )

        await db_session.refresh(v1)
        assert v1.activa is True
        assert v2.activa is True


class TestImportService:
    async def _make_csv(self, rows: list[dict]) -> tuple[bytes, str]:
        import csv
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=['nombre', 'apellidos', 'email', 'comision', 'regional'])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
        return output.getvalue().encode('utf-8'), 'alumnos.csv'

    @pytest.mark.asyncio
    async def test_preview_retorna_items_sin_persistir(self, db_session, admin_tenant, base_entiites):
        from app.services.padron_service import PadronService
        from fastapi import UploadFile

        service = PadronService(db_session, admin_tenant.id)
        csv_content, filename = await self._make_csv([
            {'nombre': 'Juan', 'apellidos': 'Perez', 'email': 'juan@test.com', 'comision': 'A', 'regional': 'CABA'},
            {'nombre': 'Maria', 'apellidos': 'Garcia', 'email': 'maria@test.com', 'comision': 'B', 'regional': 'GBA'},
            {'nombre': 'Carlos', 'apellidos': 'Lopez', 'email': 'carlos@test.com', 'comision': 'A', 'regional': 'Interior'},
        ])
        uf = UploadFile(filename=filename, file=io.BytesIO(csv_content))
        preview = await service.preview_import(base_entiites['materia'].id, base_entiites['cohorte'].id, uf)

        assert preview.total == 3
        assert len(preview.items) == 3
        assert preview.items[0].nombre == 'Juan'
        assert preview.items[1].email == 'maria@test.com'

        # Verify nothing persisted
        from app.repositories.padron_repository import VersionPadronRepository
        vrepo = VersionPadronRepository(db_session, admin_tenant.id)
        activa = await vrepo.get_activa(base_entiites['materia'].id, base_entiites['cohorte'].id)
        assert activa is None

    @pytest.mark.asyncio
    async def test_confirm_import_persiste_version_y_entradas(self, db_session, admin_tenant, admin_setup, base_entiites):
        from app.schemas.auth import UserContext
        from app.schemas.padron import ImportPreviewItem
        from app.services.audit_service import AuditService
        from app.services.padron_service import PadronService

        service = PadronService(db_session, admin_tenant.id)
        items = [
            ImportPreviewItem(nombre='Juan', apellidos='Perez', email='juan@test.com', comision='A', regional='CABA'),
        ]

        user_ctx = UserContext(user_id=admin_setup['user'].id, tenant_id=admin_tenant.id, roles=['ADMIN'])
        audit = AuditService(db_session, user_ctx)

        version = await service.confirm_import(
            base_entiites['materia'].id, base_entiites['cohorte'].id, items, user_ctx, audit,
        )

        assert version.activa is True
        assert version.materia_id == base_entiites['materia'].id

        from app.repositories.padron_repository import EntradaPadronRepository
        erepo = EntradaPadronRepository(db_session, admin_tenant.id)
        entradas = await erepo.get_by_version(version.id)
        assert len(entradas) == 1
        assert entradas[0].nombre == 'Juan'

    @pytest.mark.asyncio
    async def test_entrada_sin_usuario_id(self, db_session, admin_tenant, admin_setup, base_entiites):
        from app.schemas.auth import UserContext
        from app.schemas.padron import ImportPreviewItem
        from app.services.audit_service import AuditService
        from app.services.padron_service import PadronService

        email = 'noexiste@test.com'
        service = PadronService(db_session, admin_tenant.id)
        items = [
            ImportPreviewItem(nombre='Sin', apellidos='Cuenta', email=email, comision='A', regional='CABA'),
        ]

        user_ctx = UserContext(user_id=admin_setup['user'].id, tenant_id=admin_tenant.id, roles=['ADMIN'])
        audit = AuditService(db_session, user_ctx)

        version = await service.confirm_import(
            base_entiites['materia'].id, base_entiites['cohorte'].id, items, user_ctx, audit,
        )

        from app.repositories.padron_repository import EntradaPadronRepository
        erepo = EntradaPadronRepository(db_session, admin_tenant.id)
        entradas = await erepo.get_by_version(version.id)
        assert len(entradas) == 1
        assert entradas[0].usuario_id is None
        assert entradas[0].nombre == 'Sin'
        assert entradas[0].email == email

    @pytest.mark.asyncio
    async def test_archivo_formato_invalido(self, db_session, admin_tenant, base_entiites):
        from app.services.padron_service import PadronService
        from fastapi import HTTPException, UploadFile

        service = PadronService(db_session, admin_tenant.id)
        uf = UploadFile(filename='datos.pdf', file=io.BytesIO(b'fake pdf content'))

        with pytest.raises(HTTPException) as exc:
            await service.preview_import(base_entiites['materia'].id, base_entiites['cohorte'].id, uf)
        assert exc.value.status_code == 400
        assert 'no soportado' in exc.value.detail.lower()


class TestVaciar:
    @pytest.mark.asyncio
    async def test_vaciar_materia_soft_delete(self, db_session, admin_tenant, admin_setup, base_entiites):
        from app.repositories.padron_repository import EntradaPadronRepository, VersionPadronRepository
        from app.schemas.auth import UserContext
        from app.schemas.padron import ImportPreviewItem
        from app.services.audit_service import AuditService
        from app.services.padron_service import PadronService

        service = PadronService(db_session, admin_tenant.id)
        items = [
            ImportPreviewItem(nombre='Juan', apellidos='Perez', email='juan@test.com', comision='A', regional='CABA'),
            ImportPreviewItem(nombre='Maria', apellidos='Garcia', email='maria@test.com', comision='B', regional='GBA'),
        ]
        user_ctx = UserContext(user_id=admin_setup['user'].id, tenant_id=admin_tenant.id, roles=['ADMIN'])
        audit = AuditService(db_session, user_ctx)

        version = await service.confirm_import(
            base_entiites['materia'].id, base_entiites['cohorte'].id, items, user_ctx, audit,
        )

        result = await service.vaciar_materia(base_entiites['materia'].id, user_ctx, audit)

        assert result.entradas_afectadas == 2
        assert result.version_desactivada is True

        vrepo = VersionPadronRepository(db_session, admin_tenant.id)
        v = await vrepo.get_with_deleted(version.id)
        await db_session.refresh(v)
        assert v.activa is False

    @pytest.mark.asyncio
    async def test_vaciar_no_afecta_otras_materias(self, db_session, admin_tenant, admin_setup, base_entiites):
        from app.schemas.auth import UserContext
        from app.schemas.padron import ImportPreviewItem
        from app.services.audit_service import AuditService
        from app.services.padron_service import PadronService

        materia2 = Materia(tenant_id=admin_tenant.id, codigo='FIS', nombre='Fisica')
        db_session.add(materia2)
        await db_session.flush()

        service = PadronService(db_session, admin_tenant.id)
        items = [ImportPreviewItem(nombre='Juan', apellidos='Perez', email='juan@test.com', comision='A', regional='CABA')]
        user_ctx = UserContext(user_id=admin_setup['user'].id, tenant_id=admin_tenant.id, roles=['ADMIN'])
        audit = AuditService(db_session, user_ctx)

        v1 = await service.confirm_import(
            base_entiites['materia'].id, base_entiites['cohorte'].id, items, user_ctx, audit,
        )
        v2 = await service.confirm_import(
            materia2.id, base_entiites['cohorte'].id, items, user_ctx, audit,
        )

        await service.vaciar_materia(base_entiites['materia'].id, user_ctx, audit)

        from app.repositories.padron_repository import VersionPadronRepository
        vrepo = VersionPadronRepository(db_session, admin_tenant.id)
        v2_refreshed = await vrepo.get(v2.id)
        assert v2_refreshed is not None

    @pytest.mark.asyncio
    async def test_vaciar_audit(self, db_session, admin_tenant, admin_setup, base_entiites):
        from app.schemas.auth import UserContext
        from app.schemas.padron import ImportPreviewItem
        from app.services.audit_service import AuditService
        from app.services.padron_service import PadronService

        service = PadronService(db_session, admin_tenant.id)
        items = [ImportPreviewItem(nombre='Juan', apellidos='Perez', email='juan@test.com', comision='A', regional='CABA')]
        user_ctx = UserContext(user_id=admin_setup['user'].id, tenant_id=admin_tenant.id, roles=['ADMIN'])
        audit = AuditService(db_session, user_ctx)

        await service.confirm_import(
            base_entiites['materia'].id, base_entiites['cohorte'].id, items, user_ctx, audit,
        )
        await service.vaciar_materia(base_entiites['materia'].id, user_ctx, audit)

        # Check audit log
        from sqlalchemy import select
        result = await db_session.execute(
            select(AuditLog).where(AuditLog.accion == PADRON_CARGAR),
        )
        logs = result.scalars().all()
        assert len(logs) >= 1


class TestMoodleWS:
    @pytest.mark.asyncio
    async def test_skeleton_retorna_mock(self):
        from app.integrations.moodle_ws import MoodleWSClient
        client = MoodleWSClient(url='https://test.com', token='token')
        usuarios = await client.sync_usuarios(uuid.uuid4())
        assert len(usuarios) == 3
        assert usuarios[0]['nombre'] == 'Juan'
        assert usuarios[0]['apellidos'] == 'Pérez'

    @pytest.mark.asyncio
    async def test_moodle_ws_error_502(self):
        from app.integrations.moodle_ws import MoodleWSClient, MoodleWSException
        client = MoodleWSClient(url='https://test.com', token='token')

        class _FailingClient(MoodleWSClient):
            async def sync_usuarios(self, materia_id):
                try:
                    raise ConnectionError('Connection refused')
                except ConnectionError as exc:
                    raise MoodleWSException(str(exc))

        failing = _FailingClient(url='https://test.com', token='token')
        with pytest.raises(MoodleWSException) as exc:
            await failing.sync_usuarios(uuid.uuid4())
        assert 'Connection' in str(exc.value.detail)


class TestAislamientoTenant:
    @pytest.mark.asyncio
    async def test_aislamiento_tenant_import(self, db_session, admin_tenant, admin_setup, base_entiites):
        from app.repositories.padron_repository import VersionPadronRepository

        # Create data for tenant A
        repo_a = VersionPadronRepository(db_session, admin_tenant.id)
        v1 = await repo_a.create(
            materia_id=base_entiites['materia'].id,
            cohorte_id=base_entiites['cohorte'].id,
            cargado_por=admin_setup['user'].id,
            activa=True,
        )
        assert v1 is not None

        # Tenant B should not see it
        other_tenant = uuid.uuid4()
        repo_b = VersionPadronRepository(db_session, other_tenant)
        result = await repo_b.get_activa(base_entiites['materia'].id, base_entiites['cohorte'].id)
        assert result is None
