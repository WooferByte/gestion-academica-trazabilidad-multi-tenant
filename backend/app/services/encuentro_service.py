import uuid
from datetime import date, timedelta

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.asignacion import Asignacion
from app.models.instancia_encuentro import EstadoInstancia, InstanciaEncuentro
from app.models.slot_encuentro import DiaSemana, SlotEncuentro
from app.repositories.encuentro_repository import (
    InstanciaEncuentroRepository,
    SlotEncuentroRepository,
)
from app.schemas.auth import UserContext
from app.schemas.encuentros import (
    InstanciaEncuentroCreate,
    InstanciaEncuentroResponse,
    InstanciaEncuentroUpdate,
    SlotEncuentroCreate,
    SlotEncuentroResponse,
)

DIAS_MAP = {
    'Lunes': 0, 'Martes': 1, 'Miercoles': 2, 'Jueves': 3,
    'Viernes': 4, 'Sabado': 5, 'Domingo': 6,
}


def _validate_dia_semana(valor: str) -> DiaSemana:
    for d in DiaSemana:
        if d.value == valor:
            return d
    raise HTTPException(status_code=422, detail=f'Dia de semana invalido: {valor}')


def _validate_estado_instancia(valor: str) -> EstadoInstancia:
    for e in EstadoInstancia:
        if e.value == valor:
            return e
    raise HTTPException(status_code=422, detail=f'Estado invalido: {valor}')


def _generate_instance_dates(fecha_inicio: date, dia_semana_valor: str, cant_semanas: int) -> list[date]:
    target_weekday = DIAS_MAP.get(dia_semana_valor)
    if target_weekday is None:
        raise HTTPException(status_code=422, detail=f'Dia de semana invalido: {dia_semana_valor}')
    dates: list[date] = []
    current = fecha_inicio
    weeks_generated = 0
    while weeks_generated < cant_semanas:
        if current.weekday() == target_weekday:
            dates.append(current)
            weeks_generated += 1
            if weeks_generated >= cant_semanas:
                break
        current += timedelta(days=1)
    return dates


class SlotEncuentroService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self._session = session
        self._slot_repo = SlotEncuentroRepository(session, tenant_id)
        self._instancia_repo = InstanciaEncuentroRepository(session, tenant_id)
        self._tenant_id = tenant_id

    async def create_slot(self, data: SlotEncuentroCreate) -> SlotEncuentroResponse:
        dia = _validate_dia_semana(data.dia_semana)

        # Si no viene asignacion_id, resolver desde materia + primer usuario del tenant
        if data.asignacion_id is None:
            from app.models.asignacion import Asignacion
            from sqlalchemy import select
            result = await self._session.execute(
                select(Asignacion)
                .where(Asignacion.tenant_id == self._tenant_id)
                .where(Asignacion.materia_id == data.materia_id)
                .where(Asignacion.deleted_at.is_(None))
                .limit(1)
            )
            asig = result.scalar_one_or_none()
            if asig is None:
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=400,
                    detail='No hay asignaciones activas para esta materia. Creá una asignación primero.',
                )
            data.asignacion_id = asig.id

        slot = await self._slot_repo.create(
            asignacion_id=data.asignacion_id,
            materia_id=data.materia_id,
            titulo=data.titulo,
            hora=data.hora,
            dia_semana=dia,
            fecha_inicio=data.fecha_inicio,
            cant_semanas=data.cant_semanas,
            fecha_unica=data.fecha_unica,
            meet_url=data.meet_url,
            vig_desde=data.vig_desde,
            vig_hasta=data.vig_hasta,
        )

        if data.cant_semanas > 0 and data.fecha_unica is None:
            fechas = _generate_instance_dates(data.fecha_inicio, data.dia_semana, data.cant_semanas)
            for f in fechas:
                await self._instancia_repo.create(
                    slot_id=slot.id,
                    materia_id=data.materia_id,
                    fecha=f,
                    hora=data.hora,
                    titulo=data.titulo,
                    estado=EstadoInstancia.PROGRAMADO,
                    meet_url=data.meet_url,
                )

        return self._slot_to_response(slot)

    async def list_slots(self, materia_id: uuid.UUID | None = None) -> list[SlotEncuentroResponse]:
        if materia_id is not None:
            slots = await self._slot_repo.list_by_materia(materia_id)
        else:
            slots = await self._slot_repo.get_multi()
        return [self._slot_to_response(s) for s in slots]

    async def get_slot(self, slot_id: uuid.UUID) -> SlotEncuentroResponse:
        slot = await self._slot_repo.get(slot_id)
        if not slot:
            raise HTTPException(status_code=404, detail='Slot no encontrado')
        return self._slot_to_response(slot)

    def _slot_to_response(self, s: SlotEncuentro) -> SlotEncuentroResponse:
        return SlotEncuentroResponse(
            id=s.id,
            tenant_id=s.tenant_id,
            asignacion_id=s.asignacion_id,
            materia_id=s.materia_id,
            titulo=s.titulo,
            hora=s.hora,
            dia_semana=s.dia_semana.value if isinstance(s.dia_semana, DiaSemana) else str(s.dia_semana),
            fecha_inicio=s.fecha_inicio,
            cant_semanas=s.cant_semanas,
            fecha_unica=s.fecha_unica,
            meet_url=s.meet_url,
            vig_desde=s.vig_desde,
            vig_hasta=s.vig_hasta,
            created_at=s.created_at,
            updated_at=s.updated_at,
        )


class InstanciaEncuentroService:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self._session = session
        self._repo = InstanciaEncuentroRepository(session, tenant_id)
        self._tenant_id = tenant_id

    async def create_unique(self, data: InstanciaEncuentroCreate) -> InstanciaEncuentroResponse:
        instancia = await self._repo.create(
            materia_id=data.materia_id,
            fecha=data.fecha,
            hora=data.hora,
            titulo=data.titulo,
            estado=EstadoInstancia.PROGRAMADO,
            meet_url=data.meet_url,
        )
        return self._to_response(instancia)

    async def update(self, instancia_id: uuid.UUID, data: InstanciaEncuentroUpdate) -> InstanciaEncuentroResponse:
        instancia = await self._repo.get(instancia_id)
        if not instancia:
            raise HTTPException(status_code=404, detail='Instancia no encontrada')

        kwargs = {}
        if data.estado is not None:
            _validate_estado_instancia(data.estado)
            kwargs['estado'] = data.estado
        if data.meet_url is not None:
            kwargs['meet_url'] = data.meet_url
        if data.video_url is not None:
            kwargs['video_url'] = data.video_url
        if data.comentario is not None:
            kwargs['comentario'] = data.comentario

        if kwargs:
            instancia = await self._repo.update(instancia, **kwargs)

        return self._to_response(instancia)

    async def list_with_filters(
        self,
        materia_id: uuid.UUID | None = None,
        desde: date | None = None,
        hasta: date | None = None,
        estado: str | None = None,
        slot_id: uuid.UUID | None = None,
        current_user: UserContext | None = None,
        skip: int = 0,
        limit: int = 100,
    ):
        materia_ids = None
        if current_user and 'COORDINADOR' not in current_user.roles and 'ADMIN' not in current_user.roles:
            from sqlalchemy import select as sa_select
            from app.models.asignacion import Asignacion
            result = await self._session.execute(
                sa_select(Asignacion.materia_id)
                .where(Asignacion.usuario_id == current_user.user_id)
                .where(Asignacion.tenant_id == self._tenant_id)
                .where(Asignacion.deleted_at.is_(None))
                .where(Asignacion.materia_id.isnot(None))
            )
            materia_ids = list({row[0] for row in result.all()})
            if not materia_ids:
                return [], 0

        items, total = await self._repo.list_filtered(
            materia_id=materia_id,
            desde=desde,
            hasta=hasta,
            estado=estado,
            slot_id=slot_id,
            materia_ids=materia_ids,
            skip=skip,
            limit=limit,
        )
        return [self._to_response(i) for i in items], total

    async def generate_html(self, materia_id: uuid.UUID) -> str:
        items, _ = await self._repo.list_filtered(materia_id=materia_id)
        if not items:
            return '<p>No hay encuentros programados.</p>'

        rows = []
        for inst in items:
            estado_emoji = '✅' if inst.estado == EstadoInstancia.REALIZADO.value else '📅' if inst.estado == EstadoInstancia.PROGRAMADO.value else '❌'
            meet = f'<a href="{inst.meet_url}">Enlace</a>' if inst.meet_url else '—'
            rows.append(
                f'<tr>'
                f'<td>{inst.fecha.isoformat()}</td>'
                f'<td>{inst.hora}</td>'
                f'<td>{inst.titulo}</td>'
                f'<td>{estado_emoji} {inst.estado}</td>'
                f'<td>{meet}</td>'
                f'</tr>'
            )

        return (
            '<table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse;width:100%;font-family:sans-serif;">'
            '<thead><tr style="background:#f5f5f5;">'
            '<th>Fecha</th><th>Hora</th><th>Titulo</th><th>Estado</th><th>Enlace</th>'
            '</tr></thead><tbody>'
            f'{chr(10).join(rows)}'
            '</tbody></table>'
        )

    def _to_response(self, i: InstanciaEncuentro) -> InstanciaEncuentroResponse:
        return InstanciaEncuentroResponse(
            id=i.id,
            tenant_id=i.tenant_id,
            slot_id=i.slot_id,
            materia_id=i.materia_id,
            fecha=i.fecha,
            hora=i.hora,
            titulo=i.titulo,
            estado=i.estado.value if isinstance(i.estado, EstadoInstancia) else str(i.estado),
            meet_url=i.meet_url,
            video_url=i.video_url,
            comentario=i.comentario,
            created_at=i.created_at,
            updated_at=i.updated_at,
        )
