import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class GuardiaCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    asignacion_id: uuid.UUID
    materia_id: uuid.UUID
    carrera_id: uuid.UUID | None = None
    cohorte_id: uuid.UUID | None = None
    dia: str
    horario: str = Field(..., min_length=1, max_length=20)
    comentarios: str | None = None


class GuardiaUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    estado: str
    comentarios: str | None = None


class GuardiaResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    id: uuid.UUID
    tenant_id: uuid.UUID
    asignacion_id: uuid.UUID
    materia_id: uuid.UUID
    carrera_id: uuid.UUID | None = None
    cohorte_id: uuid.UUID | None = None
    dia: str
    horario: str
    estado: str
    comentarios: str | None = None
    creada_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class GuardiaListResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    items: list[GuardiaResponse]
    total: int
