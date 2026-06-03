import uuid
from collections.abc import Sequence
from datetime import datetime, timezone

from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.acknowledgment_aviso import AcknowledgmentAviso
from app.models.aviso import Aviso, AlcanceAviso
from app.models.asignacion import Asignacion
from app.repositories.base import BaseRepository


class AvisoRepository(BaseRepository[Aviso]):
    __model__ = Aviso

    async def list_visibles(
        self,
        usuario_id: uuid.UUID,
        roles: list[str],
    ) -> Sequence[Aviso]:
        now = datetime.now(timezone.utc)

        asignaciones_result = await self._session.execute(
            select(Asignacion.materia_id, Asignacion.cohorte_id)
            .where(Asignacion.usuario_id == usuario_id)
            .where(Asignacion.deleted_at.is_(None))
        )
        asignaciones = asignaciones_result.all()
        materia_ids = {row.materia_id for row in asignaciones if row.materia_id}
        cohorte_ids = {row.cohorte_id for row in asignaciones if row.cohorte_id}

        stmt = (
            select(Aviso)
            .where(Aviso.tenant_id == self._tenant_id)
            .where(Aviso.deleted_at.is_(None))
            .where(Aviso.activo.is_(True))
            .where(Aviso.inicio_vigencia <= now)
            .where(Aviso.fin_vigencia >= now)
            .where(
                or_(
                    Aviso.alcance == AlcanceAviso.GLOBAL,
                    and_(
                        Aviso.alcance == AlcanceAviso.POR_ROL,
                        Aviso.rol_destino.in_(roles),
                    ),
                    and_(
                        Aviso.alcance == AlcanceAviso.POR_MATERIA,
                        Aviso.materia_id.in_(materia_ids) if materia_ids else False,
                    ),
                    and_(
                        Aviso.alcance == AlcanceAviso.POR_COHORTE,
                        Aviso.cohorte_id.in_(cohorte_ids) if cohorte_ids else False,
                    ),
                )
            )
            .order_by(Aviso.orden.asc(), Aviso.inicio_vigencia.desc())
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def count_acks(self, aviso_id: uuid.UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(AcknowledgmentAviso)
            .where(AcknowledgmentAviso.aviso_id == aviso_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def user_has_acked(self, aviso_id: uuid.UUID, usuario_id: uuid.UUID) -> bool:
        stmt = (
            select(AcknowledgmentAviso)
            .where(AcknowledgmentAviso.aviso_id == aviso_id)
            .where(AcknowledgmentAviso.usuario_id == usuario_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def create_ack(self, aviso_id: uuid.UUID, usuario_id: uuid.UUID) -> AcknowledgmentAviso:
        ack = AcknowledgmentAviso(
            tenant_id=self._tenant_id,
            aviso_id=aviso_id,
            usuario_id=usuario_id,
            confirmado_at=datetime.now(timezone.utc),
        )
        self._session.add(ack)
        await self._session.flush()
        return ack
