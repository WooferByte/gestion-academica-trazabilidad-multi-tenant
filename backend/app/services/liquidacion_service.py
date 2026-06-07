import csv
import io
import uuid
from collections.abc import Sequence
from datetime import date, datetime
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit_codes import LIQUIDACION_CERRAR
from app.models.asignacion import Asignacion
from app.models.categoria_plus import CategoriaPlus
from app.models.liquidacion import Liquidacion
from app.models.materia import Materia
from app.models.user import User
from app.repositories.liquidacion_repository import LiquidacionRepository
from app.repositories.salario_base_repository import SalarioBaseRepository
from app.repositories.salario_plus_repository import SalarioPlusRepository
from app.schemas.auth import UserContext
from app.services.audit_service import AuditService


class LiquidacionService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self._session = session
        self._tenant_id = tenant_id
        self._liquidacion_repo = LiquidacionRepository(session, tenant_id)
        self._base_repo = SalarioBaseRepository(session, tenant_id)
        self._plus_repo = SalarioPlusRepository(session, tenant_id)

    async def listar(
        self,
        cohorte_id: uuid.UUID | None = None,
        periodo: str | None = None,
        usuario_id: uuid.UUID | None = None,
        estado: str | None = None,
    ) -> Sequence[Liquidacion]:
        return await self._liquidacion_repo.list(
            cohorte_id=cohorte_id, periodo=periodo,
            usuario_id=usuario_id, estado=estado,
        )

    async def calcular(
        self,
        cohorte_id: uuid.UUID,
        periodo: str,
    ) -> list[Liquidacion]:
        anio, mes = periodo.split('-')
        fecha_periodo = date(int(anio), int(mes), 1)

        # Get all active asignaciones for this cohorte
        stmt_asig = (
            select(Asignacion)
            .where(Asignacion.tenant_id == self._tenant_id)
            .where(Asignacion.cohorte_id == cohorte_id)
            .where(Asignacion.deleted_at.is_(None))
        )
        result = await self._session.execute(stmt_asig)
        asignaciones = list(result.scalars().all())

        if not asignaciones:
            return []

        # Group assignments by user
        user_asignaciones: dict[uuid.UUID, list[Asignacion]] = {}
        for asig in asignaciones:
            if asig.usuario_id not in user_asignaciones:
                user_asignaciones[asig.usuario_id] = []
            user_asignaciones[asig.usuario_id].append(asig)

        usuario_ids = list(user_asignaciones.keys())

        # Get all users
        stmt_users = (
            select(User)
            .where(User.tenant_id == self._tenant_id)
            .where(User.id.in_(usuario_ids))
            .where(User.deleted_at.is_(None))
        )
        result = await self._session.execute(stmt_users)
        users_map = {u.id: u for u in result.scalars().all()}

        # Get materia categories
        materia_ids = list({a.materia_id for asigs in user_asignaciones.values() for a in asigs if a.materia_id})
        stmt_mats = (
            select(Materia)
            .where(Materia.tenant_id == self._tenant_id)
            .where(Materia.id.in_(materia_ids))
        )
        result = await self._session.execute(stmt_mats)
        materias_map = {m.id: m for m in result.scalars().all()}

        # Load categorias_plus for FK lookup
        cat_ids = [m.categoria_plus_id for m in materias_map.values() if m.categoria_plus_id]
        if cat_ids:
            stmt_cat = select(CategoriaPlus).where(CategoriaPlus.id.in_(cat_ids))
            cat_result = await self._session.execute(stmt_cat)
            categorias_map = {c.id: c.codigo for c in cat_result.scalars().all()}
        else:
            categorias_map = {}

        liquidaciones = []

        for usuario_id, asigs in user_asignaciones.items():
            user = users_map.get(usuario_id)
            if not user:
                continue

            # Skip facturantes
            if user.facturador:
                continue

            rol = asigs[0].rol
            es_nexo = (rol == 'NEXO')

            # Get base vigente
            base = await self._base_repo.get_vigente(rol, fecha_periodo)
            monto_base = float(base.monto) if base else Decimal('0')

            # Accumulate plus by categoria
            total_plus = Decimal('0')
            comisiones_por_categoria: dict[str, int] = {}
            for asig in asigs:
                if not asig.materia_id:
                    continue
                materia = materias_map.get(asig.materia_id)
                if not materia or not materia.categoria_plus_id:
                    continue
                cat = categorias_map.get(materia.categoria_plus_id)
                if not cat:
                    continue
                comisiones_por_categoria[cat] = comisiones_por_categoria.get(cat, 0) + 1

            for cat, count in comisiones_por_categoria.items():
                plus = await self._plus_repo.get_vigente(cat, rol, fecha_periodo)
                if plus:
                    total_plus += Decimal(str(plus.monto)) * Decimal(count)

            total = Decimal(str(monto_base)) + total_plus

            liqui = await self._liquidacion_repo.create(
                usuario_id=usuario_id,
                cohorte_id=cohorte_id,
                periodo=periodo,
                rol=rol,
                monto_base=float(monto_base),
                monto_plus=float(total_plus),
                total=float(total),
                es_nexo=es_nexo,
                excluido_por_factura=False,
                estado='Abierta',
            )
            liquidaciones.append(liqui)

        return liquidaciones

    async def cerrar(
        self,
        cohorte_id: uuid.UUID,
        periodo: str,
        current_user: UserContext,
        audit: AuditService,
    ) -> dict:
        abiertas = await self._liquidacion_repo.get_by_cohorte_periodo(cohorte_id, periodo)
        count_abiertas = sum(1 for l in abiertas if l.estado == 'Abierta')

        if count_abiertas == 0:
            raise HTTPException(
                status_code=409,
                detail='No hay liquidaciones abiertas para cerrar en este período',
            )

        cerradas = await self._liquidacion_repo.cerrar_lote(cohorte_id, periodo)

        await audit.log(
            accion=LIQUIDACION_CERRAR,
            detalle={
                'cohorte_id': str(cohorte_id),
                'periodo': periodo,
                'liquidaciones_cerradas': cerradas,
            },
        )

        return {'cerradas': cerradas, 'periodo': periodo}

    async def exportar_csv(self, cohorte_id: uuid.UUID, periodo: str) -> str:
        liquidaciones = await self._liquidacion_repo.get_by_cohorte_periodo(cohorte_id, periodo)

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['docente_id', 'rol', 'monto_base', 'monto_plus', 'total', 'es_nexo', 'estado'])

        for l in liquidaciones:
            writer.writerow([
                str(l.usuario_id), l.rol,
                float(l.monto_base), float(l.monto_plus),
                float(l.total), 'Si' if l.es_nexo else 'No',
                l.estado,
            ])

        return output.getvalue()

    async def historial(
        self,
        cohorte_id: uuid.UUID | None = None,
        periodo: str | None = None,
        usuario_id: uuid.UUID | None = None,
    ) -> Sequence[Liquidacion]:
        return await self._liquidacion_repo.list(
            cohorte_id=cohorte_id, periodo=periodo,
            usuario_id=usuario_id, estado='Cerrada',
        )
