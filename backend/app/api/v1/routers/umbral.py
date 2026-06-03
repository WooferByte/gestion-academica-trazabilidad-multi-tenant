import uuid

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit_dependency import get_audit_service
from app.core.dependencies import get_current_user, get_db, require_permission
from app.schemas.auth import UserContext
from app.schemas.umbral import UmbralMateriaResponse, UmbralMateriaUpdate
from app.services.audit_service import AuditService
from app.services.umbral_service import UmbralService

router = APIRouter(prefix='/api/v1/umbrales', tags=['umbrales'])


@router.get('/{materia_id}/{cohorte_id}', response_model=UmbralMateriaResponse)
async def get_umbral(
    materia_id: uuid.UUID,
    cohorte_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('calificaciones:importar'),
):
    service = UmbralService(session, current_user.tenant_id)
    return await service.obtener_umbral(materia_id, cohorte_id)


@router.put('/{materia_id}/{cohorte_id}', response_model=UmbralMateriaResponse)
async def update_umbral(
    materia_id: uuid.UUID,
    cohorte_id: uuid.UUID,
    data: UmbralMateriaUpdate,
    request: Request,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('calificaciones:importar'),
    audit: AuditService = Depends(get_audit_service),
):
    service = UmbralService(session, current_user.tenant_id)
    return await service.configurar_umbral(materia_id, cohorte_id, data, current_user, audit)
