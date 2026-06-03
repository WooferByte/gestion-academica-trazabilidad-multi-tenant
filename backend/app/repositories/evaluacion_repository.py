import uuid
from collections.abc import Sequence

from sqlalchemy import and_, func, select, update
from sqlalchemy.orm import joinedload

from app.models.coloquio_alumno import ColoquioAlumno
from app.models.evaluacion import Evaluacion, EstadoEvaluacion
from app.models.reserva_evaluacion import EstadoReserva, ReservaEvaluacion
from app.models.resultado_evaluacion import ResultadoEvaluacion
from app.models.turno_coloquio import TurnoColoquio
from app.repositories.base import BaseRepository


class EvaluacionRepository(BaseRepository[Evaluacion]):
    __model__ = Evaluacion

    async def list_filtered(
        self,
        materia_id: uuid.UUID | None = None,
        cohorte_id: uuid.UUID | None = None,
        tipo: str | None = None,
        estado: str | None = None,
        alumno_id: uuid.UUID | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[Sequence[Evaluacion], int]:
        stmt = self._stmt()

        if materia_id is not None:
            stmt = stmt.where(Evaluacion.materia_id == materia_id)
        if cohorte_id is not None:
            stmt = stmt.where(Evaluacion.cohorte_id == cohorte_id)
        if tipo is not None:
            stmt = stmt.where(Evaluacion.tipo == tipo)
        if estado is not None:
            stmt = stmt.where(Evaluacion.estado == estado)
        if alumno_id is not None:
            subq = (
                select(ColoquioAlumno.evaluacion_id)
                .where(ColoquioAlumno.alumno_id == alumno_id)
                .where(ColoquioAlumno.deleted_at.is_(None))
            )
            stmt = stmt.where(Evaluacion.id.in_(subq))

        count_result = await self._session.execute(stmt.with_only_columns(func.count(Evaluacion.id)))
        total = count_result.scalar() or 0

        stmt = stmt.options(joinedload(Evaluacion.turnos)).order_by(Evaluacion.created_at.desc()).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        items = list(result.unique().scalars().all())

        return items, total

    async def get_with_turnos(self, id: uuid.UUID) -> Evaluacion | None:
        stmt = self._stmt().where(Evaluacion.id == id).options(joinedload(Evaluacion.turnos))
        result = await self._session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def count_activas(self) -> int:
        stmt = select(func.count(Evaluacion.id)).where(
            Evaluacion.tenant_id == self._tenant_id,
            Evaluacion.deleted_at.is_(None),
            Evaluacion.estado == EstadoEvaluacion.ACTIVA,
        )
        result = await self._session.execute(stmt)
        return result.scalar() or 0


class TurnoColoquioRepository(BaseRepository[TurnoColoquio]):
    __model__ = TurnoColoquio

    async def atomic_reserve(self, turno_id: uuid.UUID) -> int:
        stmt = (
            update(TurnoColoquio)
            .where(
                TurnoColoquio.id == turno_id,
                TurnoColoquio.deleted_at.is_(None),
                TurnoColoquio.ocupados < TurnoColoquio.cupo,
            )
            .values(ocupados=TurnoColoquio.ocupados + 1)
            .returning(TurnoColoquio.id)
        )
        result = await self._session.execute(stmt)
        rows = result.all()
        return len(rows)

    async def atomic_cancel(self, turno_id: uuid.UUID) -> int:
        stmt = (
            update(TurnoColoquio)
            .where(
                TurnoColoquio.id == turno_id,
                TurnoColoquio.deleted_at.is_(None),
                TurnoColoquio.ocupados > 0,
            )
            .values(ocupados=TurnoColoquio.ocupados - 1)
            .returning(TurnoColoquio.id)
        )
        result = await self._session.execute(stmt)
        rows = result.all()
        return len(rows)


class ReservaEvaluacionRepository(BaseRepository[ReservaEvaluacion]):
    __model__ = ReservaEvaluacion

    async def list_by_alumno(self, alumno_id: uuid.UUID) -> Sequence[ReservaEvaluacion]:
        stmt = self._stmt().where(ReservaEvaluacion.alumno_id == alumno_id)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def count_activas_por_evaluacion(self, evaluacion_id: uuid.UUID) -> int:
        stmt = select(func.count(ReservaEvaluacion.id)).where(
            ReservaEvaluacion.tenant_id == self._tenant_id,
            ReservaEvaluacion.deleted_at.is_(None),
            ReservaEvaluacion.evaluacion_id == evaluacion_id,
            ReservaEvaluacion.estado == EstadoReserva.ACTIVA,
        )
        result = await self._session.execute(stmt)
        return result.scalar() or 0

    async def get_activa_por_alumno(self, evaluacion_id: uuid.UUID, alumno_id: uuid.UUID) -> ReservaEvaluacion | None:
        stmt = self._stmt().where(
            ReservaEvaluacion.evaluacion_id == evaluacion_id,
            ReservaEvaluacion.alumno_id == alumno_id,
            ReservaEvaluacion.estado == EstadoReserva.ACTIVA,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()


class ResultadoEvaluacionRepository(BaseRepository[ResultadoEvaluacion]):
    __model__ = ResultadoEvaluacion

    async def upsert(self, evaluacion_id: uuid.UUID, alumno_id: uuid.UUID, nota_final: str) -> ResultadoEvaluacion:
        stmt = select(ResultadoEvaluacion).where(
            ResultadoEvaluacion.tenant_id == self._tenant_id,
            ResultadoEvaluacion.evaluacion_id == evaluacion_id,
            ResultadoEvaluacion.alumno_id == alumno_id,
            ResultadoEvaluacion.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            existing.nota_final = nota_final
            await self._session.flush()
            await self._session.refresh(existing)
            return existing

        return await self.create(evaluacion_id=evaluacion_id, alumno_id=alumno_id, nota_final=nota_final)

    async def list_by_evaluacion(self, evaluacion_id: uuid.UUID) -> Sequence[ResultadoEvaluacion]:
        stmt = self._stmt().where(ResultadoEvaluacion.evaluacion_id == evaluacion_id)
        result = await self._session.execute(stmt)
        return result.scalars().all()


class ColoquioAlumnoRepository(BaseRepository[ColoquioAlumno]):
    __model__ = ColoquioAlumno

    async def replace_alumnos(self, evaluacion_id: uuid.UUID, alumno_ids: list[uuid.UUID]) -> None:
        existing_stmt = select(ColoquioAlumno).where(
            ColoquioAlumno.tenant_id == self._tenant_id,
            ColoquioAlumno.evaluacion_id == evaluacion_id,
            ColoquioAlumno.deleted_at.is_(None),
        )
        existing_result = await self._session.execute(existing_stmt)
        existing = list(existing_result.scalars().all())

        existing_ids = {r.alumno_id for r in existing}
        incoming_ids = set(alumno_ids)

        for record in existing:
            if record.alumno_id not in incoming_ids:
                from datetime import datetime, timezone
                record.deleted_at = datetime.now(timezone.utc)

        new_ids = incoming_ids - existing_ids
        for alumno_id in new_ids:
            self._session.add(ColoquioAlumno(
                tenant_id=self._tenant_id,
                evaluacion_id=evaluacion_id,
                alumno_id=alumno_id,
            ))

        await self._session.flush()

    async def list_alumnos_by_evaluacion(self, evaluacion_id: uuid.UUID) -> Sequence[ColoquioAlumno]:
        stmt = self._stmt().where(ColoquioAlumno.evaluacion_id == evaluacion_id)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def exists(self, evaluacion_id: uuid.UUID, alumno_id: uuid.UUID) -> bool:
        stmt = self._stmt().where(
            ColoquioAlumno.evaluacion_id == evaluacion_id,
            ColoquioAlumno.alumno_id == alumno_id,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None
