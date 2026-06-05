import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db, require_permission
from app.schemas.auth import UserContext
from app.schemas.fecha_academica import (
    FechaAcademicaCreate,
    FechaAcademicaResponse,
    FechaAcademicaUpdate,
)
from app.services.fecha_academica_service import FechaAcademicaService

router = APIRouter(prefix='/api/v1/admin/fechas-academicas', tags=['fechas-academicas'])


@router.get('', response_model=dict)
async def list_fechas_academicas(
    materia_id: uuid.UUID | None = Query(None),
    cohorte_id: uuid.UUID | None = Query(None),
    tipo: str | None = Query(None),
    periodo: str | None = Query(None),
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('estructura:gestionar'),
) -> dict:
    service = FechaAcademicaService(session, current_user.tenant_id)
    return await service.list_fechas(
        materia_id=materia_id,
        cohorte_id=cohorte_id,
        tipo=tipo,
        periodo=periodo,
    )


@router.post('', response_model=FechaAcademicaResponse, status_code=status.HTTP_201_CREATED)
async def create_fecha_academica(
    data: FechaAcademicaCreate,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('estructura:gestionar'),
) -> FechaAcademicaResponse:
    service = FechaAcademicaService(session, current_user.tenant_id)
    return await service.create_fecha(data)


@router.get('/{fecha_id}', response_model=FechaAcademicaResponse)
async def get_fecha_academica(
    fecha_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('estructura:gestionar'),
) -> FechaAcademicaResponse:
    service = FechaAcademicaService(session, current_user.tenant_id)
    return await service.get_fecha(fecha_id)


@router.put('/{fecha_id}', response_model=FechaAcademicaResponse)
async def update_fecha_academica(
    fecha_id: uuid.UUID,
    data: FechaAcademicaUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('estructura:gestionar'),
) -> FechaAcademicaResponse:
    service = FechaAcademicaService(session, current_user.tenant_id)
    return await service.update_fecha(fecha_id, data)


@router.delete('/{fecha_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_fecha_academica(
    fecha_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('estructura:gestionar'),
) -> None:
    service = FechaAcademicaService(session, current_user.tenant_id)
    await service.delete_fecha(fecha_id)
