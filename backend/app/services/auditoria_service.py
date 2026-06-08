import uuid
from collections.abc import Sequence
from datetime import date, datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asignacion import Asignacion
from app.repositories.audit_repository import AuditLogFiltros, AuditRepository
from app.schemas.auth import UserContext
from app.schemas.auditoria import (
    AccionPorDiaResponse,
    ComunicacionesDocenteResponse,
    InteraccionesDocenteMateriaResponse,
    LogEntryResponse,
)


class AuditoriaService:
    def __init__(self, session: AsyncSession, user_context: UserContext):
        self._session = session
        self._user_context = user_context
        self._repo = AuditRepository(session, user_context.tenant_id)

    async def acciones_por_dia(
        self,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
    ) -> list[AccionPorDiaResponse]:
        if not fecha_desde and not fecha_hasta:
            fecha_hasta = datetime.now(timezone.utc).date()
            fecha_desde = fecha_hasta.replace(day=1)

        materias = await self._get_materias_coordinador()
        if materias is not None and not materias:
            return []
        rows = await self._repo.acciones_por_dia(
            tenant_id=self._user_context.tenant_id,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            materias=materias,
        )
        return [
            AccionPorDiaResponse(
                fecha=r['fecha'],
                accion=r['accion'],
                total=r['total'],
            )
            for r in rows
        ]

    async def comunicaciones_por_docente(
        self,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
        materia_id: uuid.UUID | None = None,
        usuario_id: uuid.UUID | None = None,
    ) -> list[ComunicacionesDocenteResponse]:
        materias = await self._get_materias_coordinador()
        if materias is not None and not materias:
            return []
        rows = await self._repo.comunicaciones_por_docente(
            tenant_id=self._user_context.tenant_id,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            materia_id=materia_id,
            usuario_id=usuario_id,
            materias=materias,
        )
        return [
            ComunicacionesDocenteResponse(
                usuario_id=r['usuario_id'],
                docente_email=None,
                pendientes=r['pendientes'],
                enviadas=r['enviadas'],
                fallidas=r['fallidas'],
            )
            for r in rows
        ]

    async def interacciones_por_docente_materia(
        self,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
        materia_id: uuid.UUID | None = None,
        usuario_id: uuid.UUID | None = None,
    ) -> list[InteraccionesDocenteMateriaResponse]:
        materias = await self._get_materias_coordinador()
        if materias is not None and not materias:
            return []
        rows = await self._repo.interacciones_por_docente_materia(
            tenant_id=self._user_context.tenant_id,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            materia_id=materia_id,
            usuario_id=usuario_id,
            materias=materias,
        )
        return [
            InteraccionesDocenteMateriaResponse(
                usuario_id=r['usuario_id'],
                materia_id=r['materia_id'],
                accion=r['accion'],
                total=r['total'],
            )
            for r in rows
        ]

    async def list_log(self, filtros: AuditLogFiltros) -> list[LogEntryResponse]:
        materias = await self._get_materias_coordinador()
        if materias is not None:
            if not materias:
                return []
            filtros.materias_coordinador = materias
        rows = await self._repo.list_log(filtros)
        return [LogEntryResponse.model_validate(r) for r in rows]

    async def _get_materias_coordinador(self) -> list[uuid.UUID] | None:
        if 'ADMIN' in self._user_context.roles or 'FINANZAS' in self._user_context.roles:
            return None

        if 'COORDINADOR' not in self._user_context.roles:
            return None

        now = datetime.now(timezone.utc)
        result = await self._session.execute(
            select(Asignacion.materia_id)
            .where(Asignacion.tenant_id == self._user_context.tenant_id)
            .where(Asignacion.usuario_id == self._user_context.user_id)
            .where(Asignacion.rol == 'COORDINADOR')
            .where(Asignacion.deleted_at.is_(None))
            .where(
                (Asignacion.desde.is_(None)) | (Asignacion.desde <= now),
            )
            .where(
                (Asignacion.hasta.is_(None)) | (Asignacion.hasta >= now),
            )
        )
        materias = [
            row[0] for row in result.all() if row[0] is not None
        ]

        return materias if materias else []
