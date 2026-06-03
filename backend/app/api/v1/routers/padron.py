import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit_dependency import get_audit_service
from app.core.dependencies import get_current_user, get_db, require_permission
from app.integrations.moodle_ws import MoodleWSClient, MoodleWSException
from app.repositories.padron_repository import VersionPadronRepository
from app.schemas.auth import UserContext
from app.schemas.padron import (
    ImportPreviewResponse,
    PadronVaciarResponse,
    VersionPadronResponse,
)
from app.services.audit_service import AuditService
from app.services.padron_service import PadronService

router = APIRouter(prefix='/api/v1/padron', tags=['padron'])


@router.post('/importar/preview', response_model=ImportPreviewResponse)
async def preview_import(
    materia_id: uuid.UUID = Form(...),
    cohorte_id: uuid.UUID = Form(...),
    archivo: UploadFile = File(...),
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('padron:cargar'),
):
    service = PadronService(session, current_user.tenant_id)
    return await service.preview_import(materia_id, cohorte_id, archivo)


@router.post('/importar/confirmar', response_model=VersionPadronResponse, status_code=status.HTTP_201_CREATED)
async def confirm_import(
    request: Request,
    materia_id: uuid.UUID = Form(...),
    cohorte_id: uuid.UUID = Form(...),
    archivo: UploadFile = File(...),
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('padron:cargar'),
    audit: AuditService = Depends(get_audit_service),
):
    service = PadronService(session, current_user.tenant_id)
    preview = await service.preview_import(materia_id, cohorte_id, archivo)
    return await service.confirm_import(
        materia_id, cohorte_id, preview.items, current_user, audit,
    )


@router.post('/vaciar/{materia_id}/{cohorte_id}', response_model=PadronVaciarResponse)
async def vaciar_materia(
    materia_id: uuid.UUID,
    cohorte_id: uuid.UUID,
    request: Request,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('padron:cargar'),
    audit: AuditService = Depends(get_audit_service),
):
    service = PadronService(session, current_user.tenant_id)
    return await service.vaciar_materia(materia_id, current_user, audit)


@router.get('/versiones', response_model=list[VersionPadronResponse])
async def list_versiones(
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('padron:cargar'),
):
    service = PadronService(session, current_user.tenant_id)
    return await service.list_versiones()


@router.post('/sync-moodle', response_model=VersionPadronResponse, status_code=status.HTTP_201_CREATED)
async def sync_moodle(
    request: Request,
    materia_id: uuid.UUID = Form(...),
    cohorte_id: uuid.UUID = Form(...),
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('padron:cargar'),
    audit: AuditService = Depends(get_audit_service),
):
    client = MoodleWSClient(
        url='https://moodle.example.com',
        token='mock-token',
    )
    try:
        usuarios_mock = await client.sync_usuarios(materia_id)
    except MoodleWSException:
        raise HTTPException(
            status_code=502,
            detail='Error de integración con Moodle',
        )

    from app.schemas.padron import ImportPreviewItem
    items = [
        ImportPreviewItem(
            nombre=u['nombre'],
            apellidos=u['apellidos'],
            email=u['email'],
            comision=u['comision'],
            regional=u['regional'],
        )
        for u in usuarios_mock
    ]

    service = PadronService(session, current_user.tenant_id)
    return await service.confirm_import(materia_id, cohorte_id, items, current_user, audit)
