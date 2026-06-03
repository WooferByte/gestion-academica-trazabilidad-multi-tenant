import csv
import io
import uuid

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asignacion import Asignacion
from app.models.guardia import EstadoGuardia, Guardia
from app.models.slot_encuentro import DiaSemana
from app.repositories.guardia_repository import GuardiaRepository
from app.schemas.auth import UserContext
from app.schemas.guardias import (
    GuardiaCreate,
    GuardiaResponse,
    GuardiaUpdate,
)


def _validate_dia_semana(valor: str) -> DiaSemana:
    for d in DiaSemana:
        if d.value == valor:
            return d
    raise HTTPException(status_code=422, detail=f'Dia de semana invalido: {valor}')


def _validate_estado_guardia(valor: str) -> EstadoGuardia:
    for e in EstadoGuardia:
        if e.value == valor:
            return e
    raise HTTPException(status_code=422, detail=f'Estado invalido: {valor}')


CSV_HEADERS = [
    'id', 'tenant_id', 'asignacion_id', 'materia_id',
    'carrera_id', 'cohorte_id', 'dia', 'horario',
    'estado', 'comentarios', 'creada_at',
]


class GuardiaService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self._session = session
        self._repo = GuardiaRepository(session, tenant_id)
        self._tenant_id = tenant_id

    async def create(self, data: GuardiaCreate) -> GuardiaResponse:
        _validate_dia_semana(data.dia)
        guardia = await self._repo.create(
            asignacion_id=data.asignacion_id,
            materia_id=data.materia_id,
            carrera_id=data.carrera_id,
            cohorte_id=data.cohorte_id,
            dia=data.dia,
            horario=data.horario,
            estado=EstadoGuardia.PENDIENTE,
            comentarios=data.comentarios,
        )
        return self._to_response(guardia)

    async def list_with_filters(
        self,
        materia_id: uuid.UUID | None = None,
        carrera_id: uuid.UUID | None = None,
        cohorte_id: uuid.UUID | None = None,
        estado: str | None = None,
        current_user: UserContext | None = None,
        skip: int = 0,
        limit: int = 100,
    ):
        asignacion_ids = None
        if current_user and 'COORDINADOR' not in current_user.roles and 'ADMIN' not in current_user.roles:
            result = await self._session.execute(
                select(Asignacion.id)
                .where(Asignacion.usuario_id == current_user.user_id)
                .where(Asignacion.tenant_id == self._tenant_id)
                .where(Asignacion.deleted_at.is_(None))
            )
            asignacion_ids = [row[0] for row in result.all()]
            if not asignacion_ids:
                return [], 0

        items, total = await self._repo.list_filtered(
            materia_id=materia_id,
            carrera_id=carrera_id,
            cohorte_id=cohorte_id,
            estado=estado,
            asignacion_ids=asignacion_ids,
            skip=skip,
            limit=limit,
        )
        return [self._to_response(i) for i in items], total

    async def update_state(self, guardia_id: uuid.UUID, data: GuardiaUpdate) -> GuardiaResponse:
        guardia = await self._repo.get(guardia_id)
        if not guardia:
            raise HTTPException(status_code=404, detail='Guardia no encontrada')

        _validate_estado_guardia(data.estado)
        kwargs: dict = {'estado': data.estado}
        if data.comentarios is not None:
            kwargs['comentarios'] = data.comentarios

        guardia = await self._repo.update(guardia, **kwargs)
        return self._to_response(guardia)

    async def export_csv(
        self,
        materia_id: uuid.UUID | None = None,
        carrera_id: uuid.UUID | None = None,
        cohorte_id: uuid.UUID | None = None,
        estado: str | None = None,
        asignacion_ids: list[uuid.UUID] | None = None,
    ) -> str:
        items = await self._repo.list_all_for_export(
            materia_id=materia_id,
            carrera_id=carrera_id,
            cohorte_id=cohorte_id,
            estado=estado,
            asignacion_ids=asignacion_ids,
        )
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(CSV_HEADERS)
        for g in items:
            writer.writerow([
                str(g.id), str(g.tenant_id), str(g.asignacion_id), str(g.materia_id),
                str(g.carrera_id) if g.carrera_id else '',
                str(g.cohorte_id) if g.cohorte_id else '',
                g.dia.value if isinstance(g.dia, DiaSemana) else str(g.dia),
                g.horario,
                g.estado.value if isinstance(g.estado, EstadoGuardia) else str(g.estado),
                g.comentarios or '',
                g.creada_at.isoformat() if g.creada_at else '',
            ])
        return output.getvalue()

    def _to_response(self, g: Guardia) -> GuardiaResponse:
        return GuardiaResponse(
            id=g.id,
            tenant_id=g.tenant_id,
            asignacion_id=g.asignacion_id,
            materia_id=g.materia_id,
            carrera_id=g.carrera_id,
            cohorte_id=g.cohorte_id,
            dia=g.dia.value if isinstance(g.dia, DiaSemana) else str(g.dia),
            horario=g.horario,
            estado=g.estado.value if isinstance(g.estado, EstadoGuardia) else str(g.estado),
            comentarios=g.comentarios,
            creada_at=g.creada_at,
            created_at=g.created_at,
            updated_at=g.updated_at,
        )
