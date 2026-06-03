import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AsignacionCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    usuario_id: uuid.UUID
    rol: str
    materia_id: uuid.UUID | None = None
    carrera_id: uuid.UUID | None = None
    cohorte_id: uuid.UUID | None = None
    comisiones: list[str] | None = None
    responsable_id: uuid.UUID | None = None
    desde: datetime | None = None
    hasta: datetime | None = None


class AsignacionUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    rol: str | None = None
    materia_id: uuid.UUID | None = None
    carrera_id: uuid.UUID | None = None
    cohorte_id: uuid.UUID | None = None
    comisiones: list[str] | None = None
    responsable_id: uuid.UUID | None = None
    desde: datetime | None = None
    hasta: datetime | None = None


class AsignacionResponse(BaseModel):
    model_config = ConfigDict(extra='forbid', from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    usuario_id: uuid.UUID
    rol: str
    materia_id: uuid.UUID | None = None
    carrera_id: uuid.UUID | None = None
    cohorte_id: uuid.UUID | None = None
    comisiones: list[str] | None = None
    responsable_id: uuid.UUID | None = None
    desde: datetime | None = None
    hasta: datetime | None = None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class AsignacionListResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    items: list[AsignacionResponse]
    total: int