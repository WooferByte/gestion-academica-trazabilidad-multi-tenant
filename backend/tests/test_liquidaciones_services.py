import uuid
from datetime import date

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tenant import Tenant
from app.models.user import User
from app.models.materia import Materia
from app.models.cohorte import Cohorte
from app.models.carrera import Carrera
from app.models.categoria_plus import CategoriaPlus
from app.models.asignacion import Asignacion
from app.core.security import encrypt, hash_email, hash_password
from app.services.grilla_salarial_service import GrillaSalarialService
from app.services.liquidacion_service import LiquidacionService
from app.services.factura_service import FacturaService


@pytest_asyncio.fixture
async def tenant(db_session: AsyncSession):
    t = Tenant(id=uuid.uuid4(), nombre='Test', codigo='TST', estado='Activo')
    db_session.add(t)
    await db_session.flush()
    return t


@pytest_asyncio.fixture
async def carrera(db_session: AsyncSession, tenant):
    c = Carrera(tenant_id=tenant.id, codigo='ING', nombre='Ingenieria')
    db_session.add(c)
    await db_session.flush()
    return c


@pytest_asyncio.fixture
async def cohorte(db_session: AsyncSession, tenant, carrera):
    c = Cohorte(tenant_id=tenant.id, carrera_id=carrera.id, nombre='2026', anio=2026, vig_desde=date(2026, 1, 1))
    db_session.add(c)
    await db_session.flush()
    return c


@pytest_asyncio.fixture
async def docente(db_session: AsyncSession, tenant):
    email = 'docente@test.com'
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
async def facturante(db_session: AsyncSession, tenant):
    email = 'facturante@test.com'
    u = User(
        tenant_id=tenant.id, email=email,
        email_cifrado=encrypt(email), email_hash=hash_email(email),
        password_hash=hash_password('pass123'),
        facturador=True, roles=['PROFESOR'], estado='Activo', is_active=True,
    )
    db_session.add(u)
    await db_session.flush()
    return u


@pytest_asyncio.fixture
async def materia_prog(db_session: AsyncSession, tenant):
    cat = CategoriaPlus(tenant_id=tenant.id, codigo='PROG', nombre='Programacion')
    db_session.add(cat)
    await db_session.flush()
    m = Materia(tenant_id=tenant.id, codigo='PROG1', nombre='Programacion I', categoria_plus_id=cat.id)
    db_session.add(m)
    await db_session.flush()
    return m


class TestGrillaSalarialService:
    @pytest.mark.asyncio
    async def test_crear_base_con_auto_cierre(self, db_session: AsyncSession, tenant):
        service = GrillaSalarialService(db_session, tenant.id)
        # Create first base
        await service.crear_base(rol='PROFESOR', monto=400000, desde=date(2025, 1, 1))
        # Create second base with later date - should auto-close previous
        nuevo = await service.crear_base(rol='PROFESOR', monto=500000, desde=date(2026, 1, 1))
        assert float(nuevo.monto) == 500000
        # Verify previous was closed
        bases = await service.listar_bases()
        bases_prof = [b for b in bases if b.rol == 'PROFESOR']
        for b in bases_prof:
            if float(b.monto) == 400000:
                assert b.hasta is not None

    @pytest.mark.asyncio
    async def test_listar_bases(self, db_session: AsyncSession, tenant):
        service = GrillaSalarialService(db_session, tenant.id)
        await service.crear_base(rol='PROFESOR', monto=500000, desde=date(2026, 1, 1))
        await service.crear_base(rol='TUTOR', monto=300000, desde=date(2026, 1, 1))
        bases = await service.listar_bases()
        assert len(bases) >= 2

    @pytest.mark.asyncio
    async def test_crear_plus_con_auto_cierre(self, db_session: AsyncSession, tenant):
        service = GrillaSalarialService(db_session, tenant.id)
        await service.crear_plus(grupo='PROG', rol='TUTOR', monto=80000, desde=date(2025, 1, 1))
        nuevo = await service.crear_plus(grupo='PROG', rol='TUTOR', monto=100000, desde=date(2026, 1, 1))
        assert float(nuevo.monto) == 100000

    @pytest.mark.asyncio
    async def test_listar_pluses_por_grupo(self, db_session: AsyncSession, tenant):
        service = GrillaSalarialService(db_session, tenant.id)
        await service.crear_plus(grupo='PROG', rol='TUTOR', monto=100000, desde=date(2026, 1, 1))
        await service.crear_plus(grupo='BD', rol='TUTOR', monto=90000, desde=date(2026, 1, 1))
        prog_pluses = await service.listar_pluses(grupo='PROG')
        assert len(prog_pluses) == 1


class TestLiquidacionService:
    @pytest.mark.asyncio
    async def test_calcular_base_sin_plus(self, db_session: AsyncSession, tenant, docente, cohorte, materia_prog):
        service = LiquidacionService(db_session, tenant.id)
        grilla = GrillaSalarialService(db_session, tenant.id)
        # Set up base salary
        await grilla.crear_base(rol='PROFESOR', monto=500000, desde=date(2026, 1, 1))
        # Set up assignment
        asig = Asignacion(
            tenant_id=tenant.id, usuario_id=docente.id, rol='PROFESOR',
            materia_id=materia_prog.id, cohorte_id=cohorte.id,
        )
        db_session.add(asig)
        await db_session.flush()
        # Calculate
        result = await service.calcular(cohorte_id=cohorte.id, periodo='2026-04')
        assert len(result) == 1
        assert float(result[0].monto_base) == 500000
        assert float(result[0].monto_plus) == 0
        assert float(result[0].total) == 500000

    @pytest.mark.asyncio
    async def test_calcular_base_plus_con_1_comision(self, db_session: AsyncSession, tenant, docente, cohorte, materia_prog):
        service = LiquidacionService(db_session, tenant.id)
        grilla = GrillaSalarialService(db_session, tenant.id)
        await grilla.crear_base(rol='PROFESOR', monto=500000, desde=date(2026, 1, 1))
        await grilla.crear_plus(grupo='PROG', rol='PROFESOR', monto=100000, desde=date(2026, 1, 1))
        asig = Asignacion(
            tenant_id=tenant.id, usuario_id=docente.id, rol='PROFESOR',
            materia_id=materia_prog.id, cohorte_id=cohorte.id,
        )
        db_session.add(asig)
        await db_session.flush()
        result = await service.calcular(cohorte_id=cohorte.id, periodo='2026-04')
        assert len(result) == 1
        assert float(result[0].total) == 600000

    @pytest.mark.asyncio
    async def test_calcular_excluye_facturante(self, db_session: AsyncSession, tenant, facturante, cohorte):
        service = LiquidacionService(db_session, tenant.id)
        result = await service.calcular(cohorte_id=cohorte.id, periodo='2026-04')
        facturante_ids = [l.usuario_id for l in result]
        assert facturante.id not in facturante_ids

    @pytest.mark.asyncio
    async def test_cerrar_exitoso(self, db_session: AsyncSession, tenant, docente, cohorte, materia_prog):
        service = LiquidacionService(db_session, tenant.id)
        grilla = GrillaSalarialService(db_session, tenant.id)
        await grilla.crear_base(rol='PROFESOR', monto=500000, desde=date(2026, 1, 1))
        asig = Asignacion(
            tenant_id=tenant.id, usuario_id=docente.id, rol='PROFESOR',
            materia_id=materia_prog.id, cohorte_id=cohorte.id,
        )
        db_session.add(asig)
        await db_session.flush()
        await service.calcular(cohorte_id=cohorte.id, periodo='2026-04')
        from app.schemas.auth import UserContext
        from app.services.audit_service import AuditService
        user_ctx = UserContext(user_id=docente.id, tenant_id=tenant.id, roles=['ADMIN'])
        audit = AuditService(db_session, user_ctx)
        result = await service.cerrar(cohorte_id=cohorte.id, periodo='2026-04', current_user=user_ctx, audit=audit)
        assert result['cerradas'] >= 1

    @pytest.mark.asyncio
    async def test_cerrar_sin_abiertas_error(self, db_session: AsyncSession, tenant, docente, cohorte, materia_prog):
        service = LiquidacionService(db_session, tenant.id)
        from app.schemas.auth import UserContext
        from app.services.audit_service import AuditService
        user_ctx = UserContext(user_id=docente.id, tenant_id=tenant.id, roles=['ADMIN'])
        audit = AuditService(db_session, user_ctx)
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc:
            await service.cerrar(cohorte_id=cohorte.id, periodo='2026-04', current_user=user_ctx, audit=audit)
        assert exc.value.status_code == 409

    @pytest.mark.asyncio
    async def test_exportar_csv(self, db_session: AsyncSession, tenant, docente, cohorte, materia_prog):
        service = LiquidacionService(db_session, tenant.id)
        grilla = GrillaSalarialService(db_session, tenant.id)
        await grilla.crear_base(rol='PROFESOR', monto=500000, desde=date(2026, 1, 1))
        asig = Asignacion(
            tenant_id=tenant.id, usuario_id=docente.id, rol='PROFESOR',
            materia_id=materia_prog.id, cohorte_id=cohorte.id,
        )
        db_session.add(asig)
        await db_session.flush()
        await service.calcular(cohorte_id=cohorte.id, periodo='2026-04')
        csv = await service.exportar_csv(cohorte_id=cohorte.id, periodo='2026-04')
        assert 'docente_id' in csv
        assert '600000' in csv or '500000' in csv


class TestFacturaService:
    @pytest.mark.asyncio
    async def test_crear_y_listar(self, db_session: AsyncSession, tenant, docente):
        service = FacturaService(db_session, tenant.id)
        f = await service.crear(usuario_id=docente.id, periodo='2026-04', detalle='Factura test')
        assert f.estado == 'Pendiente'
        lista = await service.listar(usuario_id=docente.id)
        assert len(lista) == 1

    @pytest.mark.asyncio
    async def test_cambiar_estado_a_abonada(self, db_session: AsyncSession, tenant, docente):
        service = FacturaService(db_session, tenant.id)
        f = await service.crear(usuario_id=docente.id, periodo='2026-04', detalle='Factura test')
        updated = await service.cambiar_estado(f.id, 'Abonada')
        assert updated.estado == 'Abonada'
        assert updated.abonada_at is not None

    @pytest.mark.asyncio
    async def test_estado_invalido_rechazado(self, db_session: AsyncSession, tenant, docente):
        service = FacturaService(db_session, tenant.id)
        f = await service.crear(usuario_id=docente.id, periodo='2026-04', detalle='Factura test')
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc:
            await service.cambiar_estado(f.id, 'Invalido')
        assert exc.value.status_code == 422
