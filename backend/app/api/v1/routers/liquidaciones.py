import uuid

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit_dependency import get_audit_service
from app.core.dependencies import get_current_user, get_db, require_permission
from app.schemas.auth import UserContext
from app.services.audit_service import AuditService
from app.services.liquidacion_service import LiquidacionService

router = APIRouter(prefix='/api/v1/liquidaciones', tags=['liquidaciones'])


class LiquidacionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='forbid')

    id: uuid.UUID
    usuario_id: uuid.UUID
    cohorte_id: uuid.UUID
    periodo: str
    rol: str
    monto_base: float
    monto_plus: float
    total: float
    es_nexo: bool
    excluido_por_factura: bool
    estado: str


class CalcularRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    cohorte_id: uuid.UUID
    periodo: str


class CerrarResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    cerradas: int
    periodo: str


@router.get('', response_model=list[LiquidacionResponse])
async def listar_liquidaciones(
    cohorte_id: uuid.UUID | None = None,
    periodo: str | None = None,
    usuario_id: uuid.UUID | None = None,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('liquidaciones:ver'),
) -> list[LiquidacionResponse]:
    service = LiquidacionService(session, current_user.tenant_id)
    result = await service.listar(
        cohorte_id=cohorte_id, periodo=periodo, usuario_id=usuario_id,
    )
    return [LiquidacionResponse.model_validate(l) for l in result]


@router.post('/calcular', response_model=list[LiquidacionResponse], status_code=status.HTTP_200_OK)
async def calcular_liquidacion(
    data: CalcularRequest,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('liquidaciones:calcular'),
) -> list[LiquidacionResponse]:
    service = LiquidacionService(session, current_user.tenant_id)
    result = await service.calcular(cohorte_id=data.cohorte_id, periodo=data.periodo)
    return [LiquidacionResponse.model_validate(l) for l in result]


@router.post('/cerrar/{cohorte_id}/{periodo}', response_model=CerrarResponse)
async def cerrar_liquidacion(
    cohorte_id: uuid.UUID,
    periodo: str,
    request: Request,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('liquidaciones:cerrar'),
    audit: AuditService = Depends(get_audit_service),
) -> CerrarResponse:
    service = LiquidacionService(session, current_user.tenant_id)
    result = await service.cerrar(
        cohorte_id=cohorte_id, periodo=periodo,
        current_user=current_user, audit=audit,
    )
    return CerrarResponse(**result)


@router.get('/historial', response_model=list[LiquidacionResponse])
async def historial_liquidaciones(
    cohorte_id: uuid.UUID | None = None,
    periodo: str | None = None,
    usuario_id: uuid.UUID | None = None,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('liquidaciones:ver'),
) -> list[LiquidacionResponse]:
    service = LiquidacionService(session, current_user.tenant_id)
    result = await service.historial(
        cohorte_id=cohorte_id, periodo=periodo, usuario_id=usuario_id,
    )
    return [LiquidacionResponse.model_validate(l) for l in result]


@router.get('/exportar')
async def exportar_liquidaciones(
    cohorte_id: uuid.UUID,
    periodo: str,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('liquidaciones:exportar'),
) -> StreamingResponse:
    service = LiquidacionService(session, current_user.tenant_id)
    csv_content = await service.exportar_csv(cohorte_id=cohorte_id, periodo=periodo)
    return StreamingResponse(
        iter([csv_content]),
        media_type='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename=liquidaciones-{periodo}.csv',
        },
    )
