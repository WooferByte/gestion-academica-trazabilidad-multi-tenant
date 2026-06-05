import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProgramaMateriaCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    materia_id: uuid.UUID
    carrera_id: uuid.UUID
    cohorte_id: uuid.UUID
    titulo: str
    referencia_archivo: str | None = None
    cargado_at: datetime | None = None


class ProgramaMateriaUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    titulo: str | None = None
    referencia_archivo: str | None = None
    cargado_at: datetime | None = None


class ProgramaMateriaResponse(BaseModel):
    model_config = ConfigDict(extra='forbid', from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    materia_id: uuid.UUID
    carrera_id: uuid.UUID
    cohorte_id: uuid.UUID
    titulo: str
    referencia_archivo: str | None = None
    cargado_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None


class ProgramaMateriaList(BaseModel):
    model_config = ConfigDict(extra='forbid')

    items: list[ProgramaMateriaResponse]
    total: int
