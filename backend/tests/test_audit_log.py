import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select, text

from app.core.audit_codes import (
    ASIGNACION_MODIFICAR,
    CALIFICACIONES_IMPORTAR,
    COMUNICACION_ENVIAR,
    IMPERSONACION_FINALIZAR,
    IMPERSONACION_INICIAR,
    LIQUIDACION_CERRAR,
    PADRON_CARGAR,
)
from app.core.dependencies import get_db
from app.core.security import create_access_token, decode_token
from app.main import create_app
from app.models.audit_log import AuditLog
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.tenant import Tenant
from app.models.user import User
from app.models.user_role import UserRole
from app.repositories.audit_repository import AuditRepository
from app.schemas.auth import UserContext
from app.services.audit_service import AuditService


@pytest_asyncio.fixture
async def tenant(db_session):
    t = Tenant(nombre='Test', codigo='TST', estado='Activo')
    db_session.add(t)
    await db_session.flush()
    return t


@pytest_asyncio.fixture
async def admin_user(db_session, tenant):
    user = User(
        tenant_id=tenant.id,
        email='admin@test.com',
        password_hash='hash',
        roles=['ADMIN'],
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def regular_user(db_session, tenant):
    user = User(
        tenant_id=tenant.id,
        email='user@test.com',
        password_hash='hash',
        roles=['ALUMNO'],
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def admin_role(db_session, tenant):
    role = Role(tenant_id=tenant.id, name='Admin', codigo='ADMIN')
    db_session.add(role)
    await db_session.flush()
    return role


@pytest_asyncio.fixture
async def impersonation_perm(db_session, tenant):
    perm = Permission(
        tenant_id=tenant.id,
        codigo='impersonacion:usar',
        descripcion='Iniciar sesión de impersonación',
        modulo='impersonacion',
        accion='usar',
    )
    db_session.add(perm)
    await db_session.flush()
    return perm


@pytest_asyncio.fixture
async def admin_with_impersonation(
    db_session, tenant, admin_user, admin_role, impersonation_perm,
):
    existing_ur = await db_session.execute(
        select(UserRole).where(
            UserRole.user_id == admin_user.id,
            UserRole.role_id == admin_role.id,
            UserRole.tenant_id == tenant.id,
        ),
    )
    if not existing_ur.scalar_one_or_none():
        ur = UserRole(
            tenant_id=tenant.id,
            user_id=admin_user.id,
            role_id=admin_role.id,
        )
        db_session.add(ur)

    existing_rp = await db_session.execute(
        select(RolePermission).where(
            RolePermission.role_id == admin_role.id,
            RolePermission.permiso_id == impersonation_perm.id,
            RolePermission.tenant_id == tenant.id,
        ),
    )
    if not existing_rp.scalar_one_or_none():
        rp = RolePermission(
            tenant_id=tenant.id,
            role_id=admin_role.id,
            permiso_id=impersonation_perm.id,
        )
        db_session.add(rp)

    await db_session.flush()
    return admin_user


class TestAuditLogModel:
    @pytest.mark.asyncio
    async def test_create_audit_entry(self, db_session, tenant, admin_user):
        entry = AuditLog(
            tenant_id=tenant.id,
            actor_id=admin_user.id,
            accion='TEST_ACTION',
            detalle={'key': 'value'},
            filas_afectadas=5,
            ip='192.168.1.1',
            user_agent='pytest',
        )
        db_session.add(entry)
        await db_session.flush()

        assert entry.id is not None
        assert entry.tenant_id == tenant.id
        assert entry.actor_id == admin_user.id
        assert entry.impersonado_id is None
        assert entry.materia_id is None
        assert entry.accion == 'TEST_ACTION'
        assert entry.detalle == {'key': 'value'}
        assert entry.filas_afectadas == 5
        assert entry.ip == '192.168.1.1'
        assert entry.user_agent == 'pytest'
        assert entry.fecha_hora is not None

    @pytest.mark.asyncio
    async def test_audit_entry_minimal_fields(self, db_session, tenant, admin_user):
        entry = AuditLog(
            tenant_id=tenant.id,
            actor_id=admin_user.id,
            accion='MINIMAL',
            ip='10.0.0.1',
            user_agent='curl',
        )
        db_session.add(entry)
        await db_session.flush()

        assert entry.id is not None
        assert entry.detalle is None
        assert entry.materia_id is None
        assert entry.filas_afectadas == 0

    @pytest.mark.asyncio
    async def test_audit_entry_defaults(self, db_session, tenant, admin_user):
        entry = AuditLog(
            tenant_id=tenant.id,
            actor_id=admin_user.id,
            accion='DEFAULT',
            ip='10.0.0.1',
            user_agent='curl',
        )
        db_session.add(entry)
        await db_session.flush()

        assert entry.filas_afectadas == 0
        assert entry.detalle is None


class TestAuditRepository:
    @pytest.mark.asyncio
    async def test_create_only_no_update_no_delete_methods(self, db_session, tenant, admin_user):
        repo = AuditRepository(db_session, tenant.id)
        entry = AuditLog(
            tenant_id=tenant.id,
            actor_id=admin_user.id,
            accion='REPO_TEST',
            ip='1.1.1.1',
            user_agent='test',
        )
        created = await repo.create(entry)
        assert created.id is not None
        assert not hasattr(repo, 'update')
        assert not hasattr(repo, 'delete')
        assert not hasattr(repo, 'soft_delete')


class TestAuditService:
    @pytest.mark.asyncio
    async def test_log_creates_entry_with_all_fields(self, db_session, tenant, admin_user):
        user_context = UserContext(
            user_id=admin_user.id,
            tenant_id=tenant.id,
            roles=['ADMIN'],
        )
        svc = AuditService(db_session, user_context, ip='10.0.0.1', user_agent='test-agent')

        result = await svc.log(
            accion=CALIFICACIONES_IMPORTAR,
            detalle={'origen': 'moodle', 'comision': 'A'},
            filas_afectadas=30,
        )

        assert result.accion == CALIFICACIONES_IMPORTAR
        assert result.actor_id == admin_user.id
        assert result.tenant_id == tenant.id
        assert result.impersonado_id is None
        assert result.detalle == {'origen': 'moodle', 'comision': 'A'}
        assert result.filas_afectadas == 30
        assert result.ip == '10.0.0.1'
        assert result.user_agent == 'test-agent'

    @pytest.mark.asyncio
    async def test_log_under_impersonation_sets_impersonado_id(self, db_session, tenant, admin_user, regular_user):
        user_context = UserContext(
            user_id=regular_user.id,
            tenant_id=tenant.id,
            roles=['ALUMNO'],
            impersonator_id=admin_user.id,
        )
        svc = AuditService(db_session, user_context, ip='10.0.0.1', user_agent='test-agent')

        result = await svc.log(
            accion=CALIFICACIONES_IMPORTAR,
            detalle={'test': True},
        )

        assert result.actor_id == regular_user.id
        assert result.impersonado_id == admin_user.id


class TestAuditCodes:
    def test_catalog_contains_required_codes(self):
        from app.core import audit_codes as ac

        expected = [
            'CALIFICACIONES_IMPORTAR',
            'PADRON_CARGAR',
            'COMUNICACION_ENVIAR',
            'ASIGNACION_MODIFICAR',
            'LIQUIDACION_CERRAR',
            'IMPERSONACION_INICIAR',
            'IMPERSONACION_FINALIZAR',
        ]
        for code_name in expected:
            assert hasattr(ac, code_name), f'{code_name} not found in audit_codes'

        assert ac.CALIFICACIONES_IMPORTAR == CALIFICACIONES_IMPORTAR
        assert ac.PADRON_CARGAR == PADRON_CARGAR
        assert ac.COMUNICACION_ENVIAR == COMUNICACION_ENVIAR
        assert ac.ASIGNACION_MODIFICAR == ASIGNACION_MODIFICAR
        assert ac.LIQUIDACION_CERRAR == LIQUIDACION_CERRAR
        assert ac.IMPERSONACION_INICIAR == IMPERSONACION_INICIAR
        assert ac.IMPERSONACION_FINALIZAR == IMPERSONACION_FINALIZAR


class TestAppendOnlyConstraint:
    @pytest.mark.asyncio
    async def test_update_via_sql_is_rejected(self, db_session, tenant, admin_user):
        entry = AuditLog(
            tenant_id=tenant.id,
            actor_id=admin_user.id,
            accion='TEST',
            ip='1.1.1.1',
            user_agent='test',
        )
        db_session.add(entry)
        await db_session.flush()

        entry_id = entry.id
        db_session.expire_all()

        with pytest.raises(Exception) as excinfo:
            await db_session.execute(
                text("UPDATE audit_log SET accion = 'CHANGED' WHERE id = :id"),
                {'id': entry_id},
            )
            await db_session.flush()

        error_msg = str(excinfo.value).lower()
        assert 'append-only' in error_msg

    @pytest.mark.asyncio
    async def test_delete_via_sql_is_rejected(self, db_session, tenant, admin_user):
        entry = AuditLog(
            tenant_id=tenant.id,
            actor_id=admin_user.id,
            accion='TEST',
            ip='1.1.1.1',
            user_agent='test',
        )
        db_session.add(entry)
        await db_session.flush()

        entry_id = entry.id
        db_session.expire_all()

        with pytest.raises(Exception) as excinfo:
            await db_session.execute(
                text("DELETE FROM audit_log WHERE id = :id"),
                {'id': entry_id},
            )
            await db_session.flush()

        error_msg = str(excinfo.value).lower()
        assert 'append-only' in error_msg


class TestUserContextImpersonation:
    @pytest.mark.asyncio
    async def test_token_without_impersonator_id(self, tenant, admin_user):
        token = create_access_token(
            user_id=str(admin_user.id),
            tenant_id=str(tenant.id),
            roles=['ADMIN'],
        )

        payload = decode_token(token)
        assert 'impersonator_id' not in payload
        assert payload['sub'] == str(admin_user.id)

    @pytest.mark.asyncio
    async def test_token_with_impersonator_id(self, tenant, admin_user, regular_user):
        token = create_access_token(
            user_id=str(regular_user.id),
            tenant_id=str(tenant.id),
            roles=['ALUMNO'],
            impersonator_id=str(admin_user.id),
        )

        payload = decode_token(token)
        assert payload['sub'] == str(regular_user.id)
        assert payload['impersonator_id'] == str(admin_user.id)
        assert payload['roles'] == ['ALUMNO']


class TestImpersonationPermission:
    @pytest.mark.asyncio
    async def test_impersonacion_usar_exists_and_admin_has_it(
        self, db_session, tenant, admin_with_impersonation, impersonation_perm,
    ):
        result = await db_session.execute(
            select(Permission).where(
                Permission.codigo == 'impersonacion:usar',
                Permission.tenant_id == tenant.id,
            ),
        )
        perm = result.scalar_one_or_none()
        assert perm is not None
        assert perm.modulo == 'impersonacion'
        assert perm.accion == 'usar'


class TestImpersonationAPI:
    @pytest.mark.asyncio
    async def test_impersonate_without_permission_returns_403(
        self, db_session, tenant, regular_user, admin_user,
    ):
        token = create_access_token(
            user_id=str(regular_user.id),
            tenant_id=str(tenant.id),
            roles=['ALUMNO'],
        )

        app = create_app()
        app.dependency_overrides[get_db] = lambda: db_session
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.post(
                '/api/v1/auth/impersonate',
                json={'target_user_id': str(admin_user.id)},
                headers={'Authorization': f'Bearer {token}'},
            )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_impersonate_self_returns_400(
        self, db_session, tenant, admin_with_impersonation,
    ):
        token = create_access_token(
            user_id=str(admin_with_impersonation.id),
            tenant_id=str(tenant.id),
            roles=['ADMIN'],
        )

        app = create_app()
        app.dependency_overrides[get_db] = lambda: db_session
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.post(
                '/api/v1/auth/impersonate',
                json={'target_user_id': str(admin_with_impersonation.id)},
                headers={'Authorization': f'Bearer {token}'},
            )

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_impersonate_nonexistent_user_returns_404(
        self, db_session, tenant, admin_with_impersonation,
    ):
        token = create_access_token(
            user_id=str(admin_with_impersonation.id),
            tenant_id=str(tenant.id),
            roles=['ADMIN'],
        )

        app = create_app()
        app.dependency_overrides[get_db] = lambda: db_session
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.post(
                '/api/v1/auth/impersonate',
                json={'target_user_id': str(uuid.uuid4())},
                headers={'Authorization': f'Bearer {token}'},
            )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_impersonate_stop_without_impersonation_returns_400(
        self, db_session, tenant, admin_with_impersonation,
    ):
        token = create_access_token(
            user_id=str(admin_with_impersonation.id),
            tenant_id=str(tenant.id),
            roles=['ADMIN'],
        )

        app = create_app()
        app.dependency_overrides[get_db] = lambda: db_session
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.post(
                '/api/v1/auth/impersonate/stop',
                headers={'Authorization': f'Bearer {token}'},
            )

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_impersonation_creates_audit_log(
        self, db_session, tenant, admin_with_impersonation, regular_user,
    ):
        token = create_access_token(
            user_id=str(admin_with_impersonation.id),
            tenant_id=str(tenant.id),
            roles=['ADMIN'],
        )

        app = create_app()
        app.dependency_overrides[get_db] = lambda: db_session
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.post(
                '/api/v1/auth/impersonate',
                json={'target_user_id': str(regular_user.id)},
                headers={'Authorization': f'Bearer {token}'},
            )

        assert response.status_code == 200, f'Expected 200, got {response.status_code}: {response.text}'

        data = response.json()
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert data['token_type'] == 'bearer'

        payload = decode_token(data['access_token'])
        assert payload['sub'] == str(regular_user.id)
        assert payload['impersonator_id'] == str(admin_with_impersonation.id)

        audit_result = await db_session.execute(
            select(AuditLog).where(
                AuditLog.actor_id == admin_with_impersonation.id,
                AuditLog.accion == IMPERSONACION_INICIAR,
            ),
        )
        audit_entry = audit_result.scalar_one_or_none()
        assert audit_entry is not None
        assert audit_entry.impersonado_id is None
        assert audit_entry.detalle is not None
        assert audit_entry.detalle.get('target_user_id') == str(regular_user.id)

    @pytest.mark.asyncio
    async def test_impersonation_stop_creates_audit_log(
        self, db_session, tenant, admin_with_impersonation, regular_user,
    ):
        token = create_access_token(
            user_id=str(regular_user.id),
            tenant_id=str(tenant.id),
            roles=[],
            impersonator_id=str(admin_with_impersonation.id),
        )

        app = create_app()
        app.dependency_overrides[get_db] = lambda: db_session
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url='http://test') as client:
            response = await client.post(
                '/api/v1/auth/impersonate/stop',
                headers={'Authorization': f'Bearer {token}'},
            )

        assert response.status_code == 200, f'Expected 200, got {response.status_code}: {response.text}'

        data = response.json()
        assert 'access_token' in data

        audit_result = await db_session.execute(
            select(AuditLog).where(
                AuditLog.actor_id == regular_user.id,
                AuditLog.accion == IMPERSONACION_FINALIZAR,
            ),
        )
        audit_entry = audit_result.scalar_one_or_none()
        assert audit_entry is not None
        assert audit_entry.impersonado_id == admin_with_impersonation.id
