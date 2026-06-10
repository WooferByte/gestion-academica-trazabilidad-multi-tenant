import uuid
from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db, require_permission
from app.schemas.analisis import ReporteRapido
from app.schemas.auth import UserContext

router = APIRouter(prefix='/api/v1/analisis', tags=['analisis'])


@router.get('/atrasados')
async def atrasados(
    materia_id: uuid.UUID = Query(...),
    cohorte_id: uuid.UUID = Query(...),
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('atrasados:ver'),
) -> dict:
    from app.services.analisis_service import AnalisisService
    service = AnalisisService(session, current_user.tenant_id)
    result = await service.calcular_atrasados(materia_id, cohorte_id)
    return {'items': result, 'total': len(result)}


@router.get('/ranking')
async def ranking(
    materia_id: uuid.UUID = Query(...),
    cohorte_id: uuid.UUID = Query(...),
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('atrasados:ver'),
) -> dict:
    from app.services.analisis_service import AnalisisService
    service = AnalisisService(session, current_user.tenant_id)
    result = await service.calcular_ranking(materia_id, cohorte_id)
    return {'items': result, 'total': len(result)}


@router.get('/reportes-rapidos', response_model=ReporteRapido)
async def reportes_rapidos(
    materia_id: uuid.UUID = Query(...),
    cohorte_id: uuid.UUID = Query(...),
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('atrasados:ver'),
) -> ReporteRapido:
    from app.services.analisis_service import AnalisisService
    service = AnalisisService(session, current_user.tenant_id)
    return await service.calcular_reporte_rapido(materia_id, cohorte_id)


@router.get('/actividades')
async def list_actividades(
    materia_id: uuid.UUID = Query(...),
    cohorte_id: uuid.UUID = Query(...),
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('atrasados:ver'),
) -> dict:
    from app.services.analisis_service import AnalisisService
    service = AnalisisService(session, current_user.tenant_id)
    actividades = await service.listar_actividades(materia_id, cohorte_id)
    return {'items': actividades, 'total': len(actividades)}


@router.get('/notas-finales')
async def notas_finales(
    materia_id: uuid.UUID = Query(...),
    cohorte_id: uuid.UUID = Query(...),
    actividades: str = Query(..., description='Comma-separated activity names'),
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('atrasados:ver'),
) -> dict:
    from app.services.analisis_service import AnalisisService
    service = AnalisisService(session, current_user.tenant_id)
    act_list = [a.strip() for a in actividades.split(',') if a.strip()]
    if not act_list:
        raise HTTPException(status_code=400, detail='Debe especificar al menos una actividad')
    result = await service.calcular_notas_finales(materia_id, cohorte_id, act_list)
    return {'items': result, 'total': len(result)}


@router.get('/tps-sin-corregir', response_model=None)
async def tps_sin_corregir(
    materia_id: uuid.UUID = Query(...),
    cohorte_id: uuid.UUID = Query(...),
    format: str = Query('json', pattern='^(json|csv)$'),
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('atrasados:ver'),
) -> PlainTextResponse | dict:
    from app.services.analisis_service import AnalisisService
    service = AnalisisService(session, current_user.tenant_id)
    result = await service.exportar_tps_sin_corregir(materia_id, cohorte_id)

    if format == 'csv':
        headers = ['alumno_nombre', 'alumno_apellidos', 'actividad', 'comision']
        rows = [[e.alumno_nombre, e.alumno_apellidos, e.actividad, e.comision] for e in result]
        csv_content = service.to_csv(headers, rows)
        return PlainTextResponse(
            content=csv_content,
            media_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="tps-sin-corregir.csv"'},
        )

    return {'items': result, 'total': len(result)}


@router.get('/monitor-general', response_model=None)
async def monitor_general(
    materia_id: uuid.UUID | None = Query(default=None),
    comision: str | None = Query(default=None),
    regional: str | None = Query(default=None),
    busqueda: str | None = Query(default=None, description='Buscar por nombre o apellido'),
    format: str = Query('json', pattern='^(json|csv)$'),
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('atrasados:ver'),
) -> PlainTextResponse | dict:
    from app.services.analisis_service import AnalisisService
    service = AnalisisService(session, current_user.tenant_id)
    result = await service.monitor_general(
        materia_id=materia_id,
        comision=comision,
        regional=regional,
        busqueda=busqueda,
    )

    if format == 'csv':
        headers = ['nombre', 'apellidos', 'comision', 'regional', 'materia_id', 'actividad', 'nota_numerica', 'nota_textual']
        rows = [[e.nombre, e.apellidos, e.comision, e.regional, str(e.materia_id), e.actividad, e.nota_numerica or '', e.nota_textual or ''] for e in result]
        csv_content = service.to_csv(headers, rows)
        return PlainTextResponse(
            content=csv_content,
            media_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="monitor-general.csv"'},
        )

    return {'items': result, 'total': len(result)}


@router.get('/monitor-seguimiento')
async def monitor_seguimiento(
    materia_id: uuid.UUID | None = Query(default=None),
    comision: str | None = Query(default=None),
    desde: date | None = Query(default=None),
    hasta: date | None = Query(default=None),
    min_actividades: int | None = Query(default=None, ge=1),
    busqueda: str | None = Query(default=None, description='Buscar por nombre o apellido'),
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('atrasados:ver'),
) -> dict:
    from app.services.analisis_service import AnalisisService
    service = AnalisisService(session, current_user.tenant_id)

    desde_dt: datetime | None = None
    hasta_dt: datetime | None = None
    if desde is not None:
        desde_dt = datetime.combine(desde, datetime.min.time(), tzinfo=timezone.utc)
    if hasta is not None:
        hasta_dt = datetime.combine(hasta, datetime.max.time(), tzinfo=timezone.utc)

    result = await service.monitor_seguimiento(
        usuario_id=current_user.user_id,
        materia_id=materia_id,
        comision=comision,
        desde=desde_dt,
        hasta=hasta_dt,
        min_actividades=min_actividades,
        busqueda=busqueda,
    )
    return {'items': result, 'total': len(result)}
