import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MateriaCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    codigo: str
    nombre: str
    estado: str = 'Activa'


class MateriaUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    codigo: str | None = None
    nombre: str | None = None
    estado: str | None = None


class MateriaResponse(BaseModel):
    model_config = ConfigDict(extra='forbid', from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    codigo: str
    nombre: str
    estado: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class MateriaList(BaseModel):
    model_config = ConfigDict(extra='forbid')

    items: list[MateriaResponse]
    total: int
