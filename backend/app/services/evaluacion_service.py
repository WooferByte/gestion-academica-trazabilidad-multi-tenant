import uuid
from datetime import date, datetime, time

from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.coloquio_alumno import ColoquioAlumno
from app.models.evaluacion import EstadoEvaluacion, Evaluacion, TipoEvaluacion
from app.models.reserva_evaluacion import EstadoReserva, ReservaEvaluacion
from app.models.resultado_evaluacion import ResultadoEvaluacion
from app.models.turno_coloquio import TurnoColoquio
from app.models.user import User
from app.repositories.evaluacion_repository import (
    ColoquioAlumnoRepository,
    EvaluacionRepository,
    ReservaEvaluacionRepository,
    ResultadoEvaluacionRepository,
    TurnoColoquioRepository,
)
from app.schemas.auth import UserContext
from app.schemas.evaluaciones import (
    AlumnosImportRequest,
    EvaluacionCreate,
    EvaluacionResponse,
    MetricasColoquiosResponse,
    ReservaCreate,
    ReservaResponse,
    ResultadoCreate,
    ResultadoResponse,
    ResultadosListResponse,
    TurnoColoquioResponse,
)


class EvaluacionService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self._session = session
        self._tenant_id = tenant_id
        self._eval_repo = EvaluacionRepository(session, tenant_id)
        self._turno_repo = TurnoColoquioRepository(session, tenant_id)
        self._reserva_repo = ReservaEvaluacionRepository(session, tenant_id)
        self._resultado_repo = ResultadoEvaluacionRepository(session, tenant_id)
        self._col_alumno_repo = ColoquioAlumnoRepository(session, tenant_id)

    def _parse_tipo(self, valor: str) -> TipoEvaluacion:
        for t in TipoEvaluacion:
            if t.value == valor:
                return t
        raise HTTPException(status_code=422, detail=f'Tipo de evaluacion invalido: {valor}')

    def _parse_turno_hora(self, valor: str) -> time:
        parts = valor.split(':')
        return time(int(parts[0]), int(parts[1]))

    async def create_convocatoria(self, data: EvaluacionCreate) -> EvaluacionResponse:
        tipo = self._parse_tipo(data.tipo)

        if not data.turnos:
            raise HTTPException(status_code=422, detail='Debe especificar al menos 1 turno')

        fechas_unicas = {t.fecha.isoformat() for t in data.turnos}
        dias_disponibles = len(fechas_unicas)

        evaluacion = await self._eval_repo.create(
            materia_id=data.materia_id,
            cohorte_id=data.cohorte_id,
            tipo=tipo,
            instancia=data.instancia,
            estado=EstadoEvaluacion.ACTIVA,
            dias_disponibles=dias_disponibles,
        )

        turnos_resp = []
        for t in data.turnos:
            turno = await self._turno_repo.create(
                evaluacion_id=evaluacion.id,
                fecha=t.fecha,
                hora_inicio=self._parse_turno_hora(t.hora_inicio),
                hora_fin=self._parse_turno_hora(t.hora_fin),
                cupo=t.cupo,
                ocupados=0,
            )
            turnos_resp.append(self._turno_to_response(turno))

        return self._eval_to_response(evaluacion, turnos=turnos_resp)

    async def listar_convocatorias(
        self,
        materia_id: uuid.UUID | None = None,
        cohorte_id: uuid.UUID | None = None,
        tipo: str | None = None,
        estado: str | None = None,
        current_user: UserContext | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[EvaluacionResponse], int]:
        alumno_id = None
        if current_user and 'COORDINADOR' not in current_user.roles and 'ADMIN' not in current_user.roles:
            alumno_id = current_user.user_id

        items, total = await self._eval_repo.list_filtered(
            materia_id=materia_id,
            cohorte_id=cohorte_id,
            tipo=tipo,
            estado=estado,
            alumno_id=alumno_id,
            skip=skip,
            limit=limit,
        )

        responses = []
        for ev in items:
            reservas_count = await self._reserva_repo.count_activas_por_evaluacion(ev.id)
            convocados_result = await self._session.execute(
                select(func.count(ColoquioAlumno.id)).where(
                    ColoquioAlumno.tenant_id == self._tenant_id,
                    ColoquioAlumno.evaluacion_id == ev.id,
                    ColoquioAlumno.deleted_at.is_(None),
                )
            )
            total_convocados = convocados_result.scalar() or 0

            cupo_total = sum(t.cupo for t in ev.turnos) if ev.turnos else 0
            cupos_libres = cupo_total - reservas_count

            turnos_resp = [self._turno_to_response(t) for t in (ev.turnos or [])]
            responses.append(self._eval_to_response(ev, turnos=turnos_resp, total_convocados=total_convocados, reservas_activas=reservas_count, cupos_libres=cupos_libres))

        return responses, total

    async def obtener_convocatoria(self, evaluacion_id: uuid.UUID) -> EvaluacionResponse:
        ev = await self._eval_repo.get_with_turnos(evaluacion_id)
        if not ev:
            raise HTTPException(status_code=404, detail='Convocatoria no encontrada')

        reservas_count = await self._reserva_repo.count_activas_por_evaluacion(ev.id)
        convocados_result = await self._session.execute(
            select(func.count(ColoquioAlumno.id)).where(
                ColoquioAlumno.tenant_id == self._tenant_id,
                ColoquioAlumno.evaluacion_id == ev.id,
                ColoquioAlumno.deleted_at.is_(None),
            )
        )
        total_convocados = convocados_result.scalar() or 0

        cupo_total = sum(t.cupo for t in (ev.turnos or []))
        cupos_libres = cupo_total - reservas_count

        turnos_resp = [self._turno_to_response(t) for t in (ev.turnos or [])]
        return self._eval_to_response(ev, turnos=turnos_resp, total_convocados=total_convocados, reservas_activas=reservas_count, cupos_libres=cupos_libres)

    async def obtener_metricas(self) -> MetricasColoquiosResponse:
        total_convocatorias = await self._eval_repo.count_activas()

        convocados_result = await self._session.execute(
            select(func.count(func.distinct(ColoquioAlumno.alumno_id))).where(
                ColoquioAlumno.tenant_id == self._tenant_id,
                ColoquioAlumno.deleted_at.is_(None),
            )
        )
        total_alumnos = convocados_result.scalar() or 0

        reservas_result = await self._session.execute(
            select(func.count(ReservaEvaluacion.id)).where(
                ReservaEvaluacion.tenant_id == self._tenant_id,
                ReservaEvaluacion.deleted_at.is_(None),
                ReservaEvaluacion.estado == EstadoReserva.ACTIVA,
            )
        )
        total_reservas = reservas_result.scalar() or 0

        resultados_result = await self._session.execute(
            select(func.count(ResultadoEvaluacion.id)).where(
                ResultadoEvaluacion.tenant_id == self._tenant_id,
                ResultadoEvaluacion.deleted_at.is_(None),
            )
        )
        total_resultados = resultados_result.scalar() or 0

        return MetricasColoquiosResponse(
            total_convocatorias_activas=total_convocatorias,
            total_alumnos_convocados=total_alumnos,
            total_reservas_activas=total_reservas,
            total_resultados_registrados=total_resultados,
        )

    async def importar_alumnos(self, evaluacion_id: uuid.UUID, data: AlumnosImportRequest) -> None:
        ev = await self._eval_repo.get(evaluacion_id)
        if not ev:
            raise HTTPException(status_code=404, detail='Convocatoria no encontrada')
        if ev.estado != EstadoEvaluacion.ACTIVA:
            raise HTTPException(status_code=400, detail='Solo se pueden importar alumnos en convocatorias activas')

        for alumno_id in data.alumno_ids:
            result = await self._session.execute(
                select(User).where(
                    User.id == alumno_id,
                    User.tenant_id == self._tenant_id,
                    User.deleted_at.is_(None),
                )
            )
            user = result.scalar_one_or_none()
            if not user:
                raise HTTPException(status_code=422, detail=f'Usuario {alumno_id} no encontrado o no existe en el tenant')

            roles = [r.upper() for r in (user.roles or [])]
            if 'ALUMNO' not in roles:
                raise HTTPException(status_code=422, detail=f'Usuario {alumno_id} no tiene rol ALUMNO')

        await self._col_alumno_repo.replace_alumnos(evaluacion_id, data.alumno_ids)

    async def cerrar_convocatoria(self, evaluacion_id: uuid.UUID) -> EvaluacionResponse:
        ev = await self._eval_repo.get(evaluacion_id)
        if not ev:
            raise HTTPException(status_code=404, detail='Convocatoria no encontrada')
        if ev.estado != EstadoEvaluacion.ACTIVA:
            raise HTTPException(status_code=400, detail='La convocatoria ya esta cerrada')

        ev = await self._eval_repo.update(ev, estado=EstadoEvaluacion.CERRADA)

        reservas_activas = await self._session.execute(
            select(ReservaEvaluacion).where(
                ReservaEvaluacion.tenant_id == self._tenant_id,
                ReservaEvaluacion.deleted_at.is_(None),
                ReservaEvaluacion.evaluacion_id == ev.id,
                ReservaEvaluacion.estado == EstadoReserva.ACTIVA,
            )
        )
        for r in reservas_activas.scalars().all():
            await self._reserva_repo.update(r, estado=EstadoReserva.CANCELADA)

        return self._eval_to_response(ev)

    def _turno_to_response(self, t: TurnoColoquio) -> TurnoColoquioResponse:
        return TurnoColoquioResponse(
            id=t.id,
            evaluacion_id=t.evaluacion_id,
            fecha=t.fecha,
            hora_inicio=t.hora_inicio,
            hora_fin=t.hora_fin,
            cupo=t.cupo,
            ocupados=t.ocupados,
            created_at=t.created_at,
            updated_at=t.updated_at,
        )

    def _eval_to_response(
        self,
        ev: Evaluacion,
        turnos: list | None = None,
        total_convocados: int = 0,
        reservas_activas: int = 0,
        cupos_libres: int = 0,
    ) -> EvaluacionResponse:
        return EvaluacionResponse(
            id=ev.id,
            tenant_id=ev.tenant_id,
            materia_id=ev.materia_id,
            cohorte_id=ev.cohorte_id,
            tipo=ev.tipo.value if isinstance(ev.tipo, TipoEvaluacion) else str(ev.tipo),
            instancia=ev.instancia,
            estado=ev.estado.value if isinstance(ev.estado, EstadoEvaluacion) else str(ev.estado),
            dias_disponibles=ev.dias_disponibles,
            turnos=turnos or [],
            total_convocados=total_convocados,
            reservas_activas=reservas_activas,
            cupos_libres=cupos_libres,
            created_at=ev.created_at,
            updated_at=ev.updated_at,
        )


class ReservaService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self._session = session
        self._tenant_id = tenant_id
        self._eval_repo = EvaluacionRepository(session, tenant_id)
        self._turno_repo = TurnoColoquioRepository(session, tenant_id)
        self._reserva_repo = ReservaEvaluacionRepository(session, tenant_id)
        self._col_alumno_repo = ColoquioAlumnoRepository(session, tenant_id)

    async def reservar(self, evaluacion_id: uuid.UUID, data: ReservaCreate, alumno_id: uuid.UUID) -> ReservaResponse:
        ev = await self._eval_repo.get(evaluacion_id)
        if not ev:
            raise HTTPException(status_code=404, detail='Convocatoria no encontrada')
        if ev.estado != EstadoEvaluacion.ACTIVA:
            raise HTTPException(status_code=400, detail='La convocatoria no esta activa')

        habilitado = await self._col_alumno_repo.exists(evaluacion_id, alumno_id)
        if not habilitado:
            raise HTTPException(status_code=403, detail='El alumno no esta habilitado para esta convocatoria')

        reserva_existente = await self._reserva_repo.get_activa_por_alumno(evaluacion_id, alumno_id)
        if reserva_existente:
            raise HTTPException(status_code=409, detail='Ya tiene una reserva activa en esta convocatoria')

        turno = await self._turno_repo.get(data.turno_id)
        if not turno or turno.evaluacion_id != evaluacion_id:
            raise HTTPException(status_code=404, detail='Turno no encontrado en esta convocatoria')

        affected = await self._turno_repo.atomic_reserve(data.turno_id)
        if affected == 0:
            raise HTTPException(status_code=409, detail='Turno sin cupo disponible')

        reserva = await self._reserva_repo.create(
            turno_id=data.turno_id,
            alumno_id=alumno_id,
            evaluacion_id=evaluacion_id,
            estado=EstadoReserva.ACTIVA,
        )

        return self._reserva_to_response(reserva)

    async def cancelar(self, reserva_id: uuid.UUID, current_user: UserContext) -> ReservaResponse:
        is_gestor = 'COORDINADOR' in current_user.roles or 'ADMIN' in current_user.roles

        stmt = select(ReservaEvaluacion).where(
            ReservaEvaluacion.id == reserva_id,
            ReservaEvaluacion.tenant_id == self._tenant_id,
            ReservaEvaluacion.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        reserva = result.scalar_one_or_none()

        if not reserva:
            raise HTTPException(status_code=404, detail='Reserva no encontrada')

        if not is_gestor and reserva.alumno_id != current_user.user_id:
            raise HTTPException(status_code=404, detail='Reserva no encontrada')

        if reserva.estado != EstadoReserva.ACTIVA:
            raise HTTPException(status_code=400, detail='La reserva no esta activa')

        await self._turno_repo.atomic_cancel(reserva.turno_id)
        reserva = await self._reserva_repo.update(reserva, estado=EstadoReserva.CANCELADA)

        return self._reserva_to_response(reserva)

    def _reserva_to_response(self, r: ReservaEvaluacion) -> ReservaResponse:
        return ReservaResponse(
            id=r.id,
            turno_id=r.turno_id,
            alumno_id=r.alumno_id,
            evaluacion_id=r.evaluacion_id,
            estado=r.estado.value if isinstance(r.estado, EstadoReserva) else str(r.estado),
            created_at=r.created_at,
            updated_at=r.updated_at,
        )


class ResultadoService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self._session = session
        self._tenant_id = tenant_id
        self._eval_repo = EvaluacionRepository(session, tenant_id)
        self._resultado_repo = ResultadoEvaluacionRepository(session, tenant_id)

    async def registrar(self, evaluacion_id: uuid.UUID, alumno_id: uuid.UUID, data: ResultadoCreate) -> ResultadoResponse:
        ev = await self._eval_repo.get(evaluacion_id)
        if not ev:
            raise HTTPException(status_code=404, detail='Convocatoria no encontrada')

        result = await self._resultado_repo.upsert(evaluacion_id, alumno_id, data.nota_final)
        return self._to_response(result)

    async def listar(self, evaluacion_id: uuid.UUID) -> ResultadosListResponse:
        ev = await self._eval_repo.get(evaluacion_id)
        if not ev:
            raise HTTPException(status_code=404, detail='Convocatoria no encontrada')

        items = await self._resultado_repo.list_by_evaluacion(evaluacion_id)
        return ResultadosListResponse(
            items=[self._to_response(r) for r in items],
            total=len(items),
        )

    def _to_response(self, r: ResultadoEvaluacion) -> ResultadoResponse:
        return ResultadoResponse(
            id=r.id,
            evaluacion_id=r.evaluacion_id,
            alumno_id=r.alumno_id,
            nota_final=r.nota_final,
            created_at=r.created_at,
            updated_at=r.updated_at,
        )
