import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db, require_permission
from app.schemas.auth import UserContext
from app.schemas.evaluaciones import (
    AlumnosImportRequest,
    EvaluacionCreate,
    EvaluacionListResponse,
    EvaluacionResponse,
    MetricasColoquiosResponse,
    ReservaCreate,
    ReservaResponse,
    ResultadoCreate,
    ResultadoResponse,
    ResultadosListResponse,
)
from app.services.audit_service import AuditService
from app.services.evaluacion_service import (
    EvaluacionService,
    ReservaService,
    ResultadoService,
)

router = APIRouter(prefix='/api/v1/coloquios', tags=['coloquios'])


def _audit(session: AsyncSession, current_user: UserContext) -> AuditService:
    return AuditService(session, current_user)


@router.post('/', response_model=EvaluacionResponse, status_code=status.HTTP_201_CREATED)
async def crear_convocatoria(
    data: EvaluacionCreate,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('coloquios:gestionar'),
) -> EvaluacionResponse:
    service = EvaluacionService(session, current_user.tenant_id)
    result = await service.create_convocatoria(data)
    audit_svc = _audit(session, current_user)
    await audit_svc.log('coloquios:crear', detalle={'materia_id': str(data.materia_id), 'instancia': data.instancia})
    return result


@router.get('/', response_model=EvaluacionListResponse)
async def listar_convocatorias(
    materia_id: uuid.UUID | None = Query(None),
    cohorte_id: uuid.UUID | None = Query(None),
    tipo: str | None = Query(None),
    estado: str | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('coloquios:reservar'),
) -> EvaluacionListResponse:
    service = EvaluacionService(session, current_user.tenant_id)
    items, total = await service.listar_convocatorias(
        materia_id=materia_id,
        cohorte_id=cohorte_id,
        tipo=tipo,
        estado=estado,
        current_user=current_user,
        skip=offset,
        limit=limit,
    )
    return EvaluacionListResponse(items=items, total=total)


@router.get('/metricas', response_model=MetricasColoquiosResponse)
async def obtener_metricas(
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('coloquios:reservar'),
) -> MetricasColoquiosResponse:
    service = EvaluacionService(session, current_user.tenant_id)
    return await service.obtener_metricas()


@router.get('/{evaluacion_id}', response_model=EvaluacionResponse)
async def obtener_convocatoria(
    evaluacion_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('coloquios:reservar'),
) -> EvaluacionResponse:
    service = EvaluacionService(session, current_user.tenant_id)
    return await service.obtener_convocatoria(evaluacion_id)


@router.post('/{evaluacion_id}/alumnos', status_code=status.HTTP_204_NO_CONTENT)
async def importar_alumnos(
    evaluacion_id: uuid.UUID,
    data: AlumnosImportRequest,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('coloquios:gestionar'),
) -> None:
    service = EvaluacionService(session, current_user.tenant_id)
    await service.importar_alumnos(evaluacion_id, data)
    audit_svc = _audit(session, current_user)
    await audit_svc.log('coloquios:importar_alumnos', detalle={'evaluacion_id': str(evaluacion_id), 'cantidad': len(data.alumno_ids)})


@router.post('/{evaluacion_id}/reservas', response_model=ReservaResponse, status_code=status.HTTP_201_CREATED)
async def reservar_turno(
    evaluacion_id: uuid.UUID,
    data: ReservaCreate,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('coloquios:reservar'),
) -> ReservaResponse:
    service = ReservaService(session, current_user.tenant_id)
    result = await service.reservar(evaluacion_id, data, current_user.user_id)
    audit_svc = _audit(session, current_user)
    await audit_svc.log('coloquios:reservar', detalle={'turno_id': str(data.turno_id), 'evaluacion_id': str(evaluacion_id)})
    return result


@router.delete('/reservas/{reserva_id}', response_model=dict)
async def cancelar_reserva(
    reserva_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('coloquios:reservar'),
) -> dict:
    service = ReservaService(session, current_user.tenant_id)
    result = await service.cancelar(reserva_id, current_user)
    audit_svc = _audit(session, current_user)
    await audit_svc.log('coloquios:cancelar_reserva', detalle={'reserva_id': str(reserva_id)})
    return {'id': str(result.id), 'estado': result.estado, 'mensaje': 'Reserva cancelada exitosamente'}


@router.put('/{evaluacion_id}/resultados/{alumno_id}', response_model=ResultadoResponse)
async def registrar_resultado(
    evaluacion_id: uuid.UUID,
    alumno_id: uuid.UUID,
    data: ResultadoCreate,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('coloquios:gestionar'),
) -> ResultadoResponse:
    service = ResultadoService(session, current_user.tenant_id)
    result = await service.registrar(evaluacion_id, alumno_id, data)
    audit_svc = _audit(session, current_user)
    await audit_svc.log('coloquios:registrar_resultado', detalle={'evaluacion_id': str(evaluacion_id), 'alumno_id': str(alumno_id)})
    return result


@router.get('/{evaluacion_id}/resultados', response_model=ResultadosListResponse)
async def listar_resultados(
    evaluacion_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('coloquios:gestionar'),
) -> ResultadosListResponse:
    service = ResultadoService(session, current_user.tenant_id)
    return await service.listar(evaluacion_id)


@router.patch('/{evaluacion_id}/cerrar', response_model=EvaluacionResponse)
async def cerrar_convocatoria(
    evaluacion_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('coloquios:gestionar'),
) -> EvaluacionResponse:
    service = EvaluacionService(session, current_user.tenant_id)
    result = await service.cerrar_convocatoria(evaluacion_id)
    audit_svc = _audit(session, current_user)
    await audit_svc.log('coloquios:cerrar', detalle={'evaluacion_id': str(evaluacion_id)})
    return result
