import uuid
from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.calificacion import Calificacion
from app.models.entrada_padron import EntradaPadron
from app.models.version_padron import VersionPadron


class AnalisisRepository:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self._session = session
        self._tenant_id = tenant_id

    async def get_calificaciones_con_alumnos(
        self, materia_id: uuid.UUID, cohorte_id: uuid.UUID,
    ) -> list[dict]:
        stmt = (
            select(
                Calificacion.id,
                Calificacion.entrada_padron_id,
                Calificacion.materia_id,
                Calificacion.cohorte_id,
                Calificacion.actividad,
                Calificacion.nota_numerica,
                Calificacion.nota_textual,
                Calificacion.importado_at,
                EntradaPadron.nombre,
                EntradaPadron.apellidos,
                EntradaPadron.email,
                EntradaPadron.comision,
                EntradaPadron.regional,
            )
            .join(EntradaPadron, Calificacion.entrada_padron_id == EntradaPadron.id)
            .where(Calificacion.tenant_id == self._tenant_id)
            .where(Calificacion.deleted_at.is_(None))
            .where(EntradaPadron.deleted_at.is_(None))
            .where(Calificacion.materia_id == materia_id)
            .where(Calificacion.cohorte_id == cohorte_id)
        )
        result = await self._session.execute(stmt)
        rows = result.all()
        return [dict(row._mapping) for row in rows]

    async def get_actividades_por_materia(
        self, materia_id: uuid.UUID, cohorte_id: uuid.UUID,
    ) -> list[str]:
        stmt = (
            select(Calificacion.actividad)
            .where(Calificacion.tenant_id == self._tenant_id)
            .where(Calificacion.deleted_at.is_(None))
            .where(Calificacion.materia_id == materia_id)
            .where(Calificacion.cohorte_id == cohorte_id)
            .distinct()
            .order_by(Calificacion.actividad)
        )
        result = await self._session.execute(stmt)
        return [row[0] for row in result.all()]

    async def get_alumnos_por_materia(
        self, materia_id: uuid.UUID, cohorte_id: uuid.UUID,
    ) -> Sequence[EntradaPadron]:
        stmt = (
            select(EntradaPadron)
            .join(VersionPadron, EntradaPadron.version_id == VersionPadron.id)
            .where(VersionPadron.tenant_id == self._tenant_id)
            .where(VersionPadron.materia_id == materia_id)
            .where(VersionPadron.cohorte_id == cohorte_id)
            .where(VersionPadron.activa.is_(True))
            .where(EntradaPadron.deleted_at.is_(None))
            .where(VersionPadron.deleted_at.is_(None))
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def get_calificaciones_por_tenant(
        self,
        materia_id: uuid.UUID | None = None,
        comision: str | None = None,
        regional: str | None = None,
        busqueda: str | None = None,
    ) -> list[dict]:
        from app.models.materia import Materia

        stmt = (
            select(
                Calificacion.id,
                Calificacion.entrada_padron_id,
                Calificacion.materia_id,
                Calificacion.actividad,
                Calificacion.nota_numerica,
                Calificacion.nota_textual,
                Calificacion.importado_at,
                EntradaPadron.nombre,
                EntradaPadron.apellidos,
                EntradaPadron.comision,
                EntradaPadron.regional,
            )
            .join(EntradaPadron, Calificacion.entrada_padron_id == EntradaPadron.id)
            .where(Calificacion.tenant_id == self._tenant_id)
            .where(Calificacion.deleted_at.is_(None))
            .where(EntradaPadron.deleted_at.is_(None))
        )
        if materia_id is not None:
            stmt = stmt.where(Calificacion.materia_id == materia_id)
        if comision is not None:
            stmt = stmt.where(EntradaPadron.comision == comision)
        if regional is not None:
            stmt = stmt.where(EntradaPadron.regional == regional)
        if busqueda is not None:
            terms = [t.strip() for t in busqueda.split() if t.strip()]
            for term in terms:
                stmt = stmt.where(
                    func.unaccent(EntradaPadron.nombre).ilike(f'%{term}%')
                    | func.unaccent(EntradaPadron.apellidos).ilike(f'%{term}%'),
                )
        result = await self._session.execute(stmt)
        rows = result.all()
        return [dict(row._mapping) for row in rows]

    async def get_calificaciones_por_asignaciones(
        self,
        usuario_id: uuid.UUID,
        materia_id: uuid.UUID | None = None,
        comision: str | None = None,
        desde: datetime | None = None,
        hasta: datetime | None = None,
        min_actividades: int | None = None,
        busqueda: str | None = None,
    ) -> list[dict]:
        from app.models.asignacion import Asignacion

        asignaciones_subq = (
            select(Asignacion.materia_id, Asignacion.comisiones)
            .where(Asignacion.tenant_id == self._tenant_id)
            .where(Asignacion.usuario_id == usuario_id)
            .where(Asignacion.deleted_at.is_(None))
            .where(Asignacion.rol.in_(['TUTOR', 'PROFESOR']))
            .subquery()
        )

        stmt = (
            select(
                Calificacion.id,
                Calificacion.entrada_padron_id,
                Calificacion.materia_id,
                Calificacion.actividad,
                Calificacion.nota_numerica,
                Calificacion.nota_textual,
                Calificacion.importado_at,
                EntradaPadron.nombre,
                EntradaPadron.apellidos,
                EntradaPadron.comision,
            )
            .join(EntradaPadron, Calificacion.entrada_padron_id == EntradaPadron.id)
            .join(
                asignaciones_subq,
                Calificacion.materia_id == asignaciones_subq.c.materia_id,
            )
            .where(Calificacion.tenant_id == self._tenant_id)
            .where(Calificacion.deleted_at.is_(None))
            .where(EntradaPadron.deleted_at.is_(None))
        )
        if materia_id is not None:
            stmt = stmt.where(Calificacion.materia_id == materia_id)
        if comision is not None:
            stmt = stmt.where(EntradaPadron.comision == comision)
        if desde is not None:
            stmt = stmt.where(Calificacion.importado_at >= desde)
        if hasta is not None:
            stmt = stmt.where(Calificacion.importado_at <= hasta)
        if busqueda is not None:
            terms = [t.strip() for t in busqueda.split() if t.strip()]
            for term in terms:
                stmt = stmt.where(
                    func.unaccent(EntradaPadron.nombre).ilike(f'%{term}%')
                    | func.unaccent(EntradaPadron.apellidos).ilike(f'%{term}%'),
                )
        result = await self._session.execute(stmt)
        rows = result.all()
        return [dict(row._mapping) for row in rows]

    async def get_calificaciones_por_materias_usuario(
        self,
        usuario_id: uuid.UUID,
        materia_id: uuid.UUID | None = None,
        desde: datetime | None = None,
        hasta: datetime | None = None,
    ) -> list[dict]:
        from app.models.asignacion import Asignacion

        asignaciones_subq = (
            select(Asignacion.materia_id)
            .where(Asignacion.tenant_id == self._tenant_id)
            .where(Asignacion.usuario_id == usuario_id)
            .where(Asignacion.deleted_at.is_(None))
            .subquery()
        )

        stmt = (
            select(
                Calificacion.id,
                Calificacion.entrada_padron_id,
                Calificacion.materia_id,
                Calificacion.actividad,
                Calificacion.nota_numerica,
                Calificacion.nota_textual,
                Calificacion.importado_at,
                EntradaPadron.nombre,
                EntradaPadron.apellidos,
                EntradaPadron.comision,
            )
            .join(EntradaPadron, Calificacion.entrada_padron_id == EntradaPadron.id)
            .join(
                asignaciones_subq,
                Calificacion.materia_id == asignaciones_subq.c.materia_id,
            )
            .where(Calificacion.tenant_id == self._tenant_id)
            .where(Calificacion.deleted_at.is_(None))
            .where(EntradaPadron.deleted_at.is_(None))
        )
        if materia_id is not None:
            stmt = stmt.where(Calificacion.materia_id == materia_id)
        if desde is not None:
            stmt = stmt.where(Calificacion.importado_at >= desde)
        if hasta is not None:
            stmt = stmt.where(Calificacion.importado_at <= hasta)
        result = await self._session.execute(stmt)
        rows = result.all()
        return [dict(row._mapping) for row in rows]
