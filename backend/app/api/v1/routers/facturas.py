import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db, require_permission
from app.schemas.auth import UserContext
from app.services.factura_service import FacturaService

router = APIRouter(prefix='/api/v1/facturas', tags=['facturas'])


class FacturaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='forbid')

    id: uuid.UUID
    usuario_id: uuid.UUID
    periodo: str
    detalle: str
    referencia_archivo: str | None = None
    tamano_kb: float | None = None
    estado: str
    cargada_at: datetime
    abonada_at: datetime | None = None


class FacturaCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    usuario_id: uuid.UUID
    periodo: str
    detalle: str
    referencia_archivo: str | None = None
    tamano_kb: float | None = None


class CambioEstadoRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    estado: str


@router.get('', response_model=list[FacturaResponse])
async def listar_facturas(
    usuario_id: uuid.UUID | None = None,
    periodo: str | None = None,
    estado: str | None = None,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('facturas:gestionar'),
) -> list[FacturaResponse]:
    service = FacturaService(session, current_user.tenant_id)
    result = await service.listar(
        usuario_id=usuario_id, periodo=periodo, estado=estado,
    )
    return [FacturaResponse.model_validate(f) for f in result]


@router.post('', response_model=FacturaResponse, status_code=status.HTTP_201_CREATED)
async def crear_factura(
    data: FacturaCreate,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('facturas:gestionar'),
) -> FacturaResponse:
    service = FacturaService(session, current_user.tenant_id)
    result = await service.crear(
        usuario_id=data.usuario_id, periodo=data.periodo,
        detalle=data.detalle, referencia_archivo=data.referencia_archivo,
        tamano_kb=data.tamano_kb,
    )
    return FacturaResponse.model_validate(result)


@router.get('/{factura_id}', response_model=FacturaResponse)
async def detalle_factura(
    factura_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('facturas:gestionar'),
) -> FacturaResponse:
    service = FacturaService(session, current_user.tenant_id)
    result = await service.obtener(factura_id)
    if result is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail='Factura no encontrada')
    return FacturaResponse.model_validate(result)


@router.patch('/{factura_id}/estado', response_model=FacturaResponse)
async def cambiar_estado_factura(
    factura_id: uuid.UUID,
    data: CambioEstadoRequest,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('facturas:gestionar'),
) -> FacturaResponse:
    service = FacturaService(session, current_user.tenant_id)
    result = await service.cambiar_estado(factura_id, data.estado)
    return FacturaResponse.model_validate(result)
