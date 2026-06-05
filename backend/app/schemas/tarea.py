import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TareaCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    materia_id: uuid.UUID | None = None
    asignado_a: uuid.UUID
    descripcion: str = Field(..., min_length=1)
    contexto_id: uuid.UUID | None = None


class TareaUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    descripcion: str | None = Field(None, min_length=1)
    asignado_a: uuid.UUID | None = None


class TareaEstadoUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    estado: str


class ComentarioCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    texto: str = Field(..., min_length=1)


class ComentarioResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    id: uuid.UUID
    tarea_id: uuid.UUID
    autor_id: uuid.UUID
    texto: str
    creado_at: datetime


class TareaResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    id: uuid.UUID
    tenant_id: uuid.UUID
    materia_id: uuid.UUID | None = None
    asignado_a: uuid.UUID
    asignado_por: uuid.UUID
    estado: str
    descripcion: str
    contexto_id: uuid.UUID | None = None
    comentarios: list[ComentarioResponse] = []
    created_at: datetime | None = None
    updated_at: datetime | None = None


class TareaListResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    items: list[TareaResponse]
    total: int
