import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CarreraCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    codigo: str
    nombre: str
    estado: str = 'Activa'


class CarreraUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    codigo: str | None = None
    nombre: str | None = None
    estado: str | None = None


class CarreraResponse(BaseModel):
    model_config = ConfigDict(extra='forbid', from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    codigo: str
    nombre: str
    estado: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class CarreraList(BaseModel):
    model_config = ConfigDict(extra='forbid')

    items: list[CarreraResponse]
    total: int
