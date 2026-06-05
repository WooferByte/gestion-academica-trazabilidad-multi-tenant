import uuid

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db, require_permission
from app.schemas.auth import UserContext
from app.schemas.guardias import (
    GuardiaCreate,
    GuardiaListResponse,
    GuardiaResponse,
    GuardiaUpdate,
)
from app.services.guardia_service import GuardiaService

router = APIRouter(prefix='/api/v1/guardias', tags=['guardias'])


def _get_service(session: AsyncSession, current_user: UserContext) -> GuardiaService:
    return GuardiaService(session, current_user.tenant_id)


@router.post('', response_model=GuardiaResponse, status_code=status.HTTP_201_CREATED)
async def registrar_guardia(
    data: GuardiaCreate,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('encuentros:gestionar'),
) -> GuardiaResponse:
    service = _get_service(session, current_user)
    return await service.create(data)


@router.get('', response_model=GuardiaListResponse)
async def listar_guardias(
    materia_id: uuid.UUID | None = Query(None),
    carrera_id: uuid.UUID | None = Query(None),
    cohorte_id: uuid.UUID | None = Query(None),
    estado: str | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('encuentros:gestionar'),
) -> GuardiaListResponse:
    service = _get_service(session, current_user)
    items, total = await service.list_with_filters(
        materia_id=materia_id,
        carrera_id=carrera_id,
        cohorte_id=cohorte_id,
        estado=estado,
        current_user=current_user,
        skip=offset,
        limit=limit,
    )
    return GuardiaListResponse(items=items, total=total)


@router.patch('/{guardia_id}', response_model=GuardiaResponse)
async def actualizar_guardia(
    guardia_id: uuid.UUID,
    data: GuardiaUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('encuentros:gestionar'),
) -> GuardiaResponse:
    service = _get_service(session, current_user)
    return await service.update_state(guardia_id, data)


@router.get('/export')
async def exportar_guardias(
    materia_id: uuid.UUID | None = Query(None),
    carrera_id: uuid.UUID | None = Query(None),
    cohorte_id: uuid.UUID | None = Query(None),
    estado: str | None = Query(None),
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('encuentros:gestionar'),
) -> PlainTextResponse:
    service = _get_service(session, current_user)
    csv_content = await service.export_csv(
        materia_id=materia_id,
        carrera_id=carrera_id,
        cohorte_id=cohorte_id,
        estado=estado,
    )
    return PlainTextResponse(
        content=csv_content,
        media_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename=guardias.csv'},
    )
