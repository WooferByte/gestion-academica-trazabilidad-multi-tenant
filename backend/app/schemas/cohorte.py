import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class CohorteCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    carrera_id: uuid.UUID
    nombre: str
    anio: int
    vig_desde: date
    vig_hasta: date | None = None
    estado: str = 'Activa'


class CohorteUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    nombre: str | None = None
    anio: int | None = None
    vig_desde: date | None = None
    vig_hasta: date | None = None
    estado: str | None = None


class CohorteResponse(BaseModel):
    model_config = ConfigDict(extra='forbid', from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    carrera_id: uuid.UUID
    nombre: str
    anio: int
    vig_desde: date
    vig_hasta: date | None = None
    estado: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class CohorteList(BaseModel):
    model_config = ConfigDict(extra='forbid')

    items: list[CohorteResponse]
    total: int
