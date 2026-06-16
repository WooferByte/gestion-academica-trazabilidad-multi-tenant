import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class SlotEncuentroCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    asignacion_id: uuid.UUID | None = None
    materia_id: uuid.UUID
    titulo: str = Field(..., min_length=1, max_length=255)
    hora: str = Field(..., pattern=r'^\d{2}:\d{2}$')
    dia_semana: str
    fecha_inicio: date
    cant_semanas: int = Field(default=0, ge=0)
    fecha_unica: date | None = None
    meet_url: str | None = None
    vig_desde: date | None = None
    vig_hasta: date | None = None


class SlotEncuentroResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    id: uuid.UUID
    tenant_id: uuid.UUID
    asignacion_id: uuid.UUID
    materia_id: uuid.UUID
    titulo: str
    hora: str
    dia_semana: str
    fecha_inicio: date
    cant_semanas: int
    fecha_unica: date | None = None
    meet_url: str | None = None
    vig_desde: date | None = None
    vig_hasta: date | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class InstanciaEncuentroCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    materia_id: uuid.UUID
    fecha: date
    hora: str = Field(..., pattern=r'^\d{2}:\d{2}$')
    titulo: str = Field(..., min_length=1, max_length=255)
    meet_url: str | None = None


class InstanciaEncuentroUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    estado: str | None = None
    meet_url: str | None = None
    video_url: str | None = None
    comentario: str | None = None


class InstanciaEncuentroResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    id: uuid.UUID
    tenant_id: uuid.UUID
    slot_id: uuid.UUID | None = None
    materia_id: uuid.UUID
    fecha: date
    hora: str
    titulo: str
    estado: str
    meet_url: str | None = None
    video_url: str | None = None
    comentario: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class InstanciaEncuentroListResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    items: list[InstanciaEncuentroResponse]
    total: int


class SlotEncuentroListResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')

    items: list[SlotEncuentroResponse]
    total: int
