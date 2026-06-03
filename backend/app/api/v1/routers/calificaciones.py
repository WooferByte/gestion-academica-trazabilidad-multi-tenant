import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from fastapi import Form as FastAPIForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit_dependency import get_audit_service
from app.core.dependencies import get_current_user, get_db, require_permission
from app.schemas.auth import UserContext
from app.schemas.calificaciones import (
    CalificacionConfirmRequest,
    CalificacionConfirmResponse,
    CalificacionListResponse,
    CalificacionPreviewResponse,
    CalificacionResponse,
    ReporteFinalizacionPreviewResponse,
)
from app.services.audit_service import AuditService
from app.services.calificaciones_service import CalificacionesService

router = APIRouter(prefix='/api/v1/calificaciones', tags=['calificaciones'])


@router.post('/importar/preview', response_model=CalificacionPreviewResponse)
async def preview_import(
    materia_id: uuid.UUID = FastAPIForm(...),
    cohorte_id: uuid.UUID = FastAPIForm(...),
    archivo: UploadFile = File(...),
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('calificaciones:importar'),
):
    service = CalificacionesService(session, current_user.tenant_id)
    return await service.preview_import(materia_id, cohorte_id, archivo)


@router.post('/importar/confirmar', response_model=CalificacionConfirmResponse, status_code=status.HTTP_201_CREATED)
async def confirm_import(
    request: Request,
    materia_id: uuid.UUID = FastAPIForm(...),
    cohorte_id: uuid.UUID = FastAPIForm(...),
    actividades: str = FastAPIForm(...),
    archivo: UploadFile = File(...),
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('calificaciones:importar'),
    audit: AuditService = Depends(get_audit_service),
):
    import json
    from app.schemas.calificaciones import ActividadAImportar

    try:
        actividades_data = json.loads(actividades)
        actividades_list = [ActividadAImportar(**a) for a in actividades_data]
    except (json.JSONDecodeError, Exception) as e:
        raise HTTPException(status_code=400, detail=f'Formato de actividades inválido: {e}')

    confirm_request = CalificacionConfirmRequest(
        materia_id=materia_id,
        cohorte_id=cohorte_id,
        actividades=actividades_list,
    )

    service = CalificacionesService(session, current_user.tenant_id)
    return await service.confirm_import(confirm_request, archivo, current_user, audit)


@router.post('/importar/finalizacion', response_model=ReporteFinalizacionPreviewResponse)
async def import_reporte_finalizacion(
    materia_id: uuid.UUID = FastAPIForm(...),
    cohorte_id: uuid.UUID = FastAPIForm(...),
    archivo: UploadFile = File(...),
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('calificaciones:importar'),
):
    service = CalificacionesService(session, current_user.tenant_id)
    return await service.import_reporte_finalizacion(materia_id, cohorte_id, archivo)


@router.get('', response_model=CalificacionListResponse)
async def list_calificaciones(
    materia_id: uuid.UUID,
    cohorte_id: uuid.UUID | None = None,
    entrada_padron_id: uuid.UUID | None = None,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('calificaciones:importar'),
):
    service = CalificacionesService(session, current_user.tenant_id)
    umbral_pct, valores_aprobatorios = await service.get_umbral(materia_id, cohorte_id)
    items = await service.list_calificaciones(
        materia_id, cohorte_id, entrada_padron_id,
        umbral_pct=umbral_pct,
        valores_aprobatorios=valores_aprobatorios,
    )
    return CalificacionListResponse(items=items, total=len(items))
