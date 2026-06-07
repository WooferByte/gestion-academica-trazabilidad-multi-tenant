import uuid
from datetime import date

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tenant import Tenant
from app.models.user import User
from app.models.cohorte import Cohorte
from app.models.carrera import Carrera
from app.core.security import encrypt, hash_email, hash_password
from app.repositories.salario_base_repository import SalarioBaseRepository
from app.repositories.salario_plus_repository import SalarioPlusRepository
from app.repositories.liquidacion_repository import LiquidacionRepository
from app.repositories.factura_repository import FacturaRepository


@pytest_asyncio.fixture
async def tenant(db_session: AsyncSession):
    t = Tenant(id=uuid.uuid4(), nombre='Test', codigo='TST', estado='Activo')
    db_session.add(t)
    await db_session.flush()
    return t


@pytest_asyncio.fixture
async def user(db_session: AsyncSession, tenant):
    email = 'user@test.com'
    u = User(
        tenant_id=tenant.id, email=email,
        email_cifrado=encrypt(email), email_hash=hash_email(email),
        password_hash=hash_password('pass123'),
        facturador=False, roles=['PROFESOR'], estado='Activo', is_active=True,
    )
    db_session.add(u)
    await db_session.flush()
    return u


@pytest_asyncio.fixture
async def cohorte(db_session: AsyncSession, tenant):
    carrera = Carrera(tenant_id=tenant.id, codigo='ING', nombre='Ingenieria')
    db_session.add(carrera)
    await db_session.flush()
    c = Cohorte(tenant_id=tenant.id, carrera_id=carrera.id, nombre='2026', anio=2026, vig_desde=date(2026, 1, 1))
    db_session.add(c)
    await db_session.flush()
    return c


class TestSalarioBaseRepository:
    @pytest.mark.asyncio
    async def test_create_and_get(self, db_session: AsyncSession, tenant):
        repo = SalarioBaseRepository(db_session, tenant.id)
        sb = await repo.create(rol='PROFESOR', monto=500000, desde=date(2026, 1, 1))
        assert sb.rol == 'PROFESOR'
        assert float(sb.monto) == 500000
        assert sb.desde == date(2026, 1, 1)
        assert sb.hasta is None

    @pytest.mark.asyncio
    async def test_get_vigente_returns_correct(self, db_session: AsyncSession, tenant):
        repo = SalarioBaseRepository(db_session, tenant.id)
        await repo.create(rol='PROFESOR', monto=400000, desde=date(2025, 1, 1), hasta=date(2025, 12, 31))
        await repo.create(rol='PROFESOR', monto=500000, desde=date(2026, 1, 1))
        vigente = await repo.get_vigente('PROFESOR', date(2026, 6, 1))
        assert vigente is not None
        assert float(vigente.monto) == 500000

    @pytest.mark.asyncio
    async def test_get_vigente_returns_none_if_no_match(self, db_session: AsyncSession, tenant):
        repo = SalarioBaseRepository(db_session, tenant.id)
        await repo.create(rol='PROFESOR', monto=500000, desde=date(2026, 1, 1), hasta=date(2026, 6, 30))
        vigente = await repo.get_vigente('PROFESOR', date(2026, 9, 1))
        assert vigente is None

    @pytest.mark.asyncio
    async def test_cerrar_vigencia(self, db_session: AsyncSession, tenant):
        repo = SalarioBaseRepository(db_session, tenant.id)
        sb = await repo.create(rol='TUTOR', monto=300000, desde=date(2026, 1, 1))
        await repo.cerrar_vigencia(sb.id, date(2026, 6, 30))
        updated = await repo.get(sb.id)
        assert updated is not None
        assert updated.hasta == date(2026, 6, 30)

    @pytest.mark.asyncio
    async def test_get_vigente_sin_hasta(self, db_session: AsyncSession, tenant):
        repo = SalarioBaseRepository(db_session, tenant.id)
        await repo.create(rol='NEXO', monto=350000, desde=date(2026, 1, 1))
        sin_hasta = await repo.get_vigente_sin_hasta('NEXO')
        assert sin_hasta is not None
        assert float(sin_hasta.monto) == 350000


class TestSalarioPlusRepository:
    @pytest.mark.asyncio
    async def test_create_and_get(self, db_session: AsyncSession, tenant):
        repo = SalarioPlusRepository(db_session, tenant.id)
        sp = await repo.create(grupo='PROG', rol='TUTOR', monto=100000, desde=date(2026, 1, 1))
        assert sp.grupo == 'PROG'
        assert sp.rol == 'TUTOR'
        assert float(sp.monto) == 100000

    @pytest.mark.asyncio
    async def test_get_vigente(self, db_session: AsyncSession, tenant):
        repo = SalarioPlusRepository(db_session, tenant.id)
        await repo.create(grupo='PROG', rol='TUTOR', monto=80000, desde=date(2025, 1, 1), hasta=date(2025, 12, 31))
        await repo.create(grupo='PROG', rol='TUTOR', monto=100000, desde=date(2026, 1, 1))
        vigente = await repo.get_vigente('PROG', 'TUTOR', date(2026, 6, 1))
        assert vigente is not None
        assert float(vigente.monto) == 100000

    @pytest.mark.asyncio
    async def test_get_vigente_no_match(self, db_session: AsyncSession, tenant):
        repo = SalarioPlusRepository(db_session, tenant.id)
        result = await repo.get_vigente('BD', 'PROFESOR', date(2026, 6, 1))
        assert result is None

    @pytest.mark.asyncio
    async def test_list_por_grupo(self, db_session: AsyncSession, tenant):
        repo = SalarioPlusRepository(db_session, tenant.id)
        await repo.create(grupo='PROG', rol='TUTOR', monto=100000, desde=date(2026, 1, 1))
        await repo.create(grupo='BD', rol='TUTOR', monto=90000, desde=date(2026, 1, 1))
        prog_only = await repo.list_por_grupo(grupo='PROG')
        assert len(prog_only) == 1
        assert prog_only[0].grupo == 'PROG'


class TestLiquidacionRepository:
    @pytest.mark.asyncio
    async def test_create_and_get(self, db_session: AsyncSession, tenant, user, cohorte):
        repo = LiquidacionRepository(db_session, tenant.id)
        liqui = await repo.create(
            usuario_id=user.id, cohorte_id=cohorte.id,
            periodo='2026-04', rol='PROFESOR',
            monto_base=500000, monto_plus=100000, total=600000,
            es_nexo=False, excluido_por_factura=False, estado='Abierta',
        )
        assert liqui.periodo == '2026-04'
        assert float(liqui.total) == 600000

    @pytest.mark.asyncio
    async def test_filter_by_cohorte_periodo(self, db_session: AsyncSession, tenant, user, cohorte):
        repo = LiquidacionRepository(db_session, tenant.id)
        await repo.create(usuario_id=user.id, cohorte_id=cohorte.id, periodo='2026-04', rol='PROFESOR', monto_base=500000, monto_plus=0, total=500000, es_nexo=False, excluido_por_factura=False, estado='Abierta')
        await repo.create(usuario_id=user.id, cohorte_id=cohorte.id, periodo='2026-04', rol='TUTOR', monto_base=300000, monto_plus=0, total=300000, es_nexo=False, excluido_por_factura=False, estado='Abierta')
        result = await repo.get_by_cohorte_periodo(cohorte.id, '2026-04')
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_cerrar_lote(self, db_session: AsyncSession, tenant, user, cohorte):
        repo = LiquidacionRepository(db_session, tenant.id)
        await repo.create(usuario_id=user.id, cohorte_id=cohorte.id, periodo='2026-04', rol='PROFESOR', monto_base=500000, monto_plus=0, total=500000, es_nexo=False, excluido_por_factura=False, estado='Abierta')
        cerradas = await repo.cerrar_lote(cohorte.id, '2026-04')
        assert cerradas == 1
        liquis = await repo.get_by_cohorte_periodo(cohorte.id, '2026-04')
        assert liquis[0].estado == 'Cerrada'

    @pytest.mark.asyncio
    async def test_reject_write_on_closed(self, db_session: AsyncSession, tenant, user, cohorte):
        repo = LiquidacionRepository(db_session, tenant.id)
        liqui = await repo.create(usuario_id=user.id, cohorte_id=cohorte.id, periodo='2026-04', rol='PROFESOR', monto_base=500000, monto_plus=0, total=500000, es_nexo=False, excluido_por_factura=False, estado='Abierta')
        await repo.cerrar_lote(cohorte.id, '2026-04')
        with pytest.raises(Exception) as exc_info:
            await repo.reject_if_closed(liqui.id)
        assert exc_info.value.status_code == 409


class TestFacturaRepository:
    @pytest.mark.asyncio
    async def test_create_and_get(self, db_session: AsyncSession, tenant, user):
        repo = FacturaRepository(db_session, tenant.id)
        f = await repo.create(usuario_id=user.id, periodo='2026-04', detalle='Factura test', estado='Pendiente')
        assert f.periodo == '2026-04'
        assert f.estado == 'Pendiente'

    @pytest.mark.asyncio
    async def test_update_estado_sets_abonada_at(self, db_session: AsyncSession, tenant, user):
        repo = FacturaRepository(db_session, tenant.id)
        f = await repo.create(usuario_id=user.id, periodo='2026-04', detalle='Factura test', estado='Pendiente')
        updated = await repo.update_estado(f.id, 'Abonada')
        assert updated is not None
        assert updated.estado == 'Abonada'
        assert updated.abonada_at is not None

    @pytest.mark.asyncio
    async def test_filter_by_usuario(self, db_session: AsyncSession, tenant, user):
        repo = FacturaRepository(db_session, tenant.id)
        await repo.create(usuario_id=user.id, periodo='2026-04', detalle='F1', estado='Pendiente')
        result = await repo.list(usuario_id=user.id)
        assert len(result) == 1
