import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CategoriaPlusCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    codigo: str
    nombre: str
    activo: bool = True


class CategoriaPlusUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    codigo: str | None = None
    nombre: str | None = None
    activo: bool | None = None


class CategoriaPlusResponse(BaseModel):
    model_config = ConfigDict(extra='forbid', from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    codigo: str
    nombre: str
    activo: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class AsignacionMasivaRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    categoria_plus_id: uuid.UUID
    materia_ids: list[uuid.UUID]


class AsignarCategoriaRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')

    categoria_plus_id: uuid.UUID
