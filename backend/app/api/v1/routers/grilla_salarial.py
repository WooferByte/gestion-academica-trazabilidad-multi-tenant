import uuid
from datetime import date

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db, require_permission
from app.schemas.auth import UserContext
from app.services.grilla_salarial_service import GrillaSalarialService

router = APIRouter(prefix='/api/v1/grilla-salarial', tags=['grilla-salarial'])


class SalarioBaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='forbid')

    id: uuid.UUID
    rol: str
    monto: float
    desde: date
    hasta: date | None = None


class SalarioBaseCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    rol: str
    monto: float
    desde: date


class SalarioPlusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='forbid')

    id: uuid.UUID
    grupo: str
    rol: str
    descripcion: str | None = None
    monto: float
    desde: date
    hasta: date | None = None


class SalarioPlusCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    grupo: str
    rol: str
    monto: float
    desde: date
    descripcion: str | None = None


@router.get('/bases', response_model=list[SalarioBaseResponse])
async def listar_bases(
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('liquidaciones:configurar-salarios'),
) -> list[SalarioBaseResponse]:
    service = GrillaSalarialService(session, current_user.tenant_id)
    bases = await service.listar_bases()
    return [SalarioBaseResponse.model_validate(b) for b in bases]


@router.post('/bases', response_model=SalarioBaseResponse, status_code=status.HTTP_201_CREATED)
async def crear_base(
    data: SalarioBaseCreate,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('liquidaciones:configurar-salarios'),
) -> SalarioBaseResponse:
    service = GrillaSalarialService(session, current_user.tenant_id)
    result = await service.crear_base(rol=data.rol, monto=data.monto, desde=data.desde)
    return SalarioBaseResponse.model_validate(result)


@router.get('/pluses', response_model=list[SalarioPlusResponse])
async def listar_pluses(
    grupo: str | None = None,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('liquidaciones:configurar-salarios'),
) -> list[SalarioPlusResponse]:
    service = GrillaSalarialService(session, current_user.tenant_id)
    pluses = await service.listar_pluses(grupo=grupo)
    return [SalarioPlusResponse.model_validate(p) for p in pluses]


@router.post('/pluses', response_model=SalarioPlusResponse, status_code=status.HTTP_201_CREATED)
async def crear_plus(
    data: SalarioPlusCreate,
    session: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
    _=require_permission('liquidaciones:configurar-salarios'),
) -> SalarioPlusResponse:
    service = GrillaSalarialService(session, current_user.tenant_id)
    result = await service.crear_plus(
        grupo=data.grupo, rol=data.rol, monto=data.monto,
        desde=data.desde, descripcion=data.descripcion,
    )
    return SalarioPlusResponse.model_validate(result)
