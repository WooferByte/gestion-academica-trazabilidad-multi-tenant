import uuid
from collections.abc import Sequence
from datetime import date

from sqlalchemy import Select, cast, func, select
from sqlalchemy.dialects.postgresql import DATE
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.audit_log import AuditLog
from app.models.comunicacion import Comunicacion, EstadoComunicacion


class AuditLogFiltros:
    def __init__(
        self,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
        materia_id: uuid.UUID | None = None,
        usuario_id: uuid.UUID | None = None,
        accion: str | None = None,
        max_records: int = 200,
        materias_coordinador: list[uuid.UUID] | None = None,
    ):
        self.fecha_desde = fecha_desde
        self.fecha_hasta = fecha_hasta
        self.materia_id = materia_id
        self.usuario_id = usuario_id
        self.accion = accion
        self.max_records = max_records
        self.materias_coordinador = materias_coordinador


class AuditRepository:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self._session = session
        self._tenant_id = tenant_id

    async def create(self, entry: AuditLog) -> AuditLog:
        self._session.add(entry)
        await self._session.flush()
        return entry

    async def list_log(self, filtros: AuditLogFiltros) -> Sequence[AuditLog]:
        query = self._build_log_query(filtros)
        result = await self._session.execute(query)
        return result.scalars().all()

    async def acciones_por_dia(
        self,
        tenant_id: uuid.UUID,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
        materias: list[uuid.UUID] | None = None,
    ) -> Sequence[dict]:
        query = (
            select(
                cast(func.date(AuditLog.fecha_hora), DATE).label('fecha'),
                AuditLog.accion,
                func.count(AuditLog.id).label('total'),
            )
            .where(AuditLog.tenant_id == tenant_id)
        )

        if fecha_desde:
            query = query.where(func.date(AuditLog.fecha_hora) >= fecha_desde)
        if fecha_hasta:
            query = query.where(func.date(AuditLog.fecha_hora) <= fecha_hasta)
        if materias:
            query = query.where(AuditLog.materia_id.in_(materias))

        query = query.group_by(func.date(AuditLog.fecha_hora), AuditLog.accion)
        query = query.order_by(func.date(AuditLog.fecha_hora).desc(), AuditLog.accion)

        result = await self._session.execute(query)
        return result.mappings().all()

    async def comunicaciones_por_docente(
        self,
        tenant_id: uuid.UUID,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
        materia_id: uuid.UUID | None = None,
        usuario_id: uuid.UUID | None = None,
        materias: list[uuid.UUID] | None = None,
    ) -> Sequence[dict]:
        query = (
            select(
                Comunicacion.enviado_por.label('usuario_id'),
                Comunicacion.materia_id,
                func.count()
                .filter(Comunicacion.estado == EstadoComunicacion.PENDIENTE)
                .label('pendientes'),
                func.count()
                .filter(Comunicacion.estado == EstadoComunicacion.ENVIADO)
                .label('enviadas'),
                func.count()
                .filter(
                    Comunicacion.estado.in_(
                        [EstadoComunicacion.ERROR, EstadoComunicacion.CANCELADO],
                    ),
                )
                .label('fallidas'),
            )
            .where(Comunicacion.tenant_id == tenant_id)
            .where(Comunicacion.deleted_at.is_(None))
            .group_by(Comunicacion.enviado_por, Comunicacion.materia_id)
        )

        if fecha_desde:
            query = query.where(
                func.date(Comunicacion.created_at) >= fecha_desde,
            )
        if fecha_hasta:
            query = query.where(
                func.date(Comunicacion.created_at) <= fecha_hasta,
            )
        if materia_id:
            query = query.where(Comunicacion.materia_id == materia_id)
        if usuario_id:
            query = query.where(Comunicacion.enviado_por == usuario_id)
        if materias:
            query = query.where(Comunicacion.materia_id.in_(materias))

        result = await self._session.execute(query)
        return result.mappings().all()

    async def interacciones_por_docente_materia(
        self,
        tenant_id: uuid.UUID,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
        materia_id: uuid.UUID | None = None,
        usuario_id: uuid.UUID | None = None,
        materias: list[uuid.UUID] | None = None,
    ) -> Sequence[dict]:
        query = (
            select(
                AuditLog.actor_id.label('usuario_id'),
                AuditLog.materia_id,
                AuditLog.accion,
                func.count(AuditLog.id).label('total'),
            )
            .where(AuditLog.tenant_id == tenant_id)
        )

        if fecha_desde:
            query = query.where(
                func.date(AuditLog.fecha_hora) >= fecha_desde,
            )
        if fecha_hasta:
            query = query.where(
                func.date(AuditLog.fecha_hora) <= fecha_hasta,
            )
        if materia_id:
            query = query.where(AuditLog.materia_id == materia_id)
        if usuario_id:
            query = query.where(AuditLog.actor_id == usuario_id)
        if materias:
            query = query.where(AuditLog.materia_id.in_(materias))

        query = query.group_by(
            AuditLog.actor_id, AuditLog.materia_id, AuditLog.accion,
        )
        query = query.order_by(
            AuditLog.actor_id, AuditLog.materia_id, AuditLog.accion,
        )

        result = await self._session.execute(query)
        return result.mappings().all()

    def _build_log_query(self, filtros: AuditLogFiltros) -> Select:
        query = (
            select(AuditLog)
            .where(AuditLog.tenant_id == self._tenant_id)
        )

        if filtros.fecha_desde:
            query = query.where(
                func.date(AuditLog.fecha_hora) >= filtros.fecha_desde,
            )
        if filtros.fecha_hasta:
            query = query.where(
                func.date(AuditLog.fecha_hora) <= filtros.fecha_hasta,
            )
        if filtros.materia_id:
            query = query.where(AuditLog.materia_id == filtros.materia_id)
        if filtros.usuario_id:
            query = query.where(AuditLog.actor_id == filtros.usuario_id)
        if filtros.accion:
            query = query.where(AuditLog.accion == filtros.accion)
        if filtros.materias_coordinador:
            query = query.where(
                AuditLog.materia_id.in_(filtros.materias_coordinador),
            )

        query = query.order_by(AuditLog.fecha_hora.desc())
        query = query.limit(filtros.max_records)
        return query
