import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db, require_permission
from app.schemas.auth import UserContext
from app.schemas.encuentros import (
    InstanciaEncuentroCreate,
    InstanciaEncuentroListResponse,
    InstanciaEncuentroResponse,
    InstanciaEncuentroUpdate,
    SlotEncuentroCreate,
    SlotEncuentroListResponse,
    SlotEncuentroResponse,
)
from app.services.encuentro_service import (
    InstanciaEncuentroService,
    SlotEncuentroService,
)

router = APIRouter(prefix='/api/v1/encuentros', tags=['encuentros'])


def _get_slot_service(session: AsyncSession, current_user: UserContext) -> SlotEncuentroService:
    return SlotEncuentroService(session, current_user.tenant_id)


def _get_instancia_service(session: AsyncSession, current_user: UserContext) -> InstanciaEncuentroService:
    return InstanciaEncuentroService(session, current_user.tenant_id)


@router.post('/slots', response_model=SlotEncuentroResponse, status_code=status.HTTP_201_CREATED)
async def crear_slot(
    data: SlotEncuentroCreate,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('encuentros:gestionar'),
):
    service = _get_slot_service(session, current_user)
    return await service.create_slot(data)


@router.get('/slots', response_model=SlotEncuentroListResponse)
async def listar_slots(
    materia_id: uuid.UUID | None = Query(None),
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('encuentros:gestionar'),
):
    service = _get_slot_service(session, current_user)
    items = await service.list_slots(materia_id)
    return SlotEncuentroListResponse(items=items, total=len(items))


@router.get('/slots/{slot_id}', response_model=SlotEncuentroResponse)
async def obtener_slot(
    slot_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('encuentros:gestionar'),
):
    service = _get_slot_service(session, current_user)
    return await service.get_slot(slot_id)


@router.post('/instancias', response_model=InstanciaEncuentroResponse, status_code=status.HTTP_201_CREATED)
async def crear_instancia(
    data: InstanciaEncuentroCreate,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('encuentros:gestionar'),
):
    service = _get_instancia_service(session, current_user)
    return await service.create_unique(data)


@router.get('/instancias', response_model=InstanciaEncuentroListResponse)
async def listar_instancias(
    materia_id: uuid.UUID | None = Query(None),
    desde: date | None = Query(None),
    hasta: date | None = Query(None),
    estado: str | None = Query(None),
    slot_id: uuid.UUID | None = Query(None),
    html: bool = Query(False),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('encuentros:gestionar'),
):
    service = _get_instancia_service(session, current_user)
    if html and materia_id is not None:
        html_content = await service.generate_html(materia_id)
        from fastapi.responses import HTMLResponse
        return HTMLResponse(content=html_content, media_type='text/html')

    items, total = await service.list_with_filters(
        materia_id=materia_id,
        desde=desde,
        hasta=hasta,
        estado=estado,
        slot_id=slot_id,
        current_user=current_user,
        skip=offset,
        limit=limit,
    )
    return InstanciaEncuentroListResponse(items=items, total=total)


@router.patch('/instancias/{instancia_id}', response_model=InstanciaEncuentroResponse)
async def editar_instancia(
    instancia_id: uuid.UUID,
    data: InstanciaEncuentroUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('encuentros:gestionar'),
):
    service = _get_instancia_service(session, current_user)
    return await service.update(instancia_id, data)
